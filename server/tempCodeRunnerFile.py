import json
import paho.mqtt.client as mqtt

BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "helmet/helmet_001/sensor"

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[MQTT] Connected with code {reason_code}")
    client.subscribe(TOPIC)
    print(f"[MQTT] Subscribed to {TOPIC}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        device_id = data.get("device_id")
        ts = data.get("timestamp")
        temp = data.get("temp")
        noise = data.get("noise")

        print(f"[RECV] device={device_id} ts={ts} temp={temp:.2f} noise={noise:.2f}")

        # 여기서 DB 저장 / 알람 로직 호출 / 웹소켓 브로드캐스트 등 하면 됨

    except Exception as e:
        print("[ERROR] Failed to parse message:", e)

def main():
    client = mqtt.Client(client_id="helmet_receiver")
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()