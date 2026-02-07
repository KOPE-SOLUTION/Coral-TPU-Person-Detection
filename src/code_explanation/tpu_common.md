# Explanation of the code in file tpu_common.py

## Overview: What does this file do?

This file is a **helper package** for running **TFLite SSDs** (e.g., **MobileNet-SSD**) on a **Coral USB Edge TPU**, with a focus on the Raspberry Pi OS Bullseye 64-bit.

Things that can make it easier for you include:

1. Load the **EdgeTPU delegate** (**libedgetpu.so.1**)
2. Create a **TFLite interpreter** with a **delegate**.
3. Feed the model input (supports uint8/float).
4. Retrieve the output and **"guess/match"** which are **boxes/classes/scores**.
5. Convert boxes to pixels + count people + draw frames on the image.

---

## 1. Import and check dependencies.

```py
try:
    from tflite_runtime.interpreter import Interpreter, load_delegate
except Exception as e:
    raise RuntimeError("tflite_runtime not found. Install: sudo apt install -y python3-tflite-runtime") from e
```

- Use `tflite_runtime` (more suitable for Pi than the full TensorFlow version).
- If not used, it will throw an error with clear installation instructions.

---

## 2. List of paths for the EdgeTPU shared library.

```py
EDGETPU_SO_CANDIDATES = [
    "libedgetpu.so.1",
    "/lib/aarch64-linux-gnu/libedgetpu.so.1",
    "/usr/lib/aarch64-linux-gnu/libedgetpu.so.1",
]
```

- In some systems, `libedgetpu.so.1` is located in a different location.
- Therefore, I tried several paths to ensure a "robust" solution.

<br>

**Load delegate**

```py
def load_edgetpu_delegate():
    for so in EDGETPU_SO_CANDIDATES:
        try:
            return load_delegate(so)
        except Exception as e:
            last_err = e
    raise RuntimeError(...)
```

- Try each path one at a time.
- If all paths fail, it will display an error along with the "**total paths tried + the latest error"**, which is very useful for debugging.

---

## 3. Create an interpreter with a delegate.

```py
def make_interpreter(model_path: str) -> Interpreter:
    delegate = load_edgetpu_delegate()
    interp = Interpreter(model_path=model_path, experimental_delegates=[delegate])
    interp.allocate_tensors()
    return interp
```

- `experimental_delegates=[delegate]` binds EdgeTPU to the interpreter.
- `allocate_tensors()` must be called before set_tensor/invoke.

> Used with the `_edgetpu.tflite` model, it will achieve full acceleration on TPU (if the OP supports it).

---

## 4. Handle quantization/dequantization

**Read quantization values**

```py
def _quant_params(detail):
    q = detail.get("quantization", None)  # (scale, zero_point)
```

- TFLite tensor has `quantization=(scale, zero_point)`
- If none exists, return (`0.0,0`)

<br>

**dequantize output**

```py
def _dequantize(arr, detail):
    scale, zero = _quant_params(detail)
    if scale and arr.dtype != np.float32:
        return (arr.astype(np.float32) - zero) * scale
    return arr.astype(np.float32)
```

- If the output is int8/uint8 and there is a scale, convert it to float for easier use.
- This allows the code below to correctly compare the score range [0..1].

---

## 5. Input the model.

```py
def set_input(interp, img_rgb):
    in_detail = interp.get_input_details()[0]
    dtype = in_detail["dtype"]
    if dtype == np.uint8:
        tensor = img_rgb.astype(np.uint8)
    else:
        tensor = (img_rgb.astype(np.float32) / 255.0)
    interp.set_tensor(idx, np.expand_dims(tensor, axis=0))
```

What this code assumes:
- `img_rgb` must be RGB (not BGR) and resized to match the model's input.
- If the model requires `uint8`, pass uint8 directly.
- If the model requires float normalized to 0..1.

> Practical use: If you read the image with OpenCV, it will be BGR, so you need to use `cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)` first.

---

## 6. Detection data structure

```py
@dataclass
class Detection:
    klass: int
    score: float
    box: (ymin,xmin,ymax,xmax) normalized
```

- Store detection results in an organized manner.
- The box is normalized from 0..1 for easy use with all resolutions.

---

## 7. Extracting SSD results (the most important part).

```py
def get_detections(interp, score_thresh=0.5, top_k=50):
    out_details = interp.get_output_details()
    outs = [interp.get_tensor(d["index"]) for d in out_details]
```

- Read all output from the model.
- Some SSD models have different output orders, so this code uses a "heuristic" to guess what each one is.

<br>

**Heuristic procedure performed:**

1. **Finding boxes**: tensor shape `(*,4)`

    ```py
    if a.ndim == 2 and a.shape[1] == 4: boxes_i = i
    ```

<br>

2. **Find scores**: tensor 1D values ​​close to `[0..1]`.

    ```py
    if np.nanmin(a) >= -0.01 and np.nanmax(a) <= 1.01: scores_i = i
    ```

<br>

3. **Find classes**: 1D tensors whose values ​​appear to be integers.

    ```py
    mean(abs(a-round(a))) < 0.2
    ```

<br>

4. If it's still not found, use a fallback to retrieve the remaining elements.

    Finally, if it's truly impossible to find, display an error along with all shapes.

    ```py
    raise RuntimeError(f"Cannot identify SSD outputs. shapes=...")
    ```

    > **Advantages**: Works with many types of SSDs.
    > **Caution**: If the output model is not standard (e.g., YOLO), it will not pass.

<br>

**สร้าง list ของ detection**

```py
for i in range(min(N, top_k)):
    if score < thresh: continue
    klass = int(round(classes[i]))
    box = boxes[i]  # ymin,xmin,ymax,xmax
```

---

## 8.Utility functions

**timestamp**

```py
def now_ts(): return time.strftime("%Y%m%d_%H%M%S")
```

<br>

**Clamp and convert the box to pixels.**

```py
def box_to_pixels(box, w, h):
    return (int(x1*w), int(y1*h), int(x2*w), int(y2*h))
```

- The SSD provides (ymin,xmin,ymax,xmax) normalized data.
- Convert to (x1,y1,x2,y2) for drawing frames with OpenCV.

<br>

**Counting people**

```py
def count_people(dets, person_class=0):
    return sum(1 for d in dets if d.klass == person_class)
```

- In most COCO models: `person` is class 0 (but some label maps may differ). Be mindful of this.

---

## 9. Draw a frame around the image (BGR)

```py
def draw_boxes_bgr(frame_bgr, dets, thresh, person_class=0):
    cv2.rectangle(...)
    cv2.putText(...)
```

- Receive a BGR image (using standard OpenCV format).
- Draw green for a person, light blue for other classes.
- Label as `person:0.87` or `5:0.71`

---

## Brief instructions (correct order of use)

1. `interp = make_interpreter(model_edgetpu_path)`
2. resize+RGB: `img_rgb = ...`
3. `set_input(interp, img_rgb)`
4. `interp.invoke()`
5. `dets = get_detections(interp, 0.5)`
6. `draw_boxes_bgr(frame_bgr, dets, 0.5)`

---

## Points to watch out for/adjust in a real project:

- `person_class=0` must be consistent with the label map of the model being used.
- `set_input()` currently does not perform mean/std normalization (some models require this).
- `get_detections()` is a heuristic for SSD only (not YOLO).

---