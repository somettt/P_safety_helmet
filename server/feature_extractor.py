from ultralytics import YOLO
import cv2
import os

# =========================
# YOLO 모델 경로 설정
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")

model = YOLO(MODEL_PATH)

# =========================
# 헬멧 탐지
# =========================
def detect_helmet(frame, conf_thresh=0.5):
    frame = cv2.resize(frame, (640, 480))
    results = model(frame, verbose=False)

    persons = []
    helmets = []
    heads = []

    # 1️⃣ 객체 분리
    for r in results:
        if r.boxes is None:
            continue

        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            label = model.names[cls].lower()

            if conf < conf_thresh:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if "person" in label:
                persons.append((x1, y1, x2, y2))

            elif "helmet" in label:
                helmets.append((x1, y1, x2, y2))

            elif "head" in label:
                heads.append((x1, y1, x2, y2))

    # 2️⃣ head 기준 판단 (🔥 핵심)
    for head in heads:
        for helmet in helmets:
            if is_overlap(head, helmet):
                return 1  # 착용

    return 0  # 미착용