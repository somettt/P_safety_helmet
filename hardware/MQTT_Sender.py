import time
import json
import random
import paho.mqtt.client as mqtt
import temp_reader as temp_reader

from datetime import datetime, timezone

BROKER = "test.mosquitto.org"   # 클라우드 전용 주소로 수정 필요
PORT = 1883
TOPIC = "helmet/helmet_001/sensor"
DEVICE_ID = "helmet_001"

def utc_ms():
    return int(datetime.now(timezone.utc).timestamp() * 1000)

def read_temperature():
    for _ in range(3):
        temp = temp_reader.read_temp()
        if temp is not None:
            return temp
        time.sleep(0.5)
    return None

def read_noise():
    # TODO: 마이크/소음센서 값으로 교체
    return 73.0 + random.uniform(-3, 3)

def main():
    client = mqtt.Client(client_id=DEVICE_ID)
    client.connect(BROKER, PORT, 60)

    try:
        while True:
            temp = read_temperature()
            if temp is None:
                # Skip this cycle instead of crashing on float(None)
                time.sleep(1)
                continue

            payload = {
                "device_id": DEVICE_ID,
                "timestamp": utc_ms(),
                "temp": float(temp),
                "noise": float(read_noise())
            }

            client.publish(TOPIC, json.dumps(payload))
            print("[MQTT] sent:", payload)

            time.sleep(1)  # 0.5초 간격 송신
    except KeyboardInterrupt:
        print("...Stopping sensor publisher...")
        client.disconnect()

if __name__ == "__main__":
    main()
