import os
import sys
import json
import importlib.util
import paho.mqtt.client as mqtt

# === 같은 폴더의 config.py 강제 로드 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(BASE_DIR, "config.py")

spec = importlib.util.spec_from_file_location("config", config_path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

import cbr
import db


def on_connect(client, userdata, flags, rc):
    print("MQTT connected:", rc)
    client.subscribe(config.MQTT_TOPIC)
    print(f"Subscribed to {config.MQTT_TOPIC}")


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
        print("[MQTT] raw payload:", data)

        # 센서 데이터 정리해서 DB에 저장 
        sensor_row = {
            "device_id": data.get("device_id"),
            "helmet": int(data.get("helmet", 1)),          # 못 받으면 1로 가정
            "temp": float(data.get("temp", 0.0)),
            "noise": float(data.get("noise", 0.0)),
            "timestamp": data.get("timestamp")
        }

        sensor_id = db.insert_sensor_log(sensor_row)

        # ── 2) CBR로 위험도 평가 ──
        # cbr.evaluate_risk(helmet: int, temp: float, noise: float)
        level, score, reason = cbr.evaluate_risk(
            helmet=sensor_row["helmet"],
            temp=sensor_row["temp"],
            noise=sensor_row["noise"]
        )

        # ── 3) 위험도 결과 DB 저장 ──
        db.insert_risk_result(sensor_id, level, score, reason)

        print(
            f"[MQTT] sensor_id={sensor_id}, "
            f"level={level}, score={score}, reason={reason}"
        )

    except Exception as e:
        print("[MQTT] Error handling message:", e)


def main():
    # client_id는 팀원 예시처럼 줘도 되고 안 줘도 되고 상관 없음
    client = mqtt.Client(client_id="helmet_receiver")
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
    client.loop_forever()


if __name__ == "__main__":
    main()