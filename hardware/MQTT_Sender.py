import time
import json

import paho.mqtt.client as mqtt
import temp_reader as temp_reader
import sounddevice as sd
import numpy as np

from datetime import datetime, timezone


BROKER = "broker.hivemq.com"
PORT = 1883

TOPIC = "helmet/sensor"

DEVICE_ID = "helmet_001"
NOISE_DBFS_OFFSET = 100.0


def utc_ms():
    return int(
        datetime.now(timezone.utc).timestamp() * 1000
    )


def read_temperature():

    # 실제 센서 연결 시 사용
    for _ in range(3):
        temp = temp_reader.read_temp()
        if temp is not None:
            return temp
        time.sleep(0.5)
    return None


def read_noise():
    duration = 0.2
    samplerate = 16000

    audio = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype="float32"
    )
    sd.wait()

    x = audio.flatten()
    rms = np.sqrt(np.mean(np.square(x)) + 1e-12)
    dbfs = 20 * np.log10(rms + 1e-12)

    db_spl_est = dbfs + NOISE_DBFS_OFFSET

    return float(db_spl_est)


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
