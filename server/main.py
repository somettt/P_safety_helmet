from camera_stream import get_frame, start_webrtc_server
from risk_analyzer import analyze
from sensor_receiver import start_mqtt, latest_sensor
import time

def main():
    # 1) MQTT 시작 (라즈베리파이 → 센서 데이터)
    start_mqtt()
    print("MQTT Receiver Started")
    time.sleep(1)
    # 2) WebRTC 영상 수신 서버 시작
    start_webrtc_server()
    print("WebRTC Video Receiver Started")

    # 3) 분석 루프
    while True:
        #while True:

        frame = get_frame()
        sensor = latest_sensor

        # 1) 센서 데이터 확인 먼저
        if sensor is None:
            print("Waiting for sensor data...")
        else:
            print("Sensor OK:", sensor)

        # 2) 영상 프레임 확인
        if frame is None:
            print("No frame received")
        else:
            print("Frame OK:", frame.shape)

        # 3) 두 조건 모두 만족할 때만 분석 실행
        if frame is not None and sensor is not None:
            result = analyze(frame, sensor)
            print("위험도:", result["level"])
            print("판단 사유:", result["reason"])
            print("==============")

        time.sleep(1)


if __name__ == "__main__":
    main()
