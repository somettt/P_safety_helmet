import hardware.MQTT_Sender as mqtt_sender
import hardware.WebRTC_Sender as webrtc_sender
import threading

if __name__ == "__main__":
	mqtt_thread = threading.Thread(target=mqtt_sender.main)
	webrtc_thread = threading.Thread(target=webrtc_sender.run)

	mqtt_thread.start()
	webrtc_thread.start()

	mqtt_thread.join()
	webrtc_thread.join()
