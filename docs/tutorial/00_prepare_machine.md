# 0 : Prepare machine flash os check specks

## 0.1 OS Selection

**Recommended:** Raspberry Pi OS **Bullseye 64-bit** (aarch64)  
**Reason**: It comes with Python 3.9 + `python3-tflite-runtime` (via apt), which significantly reduces dependency conflicts and segmentation fault (segfault) issues.

You can download the `.img.xz` file directly (Manual). The **Lite version** (no Desktop) is highly recommended for Coral TPU deployments.

**Direct Download**: [Raspberry Pi OS Lite (64-bit) – Bullseye](https://downloads.raspberrypi.com/raspios_lite_arm64/images/)

**Target Image Version**: Look for a folder similar to: `2023-02-21-raspios-bullseye-arm64-lite.img.xz`

Desktop (Optional, but not recommended): [Download Link](https://downloads.raspberrypi.com/raspios_arm64/images/)

[Reference : 6 main reasons why we recommend Raspberry Pi OS Lite (no desktop)](../reference/raspberrypi_os_lite_reasons.md)

### Flashing a 32GB SD Card with Raspberry Pi Imager

1. **Prerequisites**
    - 32GB SD Card (Class 10 / U1 or higher)
    - SD Card Reader
    - PC / Laptop (Windows / macOS / Linux)

2. **Download & Install**: Get the [Raspberry Pi Imager](https://www.raspberrypi.com/software/) and install it on your computer.

3. **Configuration**: Plug in the SD Card and open Raspberry Pi Imager.
    - **Step A: Choose OS**
        - Select **"Use custom"**
        - Select the downloaded file: `2023-02-21-raspios-bullseye-arm64-lite.img.xz`
        - (Note: Do not extract the file; the .img.xz format is ready for flashing.)

    - **Step B: Choose Storage**
        - Select your 32GB SD Card. `Verify carefully to ensure you don't select the wrong HDD/SSD`.

4. **Write**: Click **Write** and wait for the process to complete.

---

## 0.2 Post-Flash & First Boot: System 

Run the following commands to verify your hardware and OS specifications:

```bash
cat /proc/cpuinfo | sed -n '1,30p'
free -h
uname -a
lsb_release -a || cat /etc/os-release
df -h
python3 --version
```

Expected Output Checklist:
- **Architecture**: `aarch64`
- **Python Version**: `Approximately 3.9.x`
- **Storage**: Sufficient free space (recommended > 8GB remaining)

<details>
<summary>Actual Environment Check</summary>
<br>

```sh
solokope@raspberrypi:~ $ cat /proc/cpuinfo | sed -n '1,30p'
processor       : 0
BogoMIPS        : 108.00
Features        : fp asimd evtstrm crc32 cpuid
CPU implementer : 0x41
CPU architecture: 8
CPU variant     : 0x0
CPU part        : 0xd08
CPU revision    : 3

processor       : 1
BogoMIPS        : 108.00
Features        : fp asimd evtstrm crc32 cpuid
CPU implementer : 0x41
CPU architecture: 8
CPU variant     : 0x0
CPU part        : 0xd08
CPU revision    : 3

processor       : 2
BogoMIPS        : 108.00
Features        : fp asimd evtstrm crc32 cpuid
CPU implementer : 0x41
CPU architecture: 8
CPU variant     : 0x0
CPU part        : 0xd08
CPU revision    : 3

processor       : 3
BogoMIPS        : 108.00
Features        : fp asimd evtstrm crc32 cpuid
```

```sh
solokope@raspberrypi:~ $ free -h
               total        used        free      shared  buff/cache   available
Mem:           7.6Gi        98Mi       6.1Gi       1.0Mi       1.4Gi       7.4Gi
Swap:           99Mi          0B        99Mi
```


```sh
solokope@raspberrypi:~ $ lsb_release -a || cat /etc/os-release
No LSB modules are available.
Distributor ID: Debian
Description:    Debian GNU/Linux 11 (bullseye)
Release:        11
Codename:       bullseye
```

```sh
solokope@raspberrypi:~ $ df -h
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        29G  1.8G   26G   7% /
devtmpfs        3.7G     0  3.7G   0% /dev
tmpfs           3.9G     0  3.9G   0% /dev/shm
tmpfs           1.6G  1.3M  1.6G   1% /run
tmpfs           5.0M  4.0K  5.0M   1% /run/lock
/dev/mmcblk0p1  255M   31M  225M  13% /boot
tmpfs           782M     0  782M   0% /run/user/1000
```

```sh
solokope@raspberrypi:~ $ python3 --version
Python 3.9.2
```

</details>

---