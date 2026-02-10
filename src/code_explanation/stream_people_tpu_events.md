# Explanation of the code in file stream_people_tpu_events.py

This L9 code is **"L8(stream_people_tpu_mjpeg.py) + Events Recording"** Simply put:
- It still streams live images to the browser via MJPEG as before.
- But adds the following capabilities:
    - `/status (JSON)`: To view the latest status.
    - `/snapshot`: To manually trigger an immediate image save.
    - **Auto save**: Automatically saves an image when a **"person"** is detected, featuring a cooldown to prevent redundant captures.
    - `/events`: To view the list of recorded images.
    - `/out/<file>`: To open and view specific recorded images.

---

## 1. Overall Operational Structure

Main Loop (gen)

```sh
Camera → frame
       → RGB + resize → TPU inference
       → Parse detections → Count people
       → Draw boxes + overlay
       → Store last_frame_bgr for snapshot/auto-save.
       → If person detected AND cooldown passed → save_frame("auto").
       → Encode JPEG → yield as MJPEG.
```

<br>

Web Side (Flask endpoints)
- `/`: Main page for live viewing.
- `/video`: Video stream (MJPEG).
- `/status`: Current status in JSON format.
- `/snapshot`: Immediately save a frame and redirect to view the image.
- `/events`: Page listing previously recorded images.
- `/out/<file>`: Serves the saved image file to the browser.

---

## 2. STATE: Shared storage for all 

Several new fields have been added compared to L8(stream_people_tpu_mjpeg.py):
```py
"last_frame_bgr": None,     # Store the last frame (with drawn frame and overlay)
"last_saved_ts": 0.0,       # Last save time (to prevent spam)
"cooldown": 2.0,            # Minimum delay before saving again (seconds)
"outdir": None,             # Folder to store images
"model": None,              # Model path
```

---

## 3. init(): Prepare model + camera + output folder

Differs from L8 by adding **"outdir"** and **"cooldown"**.

```py
od = Path(outdir)
od.mkdir(parents=True, exist_ok=True)
```

Then:
- Load interpreter (Edge TPU).
- Open camera.
- Save all values into `STATE`.

---

## 4. save_frame(): The "Save Image" Function

This is the key highlight of L9.

```py
frame = STATE["last_frame_bgr"]
if frame is None:
    raise RuntimeError("No frame yet")
```

- Uses the latest frame stored by `gen()` (therefore, if the system hasn't read the camera yet, it cannot save).

<br>

Create filename with metadata:

```py
name = f"{now_ts()}_{reason}_people{people}_tpu{infer_ms:.1f}ms_fps{fps:.1f}.jpg"
```

Filename example: `20260210_173012_auto_people1_tpu4.2ms_fps19.8.jpg`
- `now_ts()` comes from **tpu_common** to create a timestamp.
- `reason` is either **"snapshot" or "auto"**.
- Attaches the person count / TPU time / FPS for very easy retrospective review.

<br>

Then save:

```py
cv2.imwrite(str(outpath), frame)
STATE["last_saved_ts"] = time.time()
```

---

## 5. gen(): Camera Loop + Inference + Auto Save + Stream

The inference part is similar to L8 but adds two major points:

### 5.1 Store “Latest Frame” for snapshot/auto-

```py
STATE["last_frame_bgr"] = frame.copy()
```

- Uses `.copy()` to prevent the frame from being modified in the next cycle.

### 5.2 Auto-save when person detected + cooldown passed

```py
now = time.time()
if people > 0 and (now - STATE["last_saved_ts"]) >= STATE["cooldown"]:
    save_frame(reason="auto")
```

- If a person is detected in this frame.
- And the time since the "last save" exceeds the `cooldown` seconds.
- Automatically save the image.

Includes `try/except` to prevent program crashes (e.g., disk full/permission issues).

---

## 6. Flask endpoints added from L8

`/status` (JSON) Returns the latest data from STATE:

```json
{
  "people": 1,
  "infer_ms": 4.2,
  "fps": 18.7,
  "outdir": "/home/pi/out",
  "cooldown_sec": 2.0
}
```

Ideal for:
- Creating Dashboards.
- Allowing ESP32 or backends to poll data.
- Integrating with MQTT/Node-RED.

<br>

`/snapshot` Immediately records an image (manual).

```py
name = save_frame(reason="snapshot")
return redirect(f"/out/{name}", code=302)
```

- Saves the image, then immediately redirects to open that image.

<br>

`/events` Displays a list of images recorded in the **outdir**.

```py
imgs = sorted([...], reverse=True)[:80]
```

- Shows the most recent images first.
- Limited to the latest 80 images.

<br>

`/out/<file>`

```py
return send_from_directory(STATE["outdir"], filename)
```

- Serves image files from the **outdir** folder so the browser can open them.

---

## 7. `main()`: Accepts 2 additional 

Different from L8 by adding:
- `outdir` (default: `./out`)
- `cooldown` (default: `2.0` seconds)

```py
python3 stream_people_tpu_events.py model.tflite 0 0.5 640 480 8080 ./out 2.0
```

---