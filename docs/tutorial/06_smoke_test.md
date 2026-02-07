# 6 Still Image Test (Smoke Test)

**Objective**: Confirm that the system can:

- Successfully load the `libedgetpu` delegate.
- Load the compiled `_edgetpu.tflite` model.
- Perform inference on a still image and successfully detect a "person."

<br>

## Required Files
- `tpu_common.py` (Utility script)
- `detect_people_tpu_image.py` (Main inference script)

<br>

## Input Requirements
- **Model**: `*_edgetpu.tflite` (Your compiled model)
- **Image**: `input.jpg` (Use any standard image containing people for testing)

<br>

## Output Expectations
- The console will display the **inference time** and the **number of detections**.
- (Depending on script configuration) An output image may be saved with drawn bounding boxes.

<br>

## Execution Command

```bash
cd ~/hazard

# Syntax: python3 <script> <model_path> <image_path> <threshold>
python3 ./detect_people_tpu_image.py \
  ./models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite \
  ./input.jpg \
  0.5
```

<br>

## Expected Result

If everything is configured correctly, you should see an output similar to this:

```sh
solokope@raspberrypi:~/hazard $ python3 ./detect_people_tpu_image.py   ./models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite   ./input.jpg   0.5
OK inference: 37.71 ms  detections: 1  people: 1
- id=00 class=0 score=0.95 box(ymin,xmin,ymax,xmax)=(0.042,0.205,0.992,0.829)
```
<br>

## Troubleshooting

- **Delegate Errors**: If you see errors regarding the "Failed to load delegate," go back to **section 5.2** to check user permissions and library paths.
- **Model Compatibility**: If the error states "Model not compiled for Edge TPU," ensure you are using the file that ends specifically with **_edgetpu.tflite** (the one compiled via WSL2 in **section 4**).
- **Performance Note**: The first inference might be slightly slower due to hardware initialization, but subsequent runs should remain consistently fast (approx. 10–40ms for MobileNet V2).

---