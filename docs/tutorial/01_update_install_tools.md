# 1 Update--install-basic-tools

## 1.1 System Update

Before installing new software, synchronize your package index and upgrade existing packages to their latest versions.

```bash
sudo apt update
sudo apt -y upgrade
```

---

## 1.2 Essential Tools & Dependencies Installation

Install the core utilities, build tools, and libraries required for AI inference, Python environments, and media handling.

```bash
sudo apt install -y   git curl wget unzip   build-essential pkg-config   python3-venv python3-pip   libgl1 libglib2.0-0   libatlas-base-dev libopenblas-dev   v4l-utils
```

<br>

**Verifying USB Camera Connectivity**

Once the tools are installed, use the following commands to ensure the system recognizes your USB camera:

```bash
v4l2-ctl --list-devices
ls -l /dev/video*
```

<details>
<summary>Actual Environment Check</summary>
<br>

```sh
solokope@raspberrypi:~ $ v4l2-ctl --list-devices
bcm2835-codec-decode (platform:bcm2835-codec):
        /dev/video10
        /dev/video11
        /dev/video12
        /dev/video18
        /dev/video31
        /dev/media3

bcm2835-isp (platform:bcm2835-isp):
        /dev/video13
        /dev/video14
        /dev/video15
        /dev/video16
        /dev/video20
        /dev/video21
        /dev/video22
        /dev/video23
        /dev/media1
        /dev/media2

rpivid (platform:rpivid):
        /dev/video19
        /dev/media0

USB PHY 2.0: USB CAMERA (usb-0000:01:00.0-1.1):
        /dev/video0
        /dev/video1
        /dev/
```

```sh
solokope@raspberrypi:~ $ ls -l /dev/video*
crw-rw----+ 1 root video 81, 14 Feb  6 13:12 /dev/video0
crw-rw----+ 1 root video 81, 15 Feb  6 13:12 /dev/video1
crw-rw----+ 1 root video 81,  2 Feb  6 13:12 /dev/video10
crw-rw----+ 1 root video 81,  7 Feb  6 13:12 /dev/video11
crw-rw----+ 1 root video 81, 11 Feb  6 13:12 /dev/video12
crw-rw----+ 1 root video 81,  1 Feb  6 13:12 /dev/video13
crw-rw----+ 1 root video 81,  3 Feb  6 13:12 /dev/video14
crw-rw----+ 1 root video 81,  4 Feb  6 13:12 /dev/video15
crw-rw----+ 1 root video 81,  5 Feb  6 13:12 /dev/video16
crw-rw----+ 1 root video 81, 12 Feb  6 13:12 /dev/video18
crw-rw----+ 1 root video 81,  0 Feb  6 13:12 /dev/video19
crw-rw----+ 1 root video 81,  6 Feb  6 13:12 /dev/video20
crw-rw----+ 1 root video 81,  8 Feb  6 13:12 /dev/video21
crw-rw----+ 1 root video 81,  9 Feb  6 13:12 /dev/video22
crw-rw----+ 1 root video 81, 10 Feb  6 13:12 /dev/video23
crw-rw----+ 1 root video 81, 13 Feb  6 13:12 /dev/video31
```

</details>

---