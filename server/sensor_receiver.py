import paho.mqtt.client as mqtt
import json

latest_sensor = None  # 최신 센서값 저장

def on_connect(client, userdata, flags, rc):
    print("MQTT Connected with result code", rc)
    client.subscribe("helmet/helmet_001/sensor")  # 라즈베리파이가 보내는 topic

def on_message(client, userdata, msg):
    global latest_sensor
    try:
        latest_sensor = json.loads(msg.payload.decode())
        print("Received Sensor:", latest_sensor)
    except Exception as e:
        print("JSON Parse Error:", e)

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    # ★ 라즈베리파이가 보낼 브로커 주소와 동일해야 함
    # 로컬 PC 브로커 사용할 경우:
    client.connect("test.mosquitto.org", 1883, 60)
    
    client.loop_start()
    return client
