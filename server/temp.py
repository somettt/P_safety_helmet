import os
import cv2
from ultralytics import YOLO

# ============================================================
# best.pt 경로 자동 계산 (server → 상위 폴더 → models/best.pt)
# ============================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))        # Safety/server
BASE_DIR = os.path.dirname(CURRENT_DIR)                         # Safety
MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")         # Safety/models/best.pt

print("MODEL PATH =", MODEL_PATH)
print("EXISTS? ->", os.path.exists(MODEL_PATH))

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("best.pt 찾을 수 없음: " + MODEL_PATH)

# ============================================================
# YOLO 모델 로드
# ============================================================

model = YOLO(MODEL_PATH)
print("Model Loaded. Classes:", model.names)

# ============================================================
# 이미지 로드(debug_frame.jpg는 server 폴더에 있다고 가정)
# ============================================================

IMG_PATH = os.path.join(CURRENT_DIR, "debug_frame.jpg")

if not os.path.exists(IMG_PATH):
    raise FileNotFoundError("debug_frame.jpg 없음: " + IMG_PATH)

img = cv2.imread(IMG_PATH)

# ============================================================
# YOLO 추론
# ============================================================

results = model(img, imgsz=640, conf=0.25)

print("=== DETECTION RESULTS ===")
for box in results[0].boxes:
    cls = int(box.cls[0])
    conf = float(box.conf[0])
    print(f"- {model.names[cls]} ({conf:.2f})")

# 박스 시각화
results[0].show()
