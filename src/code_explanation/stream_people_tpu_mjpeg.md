# Explanation of the code in file stream_people_tpu_mjpeg.py

## Overview

This script performs the following:

1. Opens a **USB camera**.
2. Runs **Object Detection (person)** on the **Coral Edge TPU**.
3. Draws **bounding boxes** and **information overlays**.
4. Converts frames into an **MJPEG stream**.
5. Starts a **web server** using **Flask**.
6. Allows viewing the live stream via browser at: `http://<IP>:<PORT>/video`


> Ideal for **Edge AI + Dashboard / Monitoring / Smart Farm / Security** applications.

---

## High-level structure

```sh
Camera (OpenCV)
        ↓
Resize → Edge TPU inference
        ↓
Parse detection (people)
        ↓
Draw boxes + overlay
        ↓
JPEG encode
        ↓
Flask MJPEG stream → Browser
```

---

## 1. Imports and Flask App

```py
import cv2
from flask import Flask, Response
```

- `cv2` : Handles the camera, image drawing, and JPEG encoding.
- `Flask` : Web server.
- `Response` : Sends the MJPEG stream.

<br>

```py
from tpu_common import make_interpreter, set_input, get_detections, count_people, draw_boxes_bgr
```

Key functions:
- `make_interpreter()` : Creates the Edge TPU interpreter.
- `set_input()` : Feeds the image into the model.
- `get_detections()` : Reads the output tensor.
- `count_people()` : Counts class=person.
- `draw_boxes_bgr()` : Draws bounding boxes on the image (BGR).

<br>

```py
app = Flask(__name__)
```

- `Flask(name)` :Creates an instance of the Flask class to define this file as the main application.
- `__name__`: A special Python variable that passes the current module's name to Flask, allowing it to locate associated files like templates or static assets.
- **Function**: Serves as the core for managing web operations, such as defining routes, handling requests, and sending responses.

---

## 2. STATE : global shared state

```py
STATE = {
    "cap": None,
    "interp": None,
    "thresh": 0.5,
    ...
}
```

Reasons for using STATE:
- The **Flask endpoint** (`/video`) and the **inference loop **must share the same data.
- Reduces redundant **object creation**.
- Serves as a** global runtime state**.

Information contained within:
- `cap` : Camera object.
- `interp` : TPU interpreter.
- `last_people` : Latest person count.
- `fps` : Latest FPS.
- `in_w, in_h` : Model input dimensions.

---

## 3. `init()` : System initialization

```py
def init(model_path, cam_index, thresh, cap_w, cap_h):
```

- Verifies that the model exists.
- Creates the Edge TPU interpreter.
- Reads the model's input shape.
- Opens the USB camera.
- Saves all values into the STATE.

<br>

```py
interp = make_interpreter(model_path)
_, ih, iw, _ = in_detail["shape"]
```

- required resize dimensions (e.g., 300×300).

<br>

```py
cap = cv2.VideoCapture(cam_index)
```

- Opens `/dev/videoX`.

<br>

Finally:

```py
STATE.update({...})
```

---

## 4. `gen()` : The heart of the MJPEG stream

This is the generator that Flask calls repeatedly to stream images.

### 4.1 Read frame from camera

```py
ok, frame = STATE["cap"].read()
```

- If reading fails, sleep briefly and skip.

### 4.2 Prepare image for TPU

```py
rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
rgb_resized = cv2.resize(rgb, (STATE["in_w"], STATE["in_h"]))
```

- **OpenCV** : BGR
- **Model** : RGB
- **Resize** to match input.

### 4.3 Inference on Edge TPU

```py
set_input(STATE["interp"], rgb_resized)
STATE["interp"].invoke()
```

Measure inference time:

```py
infer_ms = (time.time() - t0) * 1000.0
```

### 4.4 Read detection results + count people

```py
dets = get_detections(...)
people = count_people(dets, person_class=0)
```

- COCO class `0` = person
- Store values in `STATE`.

### 4.5 Draw bounding boxes + overlay text

```py
draw_boxes_bgr(frame, dets, ...)
```

Draw boxes on the original image (BGR).

```py
cv2.putText(frame, f"people:{people}  tpu:{infer_ms:.1f}ms  fps:{STATE['fps']:.1f}", ...)
```

Display real-time information on the image.

### 4.6 Encode image as JPEG

```py
ok2, jpg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
```

- balance between quality and speed.

### 4.7 Calculate FPS

```py
STATE["fps"] = frames / (now - last_t)
```

- Update approximately every 1 second.

### 4.8 Send MJPEG frame out

```py
yield (b"--frame\r\n"
       b"Content-Type: image/jpeg\r\n\r\n" + jpg.tobytes() + b"\r\n")
```

- This is the **MJPEG over HTTP** standard.

---

## 5. Flask endpoints

**`/` : Simple webpage**

```py
@app.route("/")
def index():
```
- Standard HTML.
- Contains `<img src="/video">`.

<br>

**`/video` : MJPEG stream**

```py
@app.route("/video")
def video():
    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")
```

- The browser calls `gen()` continuously.
- Provides a live feed without requiring **WebSockets**.

---

## 6. `main()` : Program entry point

```py
model_path = sys.argv[1]
cam_index = int(sys.argv[2])
...
port = int(sys.argv[6]) if len(sys.argv) >= 7 else 8080
```

- Accepts all **arguments**.
- Calls `init()`.
- Starts the **Flask server**.

<br>

```py
app.run(host="0.0.0.0", port=port, threaded=True)
```

- `0.0.0.0` : Allows other devices on the network to access it.
- `threaded=True` : Supports multiple clients.

---