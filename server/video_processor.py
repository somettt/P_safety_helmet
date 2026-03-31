import time

from feature_extractor import detect_helmet
from cbr_engine import ensemble_cbr
from sensor_receiver import get_sensor_data


class VideoProcessor:
    def __init__(self):
        pass

    def process(self, frame, metadata):
        """
        frame: numpy image
        metadata: dict (네가 준 구조)
        """

        # =========================================
        # 1️⃣ YOLO → helmet 판단
        # =========================================
        helmet = detect_helmet(frame)

        # =========================================
        # 2️⃣ 센서 데이터 가져오기
        # =========================================
        sensor = get_sensor_data()

        if sensor is None:
            print("[WARN] 센서 데이터 없음")
            return None

        # =========================================
        # 3️⃣ CBR 입력 생성
        # =========================================
        case = {
            "helmet": helmet,
            "pose": 0,  # 추후 확장
            "noise": sensor["noise"],
            "temp": sensor["temp"]
        }

        # =========================================
        # 4️⃣ CBR 판단
        # =========================================
        result, detail = ensemble_cbr(case)

        # =========================================
        # 5️⃣ 결과 패킷 생성 (🔥 중요)
        # =========================================
        output = {
            "frame_id": metadata["frame_id"],
            "device_id": metadata["device_id"],
            "timestamp": int(time.time() * 1000),

            "helmet": helmet,
            "risk": result,

            "sensor": sensor,
            "detail": detail
        }

        return output