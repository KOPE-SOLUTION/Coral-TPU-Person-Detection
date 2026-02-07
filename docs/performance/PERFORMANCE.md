# Performance

This document help to helps to systematically measure performance (FPS / Latency / CPU / Temp)

## Recommended metrics

- **FPS (end-to-end)**: Averaged from the number of frames processed per second.
- **Inference latency (ms)**: When invoking TPU (if possible)
- **CPU usage**: %CPU 0f the process (Pi will show the effect clearly)
- **Temperature / Throttling**: Check the CPU temperature to see if it's being slowed down.

## Quick benchmark (headless)

Run L7 and check the FPS/People count.

```bash
python3 src/detect_people_tpu_cam_headless.py models/<model> 0 0.5 640 480
```

## Test Results Table Template

| Device | OS | Model | Input WxH | FPS | TPU Latency (ms) | CPU % | Temp (°C) | Notes |
|---|---|---|---:|---:|---:|---:|---:|---|
| Raspberry Pi 3B+ | Bullseye 64-bit | ssd_mobilenet_v2_coco..._edgetpu.tflite | 640×480 |  |  |  |  |  |
| Raspberry Pi 4 | Bullseye 64-bit |  |  |  |  |  |  |  |

## Tips

- Use **Raspberry Pi OS 64-bit** and install the runtime as recommended in the documentation.
- If FPS drops after prolonged use, check the temperature and allow for colling.
- Reducing the input size or camera resolution will help incrase FPS.
