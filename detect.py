"""YOLOv5 armor-plate detector using OpenVINO.

Ported from sp_vision_25 (tasks/auto_aim/yolos/yolov5.cpp, MIT license).
"""
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import openvino as ov

INPUT_SIZE = 640
MODEL_PATH = Path(__file__).parent / "models" / "yolov5.xml"
NAMES = ["one", "two", "three", "four", "five", "sentry", "outpost", "base", "not_armor"]
COLOR_NAMES = {0: "blue", 1: "red"}  # any other id is "extinguish"


def armor_name(num_id):
    if num_id == 0:
        return "sentry"
    index = num_id if num_id > 5 else num_id - 1
    return NAMES[index] if 0 <= index < len(NAMES) else "not_armor"


@dataclass
class Armor:
    points: np.ndarray  # 4x2 corner points in image pixels
    name: str
    color: str
    kind: str  # "big" or "small"
    confidence: float


class ArmorDetector:
    def __init__(
        self,
        model_path=MODEL_PATH,
        device="CPU",
        score_threshold=0.7,
        nms_threshold=0.3,
        min_confidence=0.8,
    ):
        core = ov.Core()
        model = core.read_model(str(model_path))
        self.compiled = core.compile_model(model, device)
        self.output = self.compiled.output(0)
        self.score_threshold = score_threshold
        self.nms_threshold = nms_threshold
        self.min_confidence = min_confidence

    def detect(self, bgr):
        h, w = bgr.shape[:2]
        scale = min(INPUT_SIZE / h, INPUT_SIZE / w)
        nh, nw = int(h * scale), int(w * scale)

        # Resize to fit, place at the top-left of a black 640x640 canvas.
        canvas = np.zeros((INPUT_SIZE, INPUT_SIZE, 3), np.uint8)
        canvas[:nh, :nw] = cv2.resize(bgr, (nw, nh))
        blob = canvas[:, :, ::-1].astype(np.float32) / 255.0  # BGR -> RGB, 0..1
        blob = np.ascontiguousarray(blob.transpose(2, 0, 1)[None])  # NCHW

        out = self.compiled([blob])[self.output][0]  # (rows, 22)

        # Columns: 0-7 four corner points, 8 confidence logit,
        # 9-12 color scores, 13-21 plate-number scores.
        scores = 1.0 / (1.0 + np.exp(-out[:, 8]))
        keep = scores >= self.score_threshold
        out, scores = out[keep], scores[keep]
        if len(out) == 0:
            return []

        pts = out[:, :8].reshape(-1, 4, 2)[:, [0, 3, 2, 1]] / scale
        color_ids = out[:, 9:13].argmax(axis=1)
        num_ids = out[:, 13:22].argmax(axis=1)

        mins, maxs = pts.min(axis=1), pts.max(axis=1)
        boxes = np.hstack([mins, maxs - mins]).astype(int).tolist()
        picked = cv2.dnn.NMSBoxes(
            boxes, scores.tolist(), self.score_threshold, self.nms_threshold
        )

        armors = []
        for i in np.array(picked).flatten():
            num_id = int(num_ids[i])
            name = armor_name(num_id)
            kind = "big" if num_id == 1 else "small"
            confidence = float(scores[i])
            if name == "not_armor" or confidence <= self.min_confidence:
                continue
            if kind == "small" and name in ("one", "base"):
                continue
            if kind == "big" and name in ("two", "sentry", "outpost"):
                continue
            armors.append(
                Armor(
                    points=pts[i],
                    name=name,
                    color=COLOR_NAMES.get(int(color_ids[i]), "extinguish"),
                    kind=kind,
                    confidence=confidence,
                )
            )
        return armors


def draw(img, armors):
    for a in armors:
        pts = a.points.astype(np.int32)
        cv2.polylines(img, [pts], True, (0, 255, 0), 2)
        x, y = int(pts[:, 0].min()), int(pts[:, 1].min())
        label = f"{a.color} {a.name} {a.confidence:.2f}"
        cv2.putText(
            img, label, (x, max(y - 8, 12)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
        )
    return img
