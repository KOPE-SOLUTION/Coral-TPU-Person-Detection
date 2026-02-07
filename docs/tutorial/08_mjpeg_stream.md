# 8 — Browser-Based MJPEG Stream

![images](images/L8.gif)

**Objective**: View real-time AI inference directly via a **Web Browser**. This eliminates the need for a GUI on the Raspberry Pi. You can access the feed from any device on the same network at: `http://<PI-IP>:8080/`.

<br>

## Required Files
- `tpu_common.py` (Utility script)
- `stream_people_tpu_mjpeg.py` (Flask-based streaming script)

<br>

## Input Parameters
- **Model**: `_edgetpu.tflite`
- **Camera Index**: (e.g., `0`)
- **Threshold**: (e.g., `0.5`)
- **Resolution**: Width and Height (e.g., `640 480`)
- **Port**: (e.g., `8080`)

<br>

## Output
- Active Flask server providing an endpoint for the stream.
- Web Interface + `/video` endpoint (MJPEG).

<br>

## Execution Command

```bash
cd ~/hazard

# Syntax: python3 <script> <model> <cam_idx> <thresh> <width> <height> <port>
python3 ./stream_people_tpu_mjpeg.py \
  ./models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite \
  0 0.5 640 480 
  
# solokope@raspberrypi:~/hazard $ python3 ./stream_people_tpu_mjpeg.py   ./models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite   0 0.5 640 480 8080
# [ WARN:0] global ../modules/videoio/src/cap_gstreamer.cpp (501) isPipelinePlaying OpenCV | GStreamer warning: GStreamer: pipeline have not been created
# Starting MJPEG stream on 0.0.0.0:8080
# Open: http://<PI-IP>:8080/
#  * Serving Flask app 'stream_people_tpu_mjpeg'
#  * Debug mode: off
# WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
#  * Running on all addresses (0.0.0.0)
#  * Running on http://127.0.0.1:8080
#  * Running on http://192.168.1.125:8080
# Press CTRL+C to quit
# 192.168.1.110 - - [06/Feb/2026 17:02:13] "GET / HTTP/1.1" 200 -
# 192.168.1.110 - - [06/Feb/2026 17:02:14] "GET /video HTTP/1.1" 200 -
# ^Cterminate called without an active exception
# Aborted
# solokope@raspberrypi:~/hazard $ 
```

**Access on PC/Mobile**: Simply open your browser and enter: `http://<PI-IP>:8080/`

<br>

## Troubleshooting
- **Cannot Access Page**: Double-check your Pi's IP address. `bash hostname -I`
- **Port Conflict**: If port 8080 is already in use by another service, change the last argument to `8090` and run the command again.
- **Network/Firewall Issues**: Ensure your viewing device (Laptop/Smartphone) is connected to the same Local Area Network (LAN) or Wi-Fi as the Raspberry Pi.

---

## Production Mindset Tip
This MJPEG streaming method is the gold standard for **Headless Edge AI**. It consumes far less overhead than a Remote Desktop (VNC) and allows multiple people to view the detection results simultaneously without installing extra software on the client-side.

---