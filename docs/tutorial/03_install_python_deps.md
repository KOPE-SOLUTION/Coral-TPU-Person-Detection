# 3 Installing-python-libs

## 3.0 Create Project Directory

Set up a structured workspace for your scripts, AI models, and output data.

```bash
mkdir -p ~/hazard/{models,out}
cd ~/hazard
```

---

## 3.1 Python Libraries Installation

Since we are using **Raspberry Pi OS Bullseye**, we will leverage system-level packages (`apt`) to ensure maximum stability and compatibility with the hardware.

### 3.1.1 Install `tflite_runtime` (Crucial)

Instead of compiling from source, we use the optimized `apt` package provided specifically for this OS version.

```bash
sudo apt install -y python3-tflite-runtime python3-numpy python3-pil
python3 -c "import tflite_runtime; print('tflite_runtime OK', tflite_runtime.__file__)"
```

<details>
<summary>Actual Environment Check</summary>
<br>

```sh
solokope@raspberrypi:~/hazard $ python3 -c "import tflite_runtime; print('tflite_runtime OK', tflite_runtime.__file__)"
tflite_runtime OK /usr/lib/python3/dist-packages/tflite_runtime/__init__.py
```

</details>

---

### 3.1.2 Install OpenCV

We install the system-wide OpenCV package to ensure it correctly links with the Raspberry Pi's hardware-accelerated media libraries.

```bash
sudo apt install -y python3-opencv
python3 -c "import cv2; print('cv2 OK', cv2.__version__)"
```

<details>
<summary>Actual Environment Check</summary>
<br>

```sh
solokope@raspberrypi:~/hazard $ python3 -c "import cv2; print('cv2 OK', cv2.__version__)"
cv2 OK 4.5.1
```

</details>

---

### 3.1.3 Install Flask

```bash
python3 -m pip install --upgrade pip
python3 -m pip install flask
python3 -c "import flask; print('flask OK', flask.__version__)"
```

```bash
solokope@raspberrypi:~/hazard $ python3 -c "import flask; print('flask OK', flask.__version__)"
<string>:1: DeprecationWarning: The '__version__' attribute is deprecated and will be removed in Flask 3.2. Use feature detection or 'importlib.metadata.version("flask")' instead.
flask OK 3.1.2
```

---

# Why use apt instead of pip for TFLite and OpenCV?
On Raspberry Pi OS, packages installed via `sudo apt install` are pre-compiled specifically for the ARM architecture. This prevents "Illegal Instruction" errors and segmentation faults that frequently occur when `pip` attempts to install generic binary wheels that may not be fully compatible with the Pi's specific hardware configuration.

---