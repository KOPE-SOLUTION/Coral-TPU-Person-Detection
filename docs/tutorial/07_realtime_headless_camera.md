# 7 Real-time USB Inference (Headless Mode).

**Objective**: Perform real-time AI inference from a camera feed **without a GUI**. This method is optimized for Raspberry Pi OS Lite, SSH sessions, and headless production environments.

## Required Files
- `tpu_common.py` (Utility script)
- `detect_people_tpu_cam_headless.py` (Headless inference script)

<br>

## Input Parameters

- **Model**: `*_edgetpu.tflite`
- **Camera Index**: (e.g., `0` for `/dev/video0`)
- **Threshold**: Confidence score (e.g., `0.5`)
- **Resolution**: Capture width and height (e.g., `640 480`)

<br>

## Output
- Real-time logs showing **FPS, Average Inference Time**, and **Frame Count** (total vs. people detected).
- No display window is created, saving significant system resources.

<br>

## Execution Command

```bash
cd ~/hazard
python3 ./detect_people_tpu_cam_headless.py \
  ./models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite \
  0 0.5 640 480
```

<br>

## Expected

```sh
solokope@raspberrypi:~/hazard $ python3 ./detect_people_tpu_cam_headless.py \
  ./models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite \
  0 0.5 640 480
[ WARN:0] global ../modules/videoio/src/cap_gstreamer.cpp (501) isPipelinePlaying OpenCV | GStreamer warning: GStreamer: pipeline have not been created
MODEL: ./models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite
CAM: /dev/video0  capture: 640x480  model_in: 300x300  thresh: 0.5
Headless mode: no GUI. Press Ctrl+C to stop.
FPS  11.7 | infer avg   18.1 ms | frames 12 | frames_with_people 12
FPS  23.7 | infer avg   15.1 ms | frames 24 | frames_with_people 24
FPS  23.1 | infer avg   14.9 ms | frames 24 | frames_with_people 24
FPS  23.2 | infer avg   14.6 ms | frames 24 | frames_with_people 24
FPS  24.1 | infer avg   14.5 ms | frames 25 | frames_with_people 21
FPS  22.6 | infer avg   16.2 ms | frames 23 | frames_with_people 2
FPS  24.1 | infer avg   17.9 ms | frames 25 | frames_with_people 0
FPS  23.2 | infer avg   18.1 ms | frames 24 | frames_with_people 0
FPS  23.4 | infer avg   15.3 ms | frames 24 | frames_with_people 0
FPS  24.1 | infer avg   14.7 ms | frames 25 | frames_with_people 0
FPS  22.2 | infer avg   14.4 ms | frames 23 | frames_with_people 9
FPS  23.2 | infer avg   14.4 ms | frames 25 | frames_with_people 25
FPS  23.8 | infer avg   14.8 ms | frames 24 | frames_with_people 24
^C
Stopping...
```

<br>

## Troubleshooting

1. **Verify Camera Hardware**: Ensure the Pi recognizes the camera.

```bash
v4l2-ctl --list-devices
ls -l /dev/video*
```

2. **Resource Conflict**: If the camera fails to open, ensure no other programs (like Motion or another script) are currently accessing `/dev/video0`. When in doubt, a `sudo reboot` usually clears the device lock.

3. **GStreamer Warnings**: If you see a warning like `GStreamer: pipeline have not been created` but the logs continue to scroll with FPS data, you can safely ignore it. OpenCV is simply falling back from GStreamer to the **4L2 (Video4Linux2)** backend, which is perfectly fine for this setup.

---

## Efficiency Note
By running in **Headless Mode**, the CPU does not have to render graphics or manage a desktop compositor. This allows the system to achieve higher FPS and lower inference latency, reaching the full potential of the Coral TPU.

---