import os
from ultralytics import YOLO

# 모델 자동 경로 탐색
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")

# YOLO 모델 로드
model = YOLO(MODEL_PATH)

# 2 = helmet, 6 = no_helmet
HELMET_CLASS = 2
NO_HELMET_CLASS = 6


def detect_helmet(frame):
    results = model(frame)

    has_helmet = False
    has_no_helmet = False

    for box in results[0].boxes:
        cls = int(box.cls[0])

        if cls == HELMET_CLASS:
            has_helmet = True
        elif cls == NO_HELMET_CLASS:
            has_no_helmet = True

    if has_no_helmet:
        return 0
    if has_helmet:
        return 1

    return 0
