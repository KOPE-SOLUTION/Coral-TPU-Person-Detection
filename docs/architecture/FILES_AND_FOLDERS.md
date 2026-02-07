# Files and folders

```
.
├─ src/                     # Example Python code (L6-L9)
│  ├─ tpu_common.py         # helper for TFLite + EdgeTPU + SSD postprocess
│  ├─ detect_people_tpu_image.py
│  ├─ detect_people_tpu_cam_headless.py
│  ├─ stream_people_tpu_mjpeg.py
│  └─ stream_people_tpu_events.py
├─ docs/
│  ├─ tutorial/             # Step-by-step guide (00-09)
│  ├─ architecture/
│  ├─ performance/
│  ├─ demos/                # Demo GIFs (Used in the README)
│  ├─ assets/               # Sample image/file
│  └─ reference/            # Supplementary documents
├─ scripts/
│  └─ download_models.sh    # helper script (template)
├─ requirements.txt
└─ README.md
```

## Notes

- The `models/` folder is not tracked by default (to prevent large repositories). Create it yourself and add the `_edgetpu.tflite` model file to it.
- The output folder, such as `out/`, should be ignored.
