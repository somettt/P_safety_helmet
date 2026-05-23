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
def detect_person_and_helmet(frame, conf_thresh=0.45):
    frame = cv2.resize(frame, (640, 480))
    results = model(frame, verbose=False)

    persons = []
    helmets = []

    for r in results:
        if r.boxes is None:
            continue

        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            label = model.names[cls].lower()
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            if conf < conf_thresh:
                continue

            if label == "person":
                persons.append((x1, y1, x2, y2))

            elif _is_helmet_label(label):
                helmets.append((x1, y1, x2, y2))

    if len(persons) == 0:
        return None

    for px1, py1, px2, py2 in persons:

        head_y = py1 + (py2 - py1) * 0.50
        helmet_found = False
        margin_x = (px2 - px1) * 0.1
        for hx1, hy1, hx2, hy2 in helmets:
            helmet_center_x = (hx1 + hx2) / 2
            helmet_center_y = (hy1 + hy2) / 2
            if (
                px1 - margin_x
                <= helmet_center_x
                <= px2 + margin_x
                and py1 <= helmet_center_y <= head_y
            ):
                helmet_found = True
                break

        if not helmet_found:
            return 0

    return 1