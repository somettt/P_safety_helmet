import os
from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # Safety 폴더
model_path = os.path.join(BASE_DIR, "models", "best.pt")

model = YOLO(model_path)
print(model.names)
