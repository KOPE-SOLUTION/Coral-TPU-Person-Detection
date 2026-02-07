#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L9 — Stream + Events Recording (Flask)

Endpoints:
  /         - live view
  /video    - MJPEG stream
  /status   - JSON status
  /snapshot - save snapshot now (redirect to saved image)
  /events   - list recent saved images
  /out/<file> - serve images from outdir

Usage:
  python3 stream_people_tpu_events.py <model_edgetpu.tflite> <cam_index> [score_thresh] [width] [height] [port] [outdir] [cooldown_sec]
"""
from __future__ import annotations
import sys, time
from pathlib import Path
import cv2
from flask import Flask, Response, jsonify, redirect, send_from_directory

from tpu_common import make_interpreter, set_input, get_detections, count_people, draw_boxes_bgr, now_ts

app = Flask(__name__)

STATE = {
    "cap": None,
    "interp": None,
    "thresh": 0.5,
    "cam_index": 0,
    "cap_w": 640,
    "cap_h": 480,
    "in_w": 300,
    "in_h": 300,
    "last_people": 0,
    "last_infer_ms": 0.0,
    "fps": 0.0,
    "last_frame_bgr": None,
    "last_saved_ts": 0.0,
    "cooldown": 2.0,
    "outdir": None,
    "model": None,
}

def init(model_path: str, cam_index: int, thresh: float, cap_w: int, cap_h: int, outdir: str, cooldown: float):
    if not Path(model_path).exists():
        raise SystemExit(f"Model not found: {model_path}")

    od = Path(outdir)
    od.mkdir(parents=True, exist_ok=True)

    interp = make_interpreter(model_path)
    in_detail = interp.get_input_details()[0]
    _, ih, iw, _ = in_detail["shape"]

    cap = cv2.VideoCapture(cam_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cap_w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_h)
    if not cap.isOpened():
        raise SystemExit(f"Cannot open camera index {cam_index}")

    STATE.update({
        "cap": cap,
        "interp": interp,
        "thresh": thresh,
        "cam_index": cam_index,
        "cap_w": cap_w,
        "cap_h": cap_h,
        "in_w": iw,
        "in_h": ih,
        "cooldown": float(cooldown),
        "outdir": str(od.resolve()),
        "model": model_path,
    })

def save_frame(reason: str = "snapshot") -> str:
    frame = STATE["last_frame_bgr"]
    if frame is None:
        raise RuntimeError("No frame yet")
    people = int(STATE["last_people"])
    infer_ms = float(STATE["last_infer_ms"])
    fps = float(STATE["fps"])
    name = f"{now_ts()}_{reason}_people{people}_tpu{infer_ms:.1f}ms_fps{fps:.1f}.jpg"
    outpath = Path(STATE["outdir"]) / name
    cv2.imwrite(str(outpath), frame)
    STATE["last_saved_ts"] = time.time()
    return name

def gen():
    last_t = time.time()
    frames = 0
    while True:
        ok, frame = STATE["cap"].read()
        if not ok or frame is None:
            time.sleep(0.01)
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_resized = cv2.resize(rgb, (STATE["in_w"], STATE["in_h"]), interpolation=cv2.INTER_LINEAR)

        set_input(STATE["interp"], rgb_resized)
        t0 = time.time()
        STATE["interp"].invoke()
        infer_ms = (time.time() - t0) * 1000.0

        dets = get_detections(STATE["interp"], score_thresh=STATE["thresh"])
        people = count_people(dets, person_class=0)
        STATE["last_people"] = people
        STATE["last_infer_ms"] = infer_ms

        draw_boxes_bgr(frame, dets, STATE["thresh"], person_class=0)
        cv2.putText(frame, f"people:{people}  tpu:{infer_ms:.1f}ms  fps:{STATE['fps']:.1f}", (10, 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        STATE["last_frame_bgr"] = frame.copy()

        now = time.time()
        if people > 0 and (now - float(STATE["last_saved_ts"])) >= float(STATE["cooldown"]):
            try:
                save_frame(reason="auto")
            except Exception:
                pass

        ok2, jpg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ok2:
            continue

        frames += 1
        if now - last_t >= 1.0:
            STATE["fps"] = frames / (now - last_t)
            frames = 0
            last_t = now

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + jpg.tobytes() + b"\r\n")

@app.route("/")
def index():
    return """<!doctype html>
<html><head><meta charset="utf-8"><title>Coral Stream + Events</title></head>
<body>
<h2>Coral Stream + Events</h2>
<ul>
  <li><a href="/video">/video</a> (MJPEG)</li>
  <li><a href="/status">/status</a></li>
  <li><a href="/snapshot">/snapshot</a> (save now)</li>
  <li><a href="/events">/events</a></li>
</ul>
<img src="/video" style="max-width: 100%; height: auto;" />
</body></html>"""

@app.route("/video")
def video():
    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/status")
def status():
    return jsonify({
        "model": STATE["model"],
        "cam_index": STATE["cam_index"],
        "capture": {"w": STATE["cap_w"], "h": STATE["cap_h"]},
        "thresh": STATE["thresh"],
        "people": int(STATE["last_people"]),
        "infer_ms": float(STATE["last_infer_ms"]),
        "fps": float(STATE["fps"]),
        "outdir": STATE["outdir"],
        "cooldown_sec": float(STATE["cooldown"]),
    })

@app.route("/snapshot")
def snapshot():
    name = save_frame(reason="snapshot")
    return redirect(f"/out/{name}", code=302)

@app.route("/events")
def events():
    od = Path(STATE["outdir"])
    imgs = sorted([p.name for p in od.glob("*.jpg")], reverse=True)[:80]
    items = "\n".join([f'<li><a href="/out/{n}">{n}</a></li>' for n in imgs]) or "<li>(no images yet)</li>"
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Events</title></head>
<body>
<h2>Events (saved images)</h2>
<p>Folder: <code>{STATE['outdir']}</code></p>
<p><a href="/">Back</a></p>
<ol>
{items}
</ol>
</body></html>"""

@app.route("/out/<path:filename>")
def out_file(filename):
    return send_from_directory(STATE["outdir"], filename)

def main():
    if len(sys.argv) < 3:
        print(__doc__.strip())
        sys.exit(2)

    model_path = sys.argv[1]
    cam_index = int(sys.argv[2])
    thresh = float(sys.argv[3]) if len(sys.argv) >= 4 else 0.5
    w = int(sys.argv[4]) if len(sys.argv) >= 5 else 640
    h = int(sys.argv[5]) if len(sys.argv) >= 6 else 480
    port = int(sys.argv[6]) if len(sys.argv) >= 7 else 8080
    outdir = sys.argv[7] if len(sys.argv) >= 8 else "./out"
    cooldown = float(sys.argv[8]) if len(sys.argv) >= 9 else 2.0

    init(model_path, cam_index, thresh, w, h, outdir, cooldown)
    print(f"Starting stream+events on 0.0.0.0:{port}")
    print(f"Open: http://<PI-IP>:{port}/   (events: /events)")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)

if __name__ == "__main__":
    main()
