# 9 Stream + Events (Recording & Event History)

![images](images/L9.gif)

**Objective**: Expand the live stream capabilities to include event logging and automated snapshots:
- `/status`: Real-time summary of FPS, inference time, and latest person count.
- `/snapshot`: Manual trigger to capture a high-quality frame when a person is detected.
- `/events`: A dedicated page listing all archived detection images.
- **Auto-Save**: Automatically save snapshots to the `out/` folder when detection criteria are met.

<br>

## Required Files
- `tpu_common.py`(Core utilities)
- `stream_people_tpu_events.py` (Advanced streaming & event server)

<br>

## Input Parameters
- **Model**: `_edgetpu.tflite`
- **Camera Index**: (e.g., `0`)
- **Threshold**: Confidence level (e.g., `0.5`)
- **Resolution**: Width & Height (e.g., `640 480`)
- **Port**: Web server port (e.g., `8080`)
- **Output Directory**: Storage path (e.g., `./out`)
- **Cooldown**: Minimum interval between snapshots in seconds (e.g., `2`) to prevent duplicate captures of the same event.

<br>

## Output
- **Flask server**:
  - `/` : Live monitoring dashboard.
  - `/video` : Raw MJPEG stream.
  - `/status` : Diagnostic data (JSON format).
  - `/snapshot` : Capture and redirect to the latest image.
  - `/events` : Gallery view of all saved detections.
  - `/out/<filename>.jpg` : Static file server for archived images.
- **File System**: Automated image logging within the `out/` directory.

<br>

## Execution Command

```bash
cd ~/hazard
mkdir -p out

# Syntax: python3 <script> <model> <cam> <thresh> <w> <h> <port> <outdir> <cooldown>
python3 ./stream_people_tpu_events.py \
  ./models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite \
  0 0.5 640 480 8080 ./out 2
```

**Access URLs**:
- Dashboard: `http://<PI-IP>:8080/`
- Event Log: `http://<PI-IP>:8080/events`
- System Status: `http://<PI-IP>:8080/status`

**Verify Saved Files**:
```bash
ls -lh ~/hazard/out | tail
```

<br>

## Troubleshoot

1. **HTML/CSS Errors** (`KeyError: 'font-family'`): This usually happens if the HTML template uses curly braces `{}` that conflict with Python's `.format()` method.

    Fix: Escape the CSS curly braces by doubling them (`{{` and `}}`) in your Python string template.


2. **Core Dump on Exit (Ctrl+C)**: Sometimes OpenCV or Flask background threads don't terminate cleanly.

    Fix: For production, we recommend running the script as a systemd service or ensuring your code includes a `try/finally` block to properly call `camera.release()`.

---