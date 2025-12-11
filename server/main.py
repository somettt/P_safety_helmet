from camera_stream import get_frame, start_webrtc_server
from risk_analyzer import analyze
from sensor_receiver import start_mqtt, latest_sensor
from WebRTC_Server import start_webrtc_signaling_server
import time


def main():
    ###############################################
    # 0) WebRTC signaling 서버 시작 (POST /offer)
    ###############################################
    start_webrtc_signaling_server()
    print("WebRTC Server: On")

    ###############################################
    # 1) MQTT 시작 (라즈베리파이 → 센서 데이터)
    ###############################################
    start_mqtt()
    print("MQTT Receiver: On")
    time.sleep(1)

    ###############################################
    # 2) WebRTC 영상 수신 서버 시작 (프레임 받는 서버)
    ###############################################
    start_webrtc_server()
    print("WebRTC Receiver: On")

    ###############################################
    # 3) AI 분석 루프
    ###############################################
    while True:

        frame = get_frame()
        sensor = latest_sensor

        # 센서 데이터 상태 확인
        if sensor is None:
            print("센서 데이터(x)")
        else:
            print("센서 수신(o):", sensor)

        # 영상 프레임 확인
        if frame is None:
            print("프레임 수신(x)")
        else:
            print("프레임 수신(o):", frame.shape)

        # 두 조건 모두 있어야 위험도 분석 수행
        if frame is not None and sensor is not None:
            result = analyze(frame, sensor)
            print("위험도:", result["level"])
            print("판단 사유:", result["reason"])
            print("==============")

        time.sleep(1)


if __name__ == "__main__":
    main()
