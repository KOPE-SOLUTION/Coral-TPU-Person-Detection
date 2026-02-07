#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L6 — Still image smoke test (Coral TPU)

Usage:
  python3 detect_people_tpu_image.py <model_edgetpu.tflite> <image.jpg> [score_thresh]

Example:
  python3 detect_people_tpu_image.py models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite input.jpg 0.5
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import time

from tpu_common import make_interpreter, set_input, get_detections, count_people

def main():
    if len(sys.argv) < 3:
        print(__doc__.strip())
        sys.exit(2)

    model_path = sys.argv[1]
    img_path = sys.argv[2]
    thresh = float(sys.argv[3]) if len(sys.argv) >= 4 else 0.5

    if not Path(model_path).exists():
        raise SystemExit(f"Model not found: {model_path}")
    if not Path(img_path).exists():
        raise SystemExit(f"Image not found: {img_path}")

    interp = make_interpreter(model_path)
    in_detail = interp.get_input_details()[0]
    _, ih, iw, ic = in_detail["shape"]
    if ic != 3:
        raise SystemExit(f"Expected 3-channel input, got {ic}")

    img = Image.open(img_path).convert("RGB")
    img_resized = img.resize((iw, ih), Image.BILINEAR)
    img_np = np.asarray(img_resized, dtype=np.uint8)

    set_input(interp, img_np)

    t0 = time.time()
    interp.invoke()
    dt = (time.time() - t0) * 1000.0

    dets = get_detections(interp, score_thresh=thresh)
    people = count_people(dets, person_class=0)

    print(f"OK inference: {dt:.2f} ms  detections: {len(dets)}  people: {people}")
    for i, d in enumerate(dets[:20]):
        y1,x1,y2,x2 = d.box
        print(f"- id={i:02d} class={d.klass} score={d.score:.2f} box(ymin,xmin,ymax,xmax)=({y1:.3f},{x1:.3f},{y2:.3f},{x2:.3f})")

if __name__ == "__main__":
    main()
