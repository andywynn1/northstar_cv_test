# northstar_cv_test

Runs the sp_vision_25 YOLOv5 armor-plate detector on a USB camera, a video
file, or a stream, and draws the detections. Works on Windows and Linux with
Python and one pip install. No Docker and no compiling.

Detector and model adapted from TongjiSuperPower/sp_vision_25 (MIT).

## Windows

1. Install Python 3.10, 3.11 or 3.12 and Git. In PowerShell:

       winget install -e --id Python.Python.3.12
       winget install -e --id Git.Git

   Close PowerShell and open a new one.

2. Get the code and install the packages:

       git clone https://github.com/andywynn1/northstar_cv_test.git
       cd northstar_cv_test
       py -m venv .venv
       .venv\Scripts\activate
       pip install -r requirements.txt

   If activation is blocked, run
   `Set-ExecutionPolicy -Scope Process Bypass` and activate again.

3. Plug in the camera and run:

       python run_camera.py 0

   A window opens with the camera image and green boxes around armor plates.
   Press q in the window to quit. If camera 0 is the laptop's built-in camera,
   try `python run_camera.py 1`.

## Linux

    sudo apt install -y git python3 python3-venv python3-pip
    git clone https://github.com/andywynn1/northstar_cv_test.git
    cd northstar_cv_test
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python run_camera.py 0

To see which camera number to use, run `ls /dev/video*`. Many cameras list
two entries (video0 and video1). Use the lower number.

## Other inputs

    python run_camera.py clip.mp4                 # a video file
    python run_camera.py http://host:8080/video   # a network stream
    python run_camera.py 0 --no-display           # print results, no window

Options: `--model PATH` to use different weights, `--device GPU` on a machine
with an Intel GPU.

## Troubleshooting

- `Cannot open source`: wrong camera number, or another app (Zoom, a browser
  tab) is using the camera. Close it and retry.
- `No module named openvino` or `cv2`: the virtual environment is not active.
  Activate it (step 2 on Windows, the `source` line on Linux) and retry.
- `pip install` cannot find openvino: use Python 3.10 to 3.12.
- No boxes on a webcam: webcams use auto-exposure and a different image than
  the robot camera the model was tuned for. Try a recorded clip first.

## Files

- `run_camera.py`: opens the camera and shows detections
- `detect.py`: the detector (preprocessing, OpenVINO inference, decoding)
- `models/`: yolov5.xml and yolov5.bin (OpenVINO format)
