# 4 Compile Edge TPU Model on PC (Windows + WSL2)

## 4.1 Prepare Workspace (WSL2)

Create a dedicated folder for your Coral model processing.

```bash
mkdir -p ~/coral_h32 && cd ~/coral_h32
sudo apt update
sudo apt install -y wget unzip
```

---

## 4.2 Compile TensorFlow Lite Model for Edge TPU

> Note: For a library of pre-compiled models, visit the [Official Google Coral Models](https://coral.ai/models/) page.


The following steps demonstrate how to download a quantized model and compile it specifically for the Edge TPU using the `edgetpu_compiler`.

```bash
wget https://github.com/google-coral/test_data/raw/master/ssd_mobilenet_v2_coco_quant_postprocess.tflite
edgetpu_compiler -s ssd_mobilenet_v2_coco_quant_postprocess.tflite

ls -lh
```

Success Criteria: You should see a new file named: `ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite`

---

## 4.3 Transfer Compiled Model to Raspberry Pi

Use `scp` (Secure Copy) to transfer the compiled model from your PC to the models folder on your Raspberry Pi.

```bash
scp ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite   solokope@<PI-IP>:/home/solokope/hazard/models/
```

<details>
<summary>Actual Environment Check</summary>
<br>

```sh
solokope@kopesolution0:~/coral_h32$ scp ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite   solokope@192.168.1.125:
/home/solokope/hazard/models/
solokope@192.168.1.125's password:
ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite                                100% 6750KB  47.1MB/s   00:00
```

</details>

---