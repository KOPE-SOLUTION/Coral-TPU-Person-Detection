# Explanation of the code in file detect_people_tpu_cam_headless.py

## Code Overview

The script performs the following tasks:
1. **Accepts parameters**: Model path, camera index, confidence threshold, and capture resolution.
2. **Initializes the camera**: Opens the camera feed using OpenCV (`cv2.VideoCapture`).
3. **Frame processing loop**: Reads frames sequentially, converts them to **RGB**, and **resizes** them to match the model’s input requirements.
4. **Inference**: Feeds data into the TPU and executes `invoke()`.
5. **Result processing**: Reads detection outputs to determine if a **"Person"** is present.
6. **Performance reporting**: Displays **FPS**, **average inference time (ms)**, **total frames** processed, and the **count of frames** where people were detected.

---

## 1. Receiving command line arguments

```py
model_path = sys.argv[1]
cam_index = int(sys.argv[2])
thresh = float(sys.argv[3]) if len(sys.argv) >= 4 else 0.5
w = int(sys.argv[4]) if len(sys.argv) >= 5 else 640
h = int(sys.argv[5]) if len(sys.argv) >= 6 else 480
```

- **model_path** : The `.tflite` file compiled for Edge TPU.
- **cam_index** : Camera index (typically 0 or 1 : `/dev/video0`, `/dev/video1`).
- **thresh** : Minimum confidence threshold (default 0.5).
- **w, h** → Capture resolution for the camera (default 640×480).

If the first two arguments (model + cam_index) are not provided, the script prints the manual and terminates the program.

---

## 2. Model existence check

```py
if not Path(model_path).exists():
    raise SystemExit(f"Model not found: {model_path}")
```

---

## 3. Creating TPU Interpreter and identifying model input dimensions

```py
interp = make_interpreter(model_path)
in_detail = interp.get_input_details()[0]
_, ih, iw, _ = in_detail["shape"]
```

- `make_interpreter()` (from `tpu_common`) creates a TFLite Interpreter with the Edge TPU delegate.
- `ih, iw` = Height and width required by the model, such as 300×300 or 320×320.

---

## 4. Opening the camera with OpenCV and setting capture resolution

```py
cap = cv2.VideoCapture(cam_index)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
```

Then, check if the camera can be opened:

```py
if not cap.isOpened():
    raise SystemExit(f"Cannot open camera index {cam_index} (try 0/1).")
```

---

## 5. Printing initial information (for easier debugging)

```py
print(f"CAM: /dev/video{cam_index}  capture: {w}x{h}  model_in: {iw}x{ih}  thresh: {thresh}")
print("Headless mode: no GUI. Press Ctrl+C to stop.")
```

---

## 6. Statistical accumulation variables for reporting every ~1 second

```py
last_report = time.time()
frames = 0
people_frames = 0
infer_ms_acc = 0.0
```

- `frames` : Number of frames processed during the last 1 second.
- `people_frames` : Number of frames where a "person" was detected.
- `infer_ms_acc` : Accumulated inference time (used to calculate the average).

## 7. Frame Reading Loop and Inference

Read frame:

```py
ok, frame = cap.read()
if not ok or frame is None:
    time.sleep(0.02)
    continue
```

<br>

Convert BGR to RGB (OpenCV reads in BGR):

```py
rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
```

<br>

Resize to match model input:

```py
rgb_resized = cv2.resize(rgb, (iw, ih), interpolation=cv2.INTER_LINEAR)
```

<br>

Feed into TPU and run inference:

```py
set_input(interp, rgb_resized)
t0 = time.time()
interp.invoke()
infer_ms = (time.time() - t0) * 1000.0
infer_ms_acc += infer_ms
```

---

## 8. Reading Detection Results and Counting “People”

```py
dets = get_detections(interp, score_thresh=thresh)
if count_people(dets, person_class=0) > 0:
    people_frames += 1
```

- `get_detections()` จะอ่าน output tensors และกรองด้วย `score_thresh`
- `count_people(..., person_class=0)` เพราะใน COCO: class 0 คือ person
- If at least one person is found in a frame, add `people_frames`.

> Note: This code counts **"frames containing people"**, not the **"total number of people detected"**.

---

## 9. Reporting every 1 second: FPS + Average Inference

```py
if now - last_report >= 1.0:
    fps = frames / (now - last_report)
    avg_inf = infer_ms_acc / max(1, frames)
    print(f"FPS {fps:5.1f} | infer avg {avg_inf:6.1f} ms | frames {frames} | frames_with_people {people_frames}")
```

Then, reset values to start a new cycle:

```py
last_report = now
frames = 0
people_frames = 0
infer_ms_acc = 0.0
```

---

## 10. Stop with Ctrl+C and properly close the camera

```py
except KeyboardInterrupt:
    print("\nStopping...")
finally:
    cap.release()
```

---