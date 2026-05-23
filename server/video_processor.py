import time
import cv2

from feature_extractor import (
    detect_person_and_helmet
)

from cbr_engine import (
    ensemble_cbr
)


class VideoProcessor:

    def __init__(self):

        # =====================================
        # Helmet smoothing
        # =====================================

        self.helmet_history = []

        self.history_size = 10

        # =====================================
        # Sensor smoothing
        # =====================================

        self.noise_history = []

        self.temp_history = []

        self.sensor_history_size = 5

        # =====================================
        # YOLO throttling
        # =====================================

        self.last_detect_time = 0

        self.last_helmet_raw = None

        # YOLO 실행 주기
        self.detect_interval = 0.5

    # ==========================================
    # Helmet smoothing
    # ==========================================

    def smooth_helmet_status(
        self,
        helmet_raw
    ):

        if helmet_raw is not None:

            self.helmet_history.append(
                helmet_raw
            )

        if len(self.helmet_history) > self.history_size:

            self.helmet_history.pop(0)

        if len(self.helmet_history) == 0:

            return None

        helmet_count = self.helmet_history.count(1)

        no_helmet_count = self.helmet_history.count(0)

        if no_helmet_count >= 7:

            return 0

        return 1

    # ==========================================
    # Sensor smoothing
    # ==========================================

    def smooth_sensor(
        self,
        value,
        history
    ):

        history.append(value)

        if len(history) > self.sensor_history_size:

            history.pop(0)

        return round(
            sum(history) / len(history),
            1
        )

    # ==========================================
    # Overlay 출력
    # ==========================================

    def draw_overlay(
        self,
        frame,
        helmet,
        risk,
        temp,
        noise
    ):

        # 위험도 색상
        color = (0, 255, 0)

        if risk == "MID":

            color = (0, 255, 255)

        elif risk == "HIGH":

            color = (0, 0, 255)

        # 헬멧 상태 텍스트
        helmet_text = "NO PERSON"

        if helmet == 1:

            helmet_text = "HELMET"

        elif helmet == 0:

            helmet_text = "NO HELMET"

        # 반투명 박스
        overlay = frame.copy()

        cv2.rectangle(
            overlay,
            (10, 10),
            (350, 190),
            (30, 30, 30),
            -1
        )

        alpha = 0.5

        cv2.addWeighted(
            overlay,
            alpha,
            frame,
            1 - alpha,
            0,
            frame
        )

        # 텍스트 출력
        cv2.putText(
            frame,
            f"RISK : {risk}",
            (20, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            3
        )

        cv2.putText(
            frame,
            helmet_text,
            (20, 85),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            3
        )

        cv2.putText(
            frame,
            f"TEMP : {temp} C",
            (20, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"NOISE : {noise} dB",
            (20, 170),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

    # ==========================================
    # Main process
    # ==========================================

    def process(
        self,
        frame,
        metadata,
        sensor
    ):

        current_time = time.time()

        # ======================================
        # YOLO 일정 주기마다만 실행
        # ======================================

        if (
            current_time - self.last_detect_time
            > self.detect_interval
        ):

            helmet_raw = detect_person_and_helmet(
                frame
            )

            self.last_helmet_raw = helmet_raw

            self.last_detect_time = current_time

            print(
                "[YOLO] new inference:",
                helmet_raw
            )

        else:

            helmet_raw = self.last_helmet_raw

        # ======================================
        # Helmet smoothing
        # ======================================

        helmet = self.smooth_helmet_status(
            helmet_raw
        )

        # ======================================
        # Sensor smoothing
        # ======================================

        smooth_noise = self.smooth_sensor(
            sensor["noise"],
            self.noise_history
        )

        smooth_temp = self.smooth_sensor(
            sensor["temp"],
            self.temp_history
        )

        # ======================================
        # 사람 없음
        # ======================================

        if helmet is None:

            case = {

                "helmet": 1,

                "pose": 0,

                "noise": smooth_noise,

                "temp": smooth_temp
            }

            result, detail = ensemble_cbr(
                case
            )

            self.draw_overlay(
                frame,
                None,
                result,
                smooth_temp,
                smooth_noise
            )

            return {

                "frame_id": metadata["frame_id"],

                "device_id": metadata["device_id"],

                "timestamp": int(
                    time.time() * 1000
                ),

                "helmet": None,

                "risk": result,

                "sensor": {
                    "temp": smooth_temp,
                    "noise": smooth_noise
                },

                "detail": detail,

                "frame": frame
            }

        # ======================================
        # 사람 있음
        # ======================================

        case = {

            "helmet": helmet,

            "pose": 0,

            "noise": smooth_noise,

            "temp": smooth_temp
        }

        result, detail = ensemble_cbr(
            case
        )

        # Overlay 출력
        self.draw_overlay(
            frame,
            helmet,
            result,
            smooth_temp,
            smooth_noise
        )

        return {

            "frame_id": metadata["frame_id"],

            "device_id": metadata["device_id"],

            "timestamp": int(
                time.time() * 1000
            ),

            "helmet": helmet,

            "risk": result,

            "sensor": {
                "temp": smooth_temp,
                "noise": smooth_noise
            },

            "detail": detail,

            "frame": frame
        }