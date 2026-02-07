#!/usr/bin/env bash
set -euo pipefail

# Download Coral EdgeTPU-ready TFLite models into ./models
# Notes:
# - Model URLs can change. If a download fails, use the official Coral Model Zoo.
# - Keep models out of git by default (see .gitignore).

mkdir -p models
cd models

echo "Place your *_edgetpu.tflite models in ./models"
echo "Example filenames used in docs:"
echo "  ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite"
