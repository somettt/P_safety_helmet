import time
from feature_extractor import detect_person_and_helmet
from cbr_engine import ensemble_cbr


class VideoProcessor:
    def __init__(self):
        pass

    def process(self, frame, metadata, sensor):

        # =========================================
        # 1️⃣ 사람 + 헬멧 판단
        # =========================================
        helmet = detect_person_and_helmet(frame)

        # =========================================
        # 2️⃣ 사람 없음 → 센서 기반만 판단
        # =========================================
        if helmet is None:
            case = {
                "helmet": 1,   # 안전 상태 가정
                "pose": 0,
                "noise": sensor["noise"],
                "temp": sensor["temp"]
            }

            result, detail = ensemble_cbr(case)

            return {
                "frame_id": metadata["frame_id"],
                "device_id": metadata["device_id"],
                "timestamp": int(time.time() * 1000),

                "helmet": None,
                "risk": result,
                "sensor": sensor,
                "detail": detail
            }

        # =========================================
        # 3️⃣ 사람 있음 → 헬멧 포함 판단
        # =========================================
        case = {
            "helmet": helmet,
            "pose": 0,
            "noise": sensor["noise"],
            "temp": sensor["temp"]
        }

        result, detail = ensemble_cbr(case)

        return {
            "frame_id": metadata["frame_id"],
            "device_id": metadata["device_id"],
            "timestamp": int(time.time() * 1000),

            "helmet": helmet,
            "risk": result,
            "sensor": sensor,
            "detail": detail
        }