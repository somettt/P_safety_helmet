import time
import json
import random

import paho.mqtt.client as mqtt

# import temp_reader as temp_reader

from datetime import datetime, timezone


BROKER = "broker.hivemq.com"
PORT = 1883

TOPIC = "helmet/sensor"

DEVICE_ID = "helmet_001"


def utc_ms():
    return int(
        datetime.now(timezone.utc).timestamp() * 1000
    )


def read_temperature():

    # 실제 센서 연결 시 사용
    #
    # for _ in range(3):
    #
    #     temp = temp_reader.read_temp()
    #
    #     if temp is not None:
    #         return temp
    #
    #     time.sleep(0.5)
    #
    # return None

    return 24.0 + random.uniform(-3, 3)


def read_noise():

    # TODO:
    # 실제 소음 센서 연결 시 수정

    return 73.0 + random.uniform(-3, 3)


def connect_mqtt():

    client = mqtt.Client(
        client_id=DEVICE_ID
    )

    # reconnect 설정
    client.reconnect_delay_set(
        min_delay=1,
        max_delay=10
    )

    while True:

        try:

            print("[MQTT] connecting...")

            client.connect(
                BROKER,
                PORT,
                60
            )

            print("[MQTT] connected")

            return client

        except Exception as e:

            print(
                "[MQTT] connection failed:",
                e
            )

            time.sleep(3)


def main():

    client = connect_mqtt()

    # background loop 시작
    client.loop_start()

    seq = 0

    try:

        while True:

            temp = read_temperature()

            if temp is None:

                print(
                    "[TEMP] read failed"
                )

                time.sleep(1)

                continue

            noise = read_noise()

            payload = {

                "device_id": DEVICE_ID,

                "timestamp": datetime.now().strftime(
                    "%H:%M:%S"
                ),

                "seq": seq,

                "temp": round(
                    float(temp),
                    1
                ),

                "noise": round(
                    float(noise),
                    1
                )
            }

            result = client.publish(
                TOPIC,
                json.dumps(payload)
            )

            if result.rc == mqtt.MQTT_ERR_SUCCESS:

                print(f"""
[MQTT SENT]
device_id : {DEVICE_ID}
time      : {payload['timestamp']}
seq       : {seq}
temp      : {payload['temp']}
noise     : {payload['noise']}
""")

            else:

                print(
                    "[MQTT] publish failed"
                )

            seq += 1

            time.sleep(2)

    except KeyboardInterrupt:

        print(
            "[MQTT] stopping..."
        )

    finally:

        client.loop_stop()

        client.disconnect()

        print(
            "[MQTT] disconnected"
        )


if __name__ == "__main__":

    main()