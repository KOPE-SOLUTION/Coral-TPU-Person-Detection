# L5 Pi-side Testing: Model & Delegate Verification

## 5.1 Verify Model Deployment

Ensure the compiled model was transferred correctly to your models directory.

```bash
ls -lh ~/hazard/models/
```

## 5.2 Test Hardware Delegate Loading

To run the Edge TPU without requiring `sudo` every time, your user must have the correct hardware permissions.

1. Update User Groups

Add your user to the groups responsible for USB devices and video hardware.
```sh
# Replace 'solokope' with your actual username if different
sudo usermod -aG plugdev solokope
sudo usermod -aG video solokope

# Reboot to apply group changes
sudo reboot
```

2. Verify Group Membership

After rebooting, log back in and check your active groups.

```sh
id

# solokope@raspberrypi:~ $ id
# uid=1000(solokope) gid=1000(solokope) groups=1000(solokope),4(adm),20(dialout),24(cdrom),27(sudo),29(audio),44(video),46(plugdev),60(games),100(users),104(input),106(render),108(netdev),997(gpio),998(i2c),999(spi)
```

3. Test Loading the Edge TPU Delegate

Test if Python can successfully communicate with the Coral TPU through the library.

```sh
python3 -c "from tflite_runtime.interpreter import load_delegate; d=load_delegate('libedgetpu.so.1'); print('delegate OK', d)"

# solokope@raspberrypi:~ $ python3 -c "from tflite_runtime.interpreter import load_delegate; d=load_delegate('libedgetpu.so.1'); print('delegate OK', d)"
# delegate OK <tflite_runtime.interpreter.Delegate object at 0x7fba0f7fa0>
```

**Troubleshooting**: If the command above fails to find the library, try using the **absolute path**:
```sh
python3 -c "from tflite_runtime.interpreter import load_delegate; print(load_delegate('/lib/aarch64-linux-gnu/libedgetpu.so.1'))"

# solokope@raspberrypi:~ $ python3 -c "from tflite_runtime.interpreter import load_delegate; print(load_delegate('/lib/aarch64-linux-gnu/libedgetpu.so.1'))"
# <tflite_runtime.interpreter.Delegate object at 0x7f93265fa0>
```

---

##  do we need a "Delegate"?
The Delegate acts as a bridge. By default, TensorFlow Lite runs on the CPU. By loading the **libedgetpu.so.1** delegate, you are telling the interpreter to offload mathematically heavy operations to the Coral TPU hardware, which is significantly faster and more efficient.

---