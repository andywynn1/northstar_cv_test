"""Read frames from a camera, video file or stream URL and detect armor plates.

Examples:
    python run_camera.py            # camera 0
    python run_camera.py 1          # camera 1
    python run_camera.py clip.mp4   # video file
"""
import argparse
import sys
import time

import cv2

from detect import MODEL_PATH, ArmorDetector, draw


def open_source(source):
    if source.isdigit():
        backend = cv2.CAP_DSHOW if sys.platform.startswith("win") else cv2.CAP_ANY
        return cv2.VideoCapture(int(source), backend)
    return cv2.VideoCapture(source)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("source", nargs="?", default="0", help="camera index, video file, or URL")
    parser.add_argument("--model", default=str(MODEL_PATH), help="path to yolov5.xml")
    parser.add_argument("--device", default="CPU", help="OpenVINO device (CPU, GPU)")
    parser.add_argument("--no-display", action="store_true", help="print results instead of showing a window")
    args = parser.parse_args()

    cap = open_source(args.source)
    if not cap.isOpened():
        sys.exit(f"Cannot open source: {args.source}")

    detector = ArmorDetector(args.model, args.device)
    last = time.perf_counter()

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        armors = detector.detect(frame)

        now = time.perf_counter()
        fps = 1.0 / max(now - last, 1e-6)
        last = now

        if args.no_display:
            print(f"{len(armors)} armors, {fps:.1f} fps", flush=True)
            continue

        draw(frame, armors)
        cv2.putText(frame, f"{fps:.1f} fps", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        cv2.imshow("northstar_cv_test (press q to quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
