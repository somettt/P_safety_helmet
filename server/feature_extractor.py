import os
import cv2
from ultralytics import YOLO

# ============================================================
# best.pt 경로 자동 설정
# ============================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))    # Safety/server
BASE_DIR = os.path.dirname(CURRENT_DIR)                     # Safety
MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")     # Safety/models/best.pt

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("best.pt 파일을 찾을 수 없습니다: " + MODEL_PATH)

model = YOLO(MODEL_PATH)

HELMET_KEYWORDS = ["helmet", "hardhat"]
NO_HELMET_KEYWORDS = ["no_helmet", "no-hardhat", "without helmet"]


# ============================================================
# 헬멧 탐지 함수
# ============================================================
def detect_helmet(frame):

    # YOLO 입력 향상 (리사이즈)
    try:
        frame_resized = cv2.resize(frame, (640, 640))
    except Exception:
        return 0

    results = model(frame_resized, imgsz=640, conf=0.20)

    has_helmet = False
    has_no_helmet = False

    for box in results[0].boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        name = results[0].names[cls].lower()

        if conf < 0.20:
            continue

        if any(k in name for k in HELMET_KEYWORDS):
            has_helmet = True

        if any(k in name for k in NO_HELMET_KEYWORDS):
            has_no_helmet = True

    if has_no_helmet:
        return 0
    if has_helmet:
        return 1

    return 0
