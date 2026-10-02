# northstar_cv_test

YOLOv5 armor detector plus a small camera demo, adapted from
TongjiSuperPower/sp_vision_25 (MIT). It reads frames from a USB camera, a
video file, or a network stream, and prints how many armor plates it finds.

Everything runs inside a Docker container, so the only thing you install on
the computer is Docker. The container holds all the dependencies (OpenCV,
OpenVINO 2024.6, and the rest).

Requirements:

- An x86_64 computer (normal Intel or AMD laptop or desktop). ARM machines,
  including Apple Silicon and Jetson, will not work with this Dockerfile.
- About 5 GB of free disk space and an internet connection for the first build.

## Linux

### 1. Install Docker (once)

Check the machine type. It must print x86_64:

    uname -m

Install Docker and let your user run it without sudo:

    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER

Log out and back in (or run `newgrp docker`), then check it works:

    docker run --rm hello-world

### 2. Get the code and build the container

    sudo apt install -y git
    git clone https://github.com/andywynn1/northstar_cv_test.git
    cd northstar_cv_test
    docker build -t northstar-cv .

The first build downloads Ubuntu, the dependencies and OpenVINO, then compiles
the code. It takes several minutes. Later builds are fast.

### 3. Run on a USB camera

Plug the camera in and list the video devices:

    ls /dev/video*

Many cameras show two entries (for example video0 and video1). Use the lower
number first. The commands below use video0. If yours is video2, replace
`/dev/video0` with `/dev/video2` and the final `0` with `2`.

With a preview window (press q in the window to quit):

    xhost +local:docker
    docker run --rm -it --device /dev/video0 \
      -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix \
      northstar-cv configs/default.yaml 0

Without a window (log lines in the terminal, and a picture with boxes saved to
out/latest.jpg every 15 frames; press Ctrl+C to stop):

    mkdir -p out
    docker run --rm --device /dev/video0 -v "$PWD/out:/app/out" \
      northstar-cv configs/default.yaml 0 --headless

### 4. Run on a video file instead

Put a clip at data/clip.mp4, then:

    mkdir -p data out
    docker run --rm -v "$PWD/data:/data" -v "$PWD/out:/app/out" \
      northstar-cv configs/default.yaml /data/clip.mp4 --headless

## Windows

Docker containers on Windows cannot see a USB webcam directly. For a live
camera you run a small streaming script on Windows, and the container reads
the stream. A video file needs no script.

### 1. Install the tools (once)

Open PowerShell and run:

    winget install -e --id Docker.DockerDesktop
    winget install -e --id Git.Git
    winget install -e --id Python.Python.3.12

Restart the computer. Start Docker Desktop from the Start menu, accept its
prompts (leave the WSL2 option on), and wait until it says it is running.
Virtualization must be enabled in the BIOS. Then open a new PowerShell window
and check:

    docker run --rm hello-world

### 2. Get the code and build the container

    git clone https://github.com/andywynn1/northstar_cv_test.git
    cd northstar_cv_test
    docker build -t northstar-cv .

The first build takes several minutes.

### 3. Run on a video file

Make a folder named data and put a clip at data\clip.mp4, then:

    mkdir data, out
    docker run --rm -v "${PWD}/data:/data" -v "${PWD}/out:/app/out" northstar-cv configs/default.yaml /data/clip.mp4 --headless

### 4. Run on a USB camera

Install the streamer's dependency (once):

    pip install opencv-python

Terminal 1: start the streamer. Windows may ask to allow network access, and
you should allow it on private networks. Leave this running:

    python scripts\stream_webcam.py 0

The number is the camera index. Try 1 if 0 is the laptop's built-in camera.
Check the stream first by opening http://localhost:8080/video in a browser.

Terminal 2: run the detector against the stream:

    mkdir out
    docker run --rm -v "${PWD}/out:/app/out" northstar-cv configs/default.yaml http://host.docker.internal:8080/video --headless

Open out\latest.jpg to see the boxes (it updates every 15 frames). Stop the
detector with Ctrl+C, then stop the streamer with Ctrl+C. The streamer listens
on the network while it runs, so do not leave it running.

## Config

configs/default.yaml holds the model path and thresholds. Keep
`device: CPU` unless the machine has an Intel GPU. If you edit the config or
code, rebuild with `docker build -t northstar-cv .`, or mount the config
folder when running: add `-v "$PWD/configs:/app/configs"` on Linux or
`-v "${PWD}/configs:/app/configs"` on Windows.

## Troubleshooting

- `permission denied` on the Docker socket (Linux): run the usermod command
  in step 1, then log out and back in.
- `error during connect` (Windows): Docker Desktop is not running. Start it.
- `Cannot open source` in the logs: the camera index is wrong, or another app
  (Zoom, a browser tab) has the camera open. Close it and retry.
- `exec format error` or a failed OpenVINO download: the computer is not
  x86_64.
- No window on Linux: use the headless command and open out/latest.jpg.
- Zero armors found: test with a recorded clip first. Webcams use
  auto-exposure, which washes out the armor lights, and the model was trained
  on the robot camera's image.

## Credits

Detector and model from TongjiSuperPower/sp_vision_25 (MIT). The model was
adapted by that team from other open-source RoboMaster detectors.
