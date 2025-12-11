import paho.mqtt.client as mqtt
import json

latest_sensor = None        # 최신 센서값 저장
got_sensor = False          # 센서가 한 번이라도 도착했는지 체크

def on_connect(client, userdata, flags, rc):
    print("MQTT Connected with result code", rc)
    client.subscribe("helmet/helmet_001/sensor")  # 센서 토픽 구독

def on_message(client, userdata, msg):
    global latest_sensor, got_sensor

    try:
        latest_sensor = json.loads(msg.payload.decode())
        got_sensor = True  # 센서가 한번이라도 도착했음을 표시
        print("Received Sensor:", latest_sensor)

    except Exception as e:
        print("JSON Parse Error:", e)

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # 브로커는 라즈베리파이와 동일 주소여야 함
    client.connect("broker.hivemq.com", 1883, 60)

    client.loop_start()
    return client
