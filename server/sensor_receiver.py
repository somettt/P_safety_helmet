import paho.mqtt.client as mqtt
import json
from datetime import datetime
# ============================================
# 전역 변수
# ============================================
latest_sensor = None
got_sensor = False

# ============================================
# MQTT 콜백
# ============================================
def on_connect(client, userdata, flags, rc):
    print("[MQTT] Connected")
    client.subscribe("helmet/sensor") # 🔥 토픽 맞춰야 함 (라즈베리파이 sender랑 동일)


def on_message(client, userdata, msg):
    global latest_sensor, got_sensor

    try:
        payload = msg.payload.decode()
        data = json.loads(payload)

        latest_sensor = data
        got_sensor = True

        # 🔥 timestamp 유연 처리
        if "timestamp_utc_ms" in data:
            ts = datetime.fromtimestamp(data['timestamp_utc_ms'] / 1000)
            time_str = ts.strftime('%H:%M:%S')
        else:
            time_str = data.get("timestamp", "N/A")

        print(f"""
[MQTT RECEIVED]
device_id : {data.get('device_id')}
time      : {time_str}
seq       : {data.get('seq')}
temp      : {data.get('temp')}
noise     : {data.get('noise')}
""")

    except Exception as e:
        print("[MQTT] JSON Parse Error:", e)


# ============================================
# MQTT 시작
# ============================================
def start_mqtt():
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    # 🔥 브로커 주소 (sender랑 동일해야 함)
    client.connect("broker.hivemq.com", 1883, 60)

    client.loop_start()

    return client


# ============================================
# 센서 데이터 가져오기
# ============================================
def get_sensor_data():
    return latest_sensor