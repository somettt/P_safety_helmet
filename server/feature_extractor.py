from ultralytics import YOLO
import cv2
import os

# =========================
# YOLO 모델 경로 설정
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "helmet_yolov8s_hardhat.pt")

model = YOLO(MODEL_PATH)
_debug_label_print_count = 0


def _normalize_label(label):
    return label.lower().replace(" ", "").replace("-", "").replace("_", "")


def _is_helmet_label(label):
    norm = _normalize_label(label)
    helmet_aliases = {
        "helmet",
        "hardhat",
        "hardhats",
        "safetyhelmet",
        "helmeton",
        "withhelmet",
        "hat",
    }
    return norm in helmet_aliases


def _is_no_helmet_label(label):
    norm = _normalize_label(label)
    no_helmet_aliases = {
        "nohelmet",
        "nohardhat",
        "withouthelmet",
        "helmetoff",
    }
    return norm in no_helmet_aliases


def is_overlap(box_a, box_b):
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    return inter_x2 > inter_x1 and inter_y2 > inter_y1

# =========================
# 헬멧 탐지
# =========================
def detect_helmet(frame, conf_thresh=0.2):
    global _debug_label_print_count
    frame = cv2.resize(frame, (640, 480))
    results = model(frame, verbose=False)

    helmet_conf_max = 0.0
    no_helmet_conf_max = 0.0

    # 1) 클래스별 최대 confidence 수집
    for r in results:
        if r.boxes is None:
            continue

        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            label = model.names[cls].lower()

            if _debug_label_print_count < 30:
                print(f"[YOLO DEBUG] label={label}, conf={conf:.3f}")
                _debug_label_print_count += 1

            if conf < conf_thresh:
                continue

            norm = _normalize_label(label)
            if _is_no_helmet_label(label):
                no_helmet_conf_max = max(no_helmet_conf_max, conf)
            elif _is_helmet_label(label):
                helmet_conf_max = max(helmet_conf_max, conf)

    # 2) helmet / no_helmet 직접 비교
    if no_helmet_conf_max > helmet_conf_max:
        return 0  # 미착용
    if helmet_conf_max > 0:
        return 1  # 착용
    return 0  # 정보 없으면 보수적으로 미착용
