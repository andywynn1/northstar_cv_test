"""Serve a webcam as an MJPEG stream at http://localhost:8080/video.

Usage (Windows): python scripts\stream_webcam.py [camera_index] [port]
Stop it with Ctrl+C when you are done. It listens on all network interfaces
so the Docker container can reach it, so do not leave it running.
"""
import sys

import cv2
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

index = int(sys.argv[1]) if len(sys.argv) > 1 else 0
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080

backend = cv2.CAP_DSHOW if sys.platform.startswith("win") else cv2.CAP_ANY
cap = cv2.VideoCapture(index, backend)
if not cap.isOpened():
    sys.exit(f"Cannot open camera {index}")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/video":
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
        self.end_headers()
        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                ok, jpg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if not ok:
                    continue
                data = jpg.tobytes()
                self.wfile.write(
                    b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: "
                    + str(len(data)).encode()
                    + b"\r\n\r\n"
                )
                self.wfile.write(data)
                self.wfile.write(b"\r\n")
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, *args):
        pass


print(f"Streaming camera {index} at http://localhost:{port}/video (Ctrl+C to stop)")
ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
