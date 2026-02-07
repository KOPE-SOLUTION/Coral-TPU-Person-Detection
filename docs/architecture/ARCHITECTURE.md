# Architecture

This projet is an example of **Person Detection (SSD/COCO) บน Raspberry Pi + Coral USB Edge TPU**  .
Focus on practical use: headless camera, MJPEG stream, and event recording via Flask.

## High-level

```mermaid
flowchart LR
    CAM[USB Camera] -->|frames| APP[Python App<br/>OpenCV + TFLite Runtime]
    APP -->|delegate| TPU[Coral USB Edge TPU]
    APP -->|MJPEG / HTTP| WEB[Browser / Client]
    APP -->|snapshots| OUT[Local Storage<br/>out/]
```

## Components

- **OpenCV**: Reads images from the camera + draws a frame + encodes JPEG.
- **TFLite Runtime + EdgeTPU delegate**. Runs the `_edgetpu.tflite` model on the TPU.
- **Flask**:
  - `L8` MJPEG stream (live view)
  - `L9` adds status, snapshot, and event gallery

## Runtime modes

1) **L6 Still image**  
Read images files → detect → save/output

2) **L7 Headless camera**  
Read from USB camera → detect → print counts (Suitable for performance testing.)

3) **L8 MJPEG stream**  
You can watch the live stream immediately via the website (LAN)

4) **L9 Events**  
Capture snapshots based on specified conditions (e.g., detect a person and record it) + view past records.

## Data flow (detail)

```mermaid
sequenceDiagram
    participant C as Camera
    participant A as App (OpenCV)
    participant T as EdgeTPU (Delegate)
    participant W as Web (Browser)
    C->>A: frame (BGR)
    A->>A: resize/normalize (model input)
    A->>T: invoke(model)
    T-->>A: detections (boxes/classes/scores)
    A->>A: draw/encode JPEG
    A-->>W: MJPEG stream / HTML
    A->>A: save snapshot (optional)
```
