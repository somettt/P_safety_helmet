import time
import json
import random
import paho.mqtt.client as mqtt
# import temp_reader as temp_reader

from datetime import datetime, timezone

BROKER = "broker.hivemq.com" #클라우드 주소로 추후에 수정 필요(확장시)
PORT = 1883
TOPIC = "helmet/sensor"  
DEVICE_ID = "helmet_001"


def utc_ms():
    return int(datetime.now(timezone.utc).timestamp() * 1000)

def read_temperature():
    # for _ in range(3):
    #     temp = temp_reader.read_temp()
    #     if temp is not None:
    #         return temp
    #     time.sleep(0.5)
    # return None
    return 24.0 + random.uniform(-3, 3)


def read_noise():
    # TODO: 마이크/소음센서 값으로 교체
    return 73.0 + random.uniform(-3, 3)

def main():
    client = mqtt.Client(client_id=DEVICE_ID)
    client.connect(BROKER, PORT, 60)

    seq = 0
    try:
        while True:
            temp = read_temperature()
            if temp is None:
                time.sleep(1)
                continue

            payload = {
                "device_id": DEVICE_ID,
                "timestamp_utc_ms": utc_ms(),
                "seq": seq,
                "temp": float(temp),
                "noise": float(read_noise())
            }

            client.publish(TOPIC, json.dumps(payload))
            print("[MQTT] sent:", payload)

            seq += 1
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("...Stopping sensor publisher...")
        client.disconnect()

if __name__ == "__main__":
    main()
