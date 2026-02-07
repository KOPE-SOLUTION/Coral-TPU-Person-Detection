#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common helpers for Coral EdgeTPU + TFLite SSD models.
Designed for Raspberry Pi OS Bullseye 64-bit (native).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
import time
import numpy as np

try:
    from tflite_runtime.interpreter import Interpreter, load_delegate
except Exception as e:  # pragma: no cover
    raise RuntimeError("tflite_runtime not found. Install: sudo apt install -y python3-tflite-runtime") from e

EDGETPU_SO_CANDIDATES = [
    "libedgetpu.so.1",
    "/lib/aarch64-linux-gnu/libedgetpu.so.1",
    "/usr/lib/aarch64-linux-gnu/libedgetpu.so.1",
]

def load_edgetpu_delegate() -> Any:
    last_err = None
    for so in EDGETPU_SO_CANDIDATES:
        try:
            return load_delegate(so)
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Failed to load EdgeTPU delegate. Tried: {EDGETPU_SO_CANDIDATES}. Last error: {last_err}")

def make_interpreter(model_path: str) -> Interpreter:
    delegate = load_edgetpu_delegate()
    interp = Interpreter(model_path=model_path, experimental_delegates=[delegate])
    interp.allocate_tensors()
    return interp

def _quant_params(detail: Dict[str, Any]) -> Tuple[float, int]:
    q = detail.get("quantization", None)
    if q and isinstance(q, (list, tuple)) and len(q) == 2:
        return float(q[0]), int(q[1])
    return 0.0, 0

def set_input(interp: Interpreter, img_rgb: np.ndarray) -> None:
    """img_rgb: HxWx3, already resized to model input size."""
    in_detail = interp.get_input_details()[0]
    idx = in_detail["index"]
    dtype = in_detail["dtype"]
    if dtype == np.uint8:
        tensor = img_rgb.astype(np.uint8)
    else:
        tensor = (img_rgb.astype(np.float32) / 255.0)
    interp.set_tensor(idx, np.expand_dims(tensor, axis=0))

def _dequantize(arr: np.ndarray, detail: Dict[str, Any]) -> np.ndarray:
    scale, zero = _quant_params(detail)
    if scale and arr.dtype != np.float32:
        return (arr.astype(np.float32) - zero) * scale
    return arr.astype(np.float32)

@dataclass
class Detection:
    klass: int
    score: float
    box: Tuple[float, float, float, float]  # ymin,xmin,ymax,xmax normalized

def get_detections(interp: Interpreter, score_thresh: float = 0.5, top_k: int = 50) -> List[Detection]:
    """Heuristic SSD output parsing (works with common Mobilenet-SSD postprocess models)."""
    out_details = interp.get_output_details()
    outs = [interp.get_tensor(d["index"]) for d in out_details]

    def squeeze(a):
        a = np.array(a)
        if a.ndim >= 2 and a.shape[0] == 1:
            return np.squeeze(a, axis=0)
        return a

    outs_s = [squeeze(o) for o in outs]

    boxes_i = classes_i = scores_i = None

    # Find boxes by shape (*,4)
    for i, a in enumerate(outs_s):
        if a.ndim == 2 and a.shape[1] == 4:
            boxes_i = i
            break
    if boxes_i is None:
        for i, a in enumerate(outs_s):
            if a.ndim == 3 and a.shape[-1] == 4:
                outs_s[i] = a.reshape(-1, 4)
                boxes_i = i
                break

    # Find candidates 1D arrays
    one_d = [(i, a) for i, a in enumerate(outs_s) if a.ndim == 1 and i != boxes_i]
    one_d_deq = [(i, _dequantize(a, out_details[i])) for i, a in one_d]

    # scores in [0,1]
    for i, a in one_d_deq:
        if np.nanmin(a) >= -0.01 and np.nanmax(a) <= 1.01:
            scores_i = i
            break

    # classes close to integers
    for i, a in one_d_deq:
        if i == scores_i:
            continue
        if np.nanmin(a) >= -1 and np.nanmax(a) <= 200 and float(np.mean(np.abs(a - np.round(a)))) < 0.2:
            classes_i = i
            break

    # fallback if still missing
    rem = [i for i, _ in one_d_deq if i not in (scores_i, classes_i)]
    if scores_i is None and rem:
        scores_i = rem.pop(0)
    if classes_i is None and rem:
        classes_i = rem.pop(0)

    if boxes_i is None or scores_i is None or classes_i is None:
        raise RuntimeError(f"Cannot identify SSD outputs. shapes={[o.shape for o in outs_s]}")

    boxes = _dequantize(outs_s[boxes_i], out_details[boxes_i])
    scores = _dequantize(outs_s[scores_i], out_details[scores_i])
    classes = _dequantize(outs_s[classes_i], out_details[classes_i])

    N = int(boxes.shape[0])
    dets: List[Detection] = []
    for i in range(min(N, top_k)):
        sc = float(scores[i])
        if sc < score_thresh:
            continue
        kl = int(round(float(classes[i])))
        y1, x1, y2, x2 = [float(v) for v in boxes[i]]
        dets.append(Detection(klass=kl, score=sc, box=(y1, x1, y2, x2)))
    return dets

def now_ts() -> str:
    return time.strftime("%Y%m%d_%H%M%S", time.localtime())

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))

def box_to_pixels(box: Tuple[float,float,float,float], w: int, h: int) -> Tuple[int,int,int,int]:
    y1, x1, y2, x2 = [clamp01(v) for v in box]
    return (int(x1*w), int(y1*h), int(x2*w), int(y2*h))  # x1,y1,x2,y2

def count_people(dets: List[Detection], person_class: int = 0) -> int:
    return sum(1 for d in dets if d.klass == person_class)

def draw_boxes_bgr(frame_bgr, dets: List[Detection], thresh: float, person_class: int = 0):
    import cv2
    h, w = frame_bgr.shape[:2]
    for d in dets:
        if d.score < thresh:
            continue
        x1,y1,x2,y2 = box_to_pixels(d.box, w, h)
        color = (0, 255, 0) if d.klass == person_class else (255, 255, 0)
        cv2.rectangle(frame_bgr, (x1,y1), (x2,y2), color, 2)
        label = f"{'person' if d.klass==person_class else d.klass}:{d.score:.2f}"
        cv2.putText(frame_bgr, label, (x1, max(0, y1-8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    return frame_bgr
