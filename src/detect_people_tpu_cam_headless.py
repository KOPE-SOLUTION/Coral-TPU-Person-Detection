#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L7 — Real-time from USB camera (headless, no GUI)

Usage:
  python3 detect_people_tpu_cam_headless.py <model_edgetpu.tflite> <cam_index> [score_thresh] [width] [height]

Example:
  python3 detect_people_tpu_cam_headless.py models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite 0 0.5 640 480
"""
from __future__ import annotations
import sys, time
from pathlib import Path
import cv2

from tpu_common import make_interpreter, set_input, get_detections, count_people

def main():
    if len(sys.argv) < 3:
        print(__doc__.strip())
        sys.exit(2)

    model_path = sys.argv[1]
    cam_index = int(sys.argv[2])
    thresh = float(sys.argv[3]) if len(sys.argv) >= 4 else 0.5
    w = int(sys.argv[4]) if len(sys.argv) >= 5 else 640
    h = int(sys.argv[5]) if len(sys.argv) >= 6 else 480

    if not Path(model_path).exists():
        raise SystemExit(f"Model not found: {model_path}")

    interp = make_interpreter(model_path)
    in_detail = interp.get_input_details()[0]
    _, ih, iw, _ = in_detail["shape"]

    cap = cv2.VideoCapture(cam_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

    if not cap.isOpened():
        raise SystemExit(f"Cannot open camera index {cam_index} (try 0/1).")

    print(f"MODEL: {model_path}")
    print(f"CAM: /dev/video{cam_index}  capture: {w}x{h}  model_in: {iw}x{ih}  thresh: {thresh}")
    print("Headless mode: no GUI. Press Ctrl+C to stop.")

    last_report = time.time()
    frames = 0
    people_frames = 0
    infer_ms_acc = 0.0

    try:
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                time.sleep(0.02)
                continue

            frames += 1
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_resized = cv2.resize(rgb, (iw, ih), interpolation=cv2.INTER_LINEAR)

            set_input(interp, rgb_resized)
            t0 = time.time()
            interp.invoke()
            infer_ms = (time.time() - t0) * 1000.0
            infer_ms_acc += infer_ms

            dets = get_detections(interp, score_thresh=thresh)
            if count_people(dets, person_class=0) > 0:
                people_frames += 1

            now = time.time()
            if now - last_report >= 1.0:
                fps = frames / (now - last_report)
                avg_inf = infer_ms_acc / max(1, frames)
                print(f"FPS {fps:5.1f} | infer avg {avg_inf:6.1f} ms | frames {frames} | frames_with_people {people_frames}")
                last_report = now
                frames = 0
                people_frames = 0
                infer_ms_acc = 0.0

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        cap.release()

if __name__ == "__main__":
    main()
