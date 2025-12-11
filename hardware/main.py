import MQTT_Sender as mqtt_sender
import WebRTC_Sender as webrtc_sender
import asyncio
import threading

if __name__ == "__main__":
    mqtt_thread = threading.Thread(target=mqtt_sender.main, daemon=True)
    webrtc_thread = threading.Thread(
        target=lambda: asyncio.run(webrtc_sender.run()), daemon=True
    )
    mqtt_thread.start()
    webrtc_thread.start()
    mqtt_thread.join()
    webrtc_thread.join()