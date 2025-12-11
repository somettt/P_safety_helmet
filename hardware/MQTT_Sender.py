import time
import json
import random
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

BROKER = "test.mosquitto.org"   # 클라우드 전용 주소로 수정 필요
PORT = 1883
TOPIC = "helmet/helmet_001/sensor"
DEVICE_ID = "helmet_001"

def utc_ms():
    return int(datetime.now(timezone.utc).timestamp() * 1000)

def read_temperature():
    # TODO: 실제 센서 붙으면 여기 교체
    return 27.0 + random.uniform(-0.5, 0.5)

def read_noise():
    # TODO: 마이크/소음센서 값으로 교체
    return 73.0 + random.uniform(-3, 3)

def main():
    client = mqtt.Client(client_id=DEVICE_ID)
    client.connect(BROKER, PORT, 60)

    try:
        while True:
            payload = {
                "device_id": DEVICE_ID,
                "timestamp": utc_ms(),
                "temp": float(read_temperature()),
                "noise": float(read_noise())
            }

            client.publish(TOPIC, json.dumps(payload))
            print("[MQTT] sent:", payload)

            time.sleep(0.5)  # 0.5초 간격 송신
    except KeyboardInterrupt:
        print("...Stopping sensor publisher...")
        client.disconnect()

if __name__ == "__main__":
    main()