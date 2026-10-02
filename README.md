# northstar_cv_test

YOLOv5 armor detector and a camera demo, adapted from
TongjiSuperPower/sp_vision_25 (MIT). Detects armor plates in frames from a
camera index or a video file.

## Run on Linux (x86_64) with Docker

    docker build -t northstar-cv .

Webcam with a preview window:

    xhost +local:docker
    docker run --rm -it --device /dev/video0 \
      -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix \
      northstar-cv configs/default.yaml 0

Video file, no window (put the clip in ./data):

    docker run --rm -v "$PWD/data:/data" northstar-cv \
      configs/default.yaml /data/clip.mp4 --headless

## Run on Windows

Docker Desktop containers cannot see a webcam by default. Either run the
video-file command above (PowerShell: `-v ${PWD}/data:/data`), or use WSL2
Ubuntu and follow the Linux steps.

## Config

`configs/default.yaml` holds the model path and thresholds. Set
`device: CPU` unless the machine has an Intel GPU.
