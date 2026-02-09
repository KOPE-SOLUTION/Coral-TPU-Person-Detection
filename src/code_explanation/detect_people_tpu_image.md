# Explanation of the code in file detect_people_tpu_image.py

## Overview

**Code Functionality** This script loads a TFLite model compiled specifically for the Coral Edge TPU to perform the following tasks:
- **Image Input**: Reads a single static image.
- **Inference**: Executes the detection model on the Edge TPU hardware.
- **Data Extraction**: Retrieves Object Detection results from the model output.
- **Class Counting**: Specifically counts the number of "People" detected in the image.
- **Performance Metrics**: Displays the inference time and final results via the console.

<br>

**Key Technical Terms Used**:
- **Inference**: The process of running data through a machine learning model.
- **Edge TPU**: The hardware accelerator (Coral) used for high-speed AI.
- **Console**: The terminal or command line where the output is displayed.

---

## 1. File Header (Shebang + Docstring)

```py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
```

- Specifies the use of `python3`.
- Supports `UTF-8` encoding.

<br>

```py
"""
L6 — Still image smoke test (Coral TPU)
...
"""
```

This Docstring is very important because it:
- Explains the purpose of the script.
- Provides usage instructions (CLI).
- Serves as a help message when arguments are missing.

<br>

Execution Example:

```sh
python3 detect_people_tpu_image.py model.tflite image.jpg 0.5
```

---

## 2. Imports

```py
from __future__ import annotations
```

- Used for type hints with forward references (modern Python style).

<br>

```py
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import time
```

- `sys` : Receives arguments from the command line.
- `Path` : Checks if files exist.
- `numpy` : Manages image data.
- `PIL.Image` : Loads/resizes images.
- `time` : Measures inference time.

<br>

```py
from tpu_common import make_interpreter, set_input, get_detections, count_people
```

The **tpu_common.py** file is the core of the Coral TPU logic, such as:
- Loading the Edge TPU delegate.
- Formatting input tensors.
- Converting output tensors for object detection.

---

## 3. `main()` function

### 3.1 Argument Validation

```py
if len(sys.argv) < 3:
    print(__doc__.strip())
    sys.exit(2)
```

Requires at least:
- model
- image

If it's incomplete, show the instructions and exit.

<br>

### 3.2 Reading Arguments

```py
model_path = sys.argv[1]
img_path = sys.argv[2]
thresh = float(sys.argv[3]) if len(sys.argv) >= 4 else 0.5
```

- **model_path** : EdgeTPU model (*.tflite).
- **img_path** : Input image.
- **thresh** : Confidence threshold (default value = 0.5).

<br>

### 3.3 File Existence 

```py
if not Path(model_path).exists():
    raise SystemExit(f"Model not found: {model_path}")
```

Prevents errors from the start.

---

## 4. Loading the Interpreter (Edge TPU)

```py
interp = make_interpreter(model_path)
```

Inside **tpu_common.make_interpreter()**, it typically:
- Loads **tflite_runtime.Interpreter**.
- Binds the **Edge TPU delegate** (libedgetpu.so).
- Executes **allocate_tensors()**.

From this point forward, inference will run on the actual TPU.

---

## 5. Checking the Model's Input Shape

```py
in_detail = interp.get_input_details()[0]
_, ih, iw, ic = in_detail["shape"]
```

For SSD MobileNet, the result will be `[1, height, width, channels]`

<br>

```py
if ic != 3:
    raise SystemExit(f"Expected 3-channel input, got {ic}")
```

Prevents the use of incompatible models (must be RGB only).

---

## 6. Image Loading and Preparation

```py
img = Image.open(img_path).convert("RGB")
```

- Loads the **image**.
- Forces conversion to **RGB**.

<br>

```py
img_resized = img.resize((iw, ih), Image.BILINEAR)
```

- Resizes the image to match the model's input dimensions.
- Uses `BILINEAR` interpolation (suitable for image inference).

<br>

```py
img_np = np.asarray(img_resized, dtype=np.uint8)
```

- Converts the image into a **NumPy array**.
- Uses **uint8** (matches the requirements of a quantized model).

---

## 7. Feeding Data into the Model

```py
set_input(interp, img_np)
```

Inside **set_input()**, it typically:
- Inserts the data into **tensor index 0**.
- **Reshapes** or **expands the batch dimension** if necessary.

---

## 8. Running Inference + Measuring Time

```py
t0 = time.time()
interp.invoke()
dt = (time.time() - t0) * 1000.0
```

- **interp.invoke()** : Runs on the Edge TPU.
- **dt** : Inference time in milliseconds (ms).

> This serves as a validation that the **Edge TPU** is active, achieving an exceptionally fast inference time—typically within the **3–10 ms range**.

---

## 9. Extracting Detection Results

```py
dets = get_detections(interp, score_thresh=thresh)
```

- Read the **output tensors** (boxes, classes, scores, count).
- Filter them based on the **score_thresh**.
- Convert them into objects, such as: `Detection(box, klass, score)`

---

## 10. Counting “People”

```py
people = count_people(dets, person_class=0)
```

- In the COCO dataset: `class_id = 0` is person
- This function loops through the detections to check the class and increment the count.

---

## 11. Displaying Results

```py
print(f"OK inference: {dt:.2f} ms  detections: {len(dets)}  people: {people}")
```

Displays:
- Inference time.
- Total number of objects.
- Number of people.

<br>

```py
for i, d in enumerate(dets[:20]):
    y1,x1,y2,x2 = d.box
```

Displays details for each detection:
- Class ID.
- Score.
- Bounding box (normalized 0–1).

---

## 12. Entry point

```py
if __name__ == "__main__":
    main()
```

Enables:
- Running as a **standalone script**.
- Importing for use in **other modules**.

---