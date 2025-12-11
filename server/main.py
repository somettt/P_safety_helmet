import time
import sensor_receiver
import cv2
from camera_stream import get_frame, start_webrtc_server
from risk_analyzer import analyze
from db.db_writer import insert_sensor, insert_risk


def main():

    sensor_receiver.start_mqtt()
    print("MQTT Receiver: On")
    time.sleep(1)

    start_webrtc_server()
    print("WebRTC Receiver: On")

    while True:

        frame = get_frame()
        sensor = sensor_receiver.latest_sensor

        # --------------------------
        # 프레임 상태 출력
        # --------------------------
        if frame is None:
            print("프레임 수신(x)")
        else:
            print("프레임 수신(o):", frame.shape)

        # --------------------------
        # 센서 상태 출력
        # --------------------------
        if not sensor_receiver.got_sensor:
            print("센서 데이터(x)")
        else:
            print("센서 수신(o):", sensor)

        # --------------------------
        # CBR 실행 조건 (둘 다 있음)
        # --------------------------
        if frame is not None and sensor_receiver.got_sensor:
            print("CBR 분석 실행!")
            try:
                result = analyze(frame, sensor)

                print("위험도:", result["level"])
                print("판단 사유:", result["reason"])
                print("=========================")

                insert_sensor(sensor["temp"], sensor["noise"])
                insert_risk(result["level"], result["reason"])

            except Exception as e:
                print("CBR/DB Error:", e)

        time.sleep(0.2)


if __name__ == "__main__":
    main()
