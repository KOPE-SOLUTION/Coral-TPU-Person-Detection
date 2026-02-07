# 2-Install-coral-driver-libedgetpu--check-coral

## 2.1 Connect Coral TPU and Verify Hardware Recognition

Run the following command to check if the system detects the USB Accelerator:

```bash
lsusb | grep -i -E "google|coral|unichip" || lsusb
```

Commonly identified as:
- `Google Inc. 18d1:9302`
- `Global Unichip Corp`. (This often appears before the driver is initialized or during specific states).

<details>
<summary>Actual Environment Check</summary>
<br>

```sh
solokope@raspberrypi:~ $ lsusb | grep -i -E "google|coral|unichip" || lsusb
Bus 002 Device 002: ID 1a6e:089a Global Unichip Corp.
```

</details>

---

## 2.2 Add Coral Repository and Install `libedgetpu`

```bash
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg |   sudo gpg --dearmor -o /usr/share/keyrings/coral-edgetpu.gpg

echo "deb [signed-by=/usr/share/keyrings/coral-edgetpu.gpg] https://packages.cloud.google.com/apt coral-edgetpu-stable main" |   sudo tee /etc/apt/sources.list.d/coral-edgetpu.list

sudo apt update
sudo apt install -y libedgetpu1-std
# Optional: For maximum frequency mode (Higher performance but gets hotter):
# sudo apt install -y libedgetpu1-max
```

<details>
<summary>Actual Environment Check</summary>
<br>

```sh
solokope@raspberrypi:~ $ curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg |   sudo gpg --dearmor -o /usr/share/keyrings/coral-edgetpu.gpg


solokope@raspberrypi:~ $ echo "deb [signed-by=/usr/share/keyrings/coral-edgetpu.gpg] https://packages.cloud.google.com/apt coral-edgetpu-stable main" |   sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
deb [signed-by=/usr/share/keyrings/coral-edgetpu.gpg] https://packages.cloud.google.com/apt coral-edgetpu-stable main


solokope@raspberrypi:~ $ sudo apt update
Hit:1 http://security.debian.org/debian-security bullseye-security InRelease
Hit:2 http://deb.debian.org/debian bullseye InRelease
Hit:3 http://deb.debian.org/debian bullseye-updates InRelease
Get:4 https://packages.cloud.google.com/apt coral-edgetpu-stable InRelease [1,423 B]
Hit:5 http://archive.raspberrypi.org/debian bullseye InRelease
Get:6 https://packages.cloud.google.com/apt coral-edgetpu-stable/main all Packages [1,865 B]
Get:7 https://packages.cloud.google.com/apt coral-edgetpu-stable/main arm64 Packages [6,381 B]
Get:8 https://packages.cloud.google.com/apt coral-edgetpu-stable/main armhf Packages [6,379 B]
Fetched 16.0 kB in 1s (13.4 kB/s)
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
All packages are up to date.


solokope@raspberrypi:~ $ sudo apt install -y libedgetpu1-std
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following NEW packages will be installed:
  libedgetpu1-std
0 upgraded, 1 newly installed, 0 to remove and 0 not upgraded.
Need to get 341 kB of archives.
After this operation, 1,157 kB of additional disk space will be used.
Get:1 https://packages.cloud.google.com/apt coral-edgetpu-stable/main arm64 libedgetpu1-std arm64 16.0 [341 kB]
Fetched 341 kB in 1s (455 kB/s)
Selecting previously unselected package libedgetpu1-std:arm64.
(Reading database ... 40153 files and directories currently installed.)
Preparing to unpack .../libedgetpu1-std_16.0_arm64.deb ...
Unpacking libedgetpu1-std:arm64 (16.0) ...
Setting up libedgetpu1-std:arm64 (16.0) ...
Processing triggers for libc-bin (2.31-13+rpt2+rpi1+deb11u13) ...
```

</details>

---

## 2.3 Verify Runtime Library Path

Ensure the dynamic linker can locate the Edge TPU library correctly.

```bash
ldconfig -p | grep edgetpu
```

**Expected Result**: The output should point to the AArch64 (64-bit) library path as follows:

```
libedgetpu.so.1 (libc6,AArch64) => /usr/lib/aarch64-linux-gnu/libedgetpu.so.1
```

<details>
<summary>Actual Environment Check</summary>
<br>

```sh
solokope@raspberrypi:~ $ ldconfig -p | grep edgetpu
        libedgetpu.so.1 (libc6,AArch64) => /lib/aarch64-linux-gnu/libedgetpu.so.1
```

</details>

---