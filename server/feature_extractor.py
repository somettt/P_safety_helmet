from ultralytics import YOLO
import cv2
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "helmet_yolov8s_hardhat.pt")

model = YOLO(MODEL_PATH)


def _normalize_label(label):
    return label.lower().replace(" ", "").replace("-", "").replace("_", "")


def _is_helmet_label(label):
    return _normalize_label(label) in {
        "helmet", "hardhat", "safetyhelmet", "helmeton"
    }


def _is_no_helmet_label(label):
    return _normalize_label(label) in {
        "nohelmet", "nohardhat", "withouthelmet"
    }


# 🔥 핵심 함수
def detect_person_and_helmet(frame, conf_thresh=0.3):
    frame = cv2.resize(frame, (640, 480))
    results = model(frame, verbose=False)

    person_exist = False
    helmet_conf = 0
    no_helmet_conf = 0

    for r in results:
        if r.boxes is None:
            continue

        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            label = model.names[cls].lower()

            if conf < conf_thresh:
                continue

            # 👤 사람 탐지
            if label == "person":
                person_exist = True

            # ⛑️ 헬멧 탐지
            if _is_no_helmet_label(label):
                no_helmet_conf = max(no_helmet_conf, conf)
            elif _is_helmet_label(label):
                helmet_conf = max(helmet_conf, conf)

    # 🎯 로직
    if not person_exist:
        return None   # 👈 핵심: 사람 없음

    if no_helmet_conf > helmet_conf:
        return 0

    if helmet_conf > 0:
        return 1

    return 0