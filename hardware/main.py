import time
import asyncio
import threading

import MQTT_Sender as mqtt_sender
import WebRTC_Sender as webrtc_sender


def run_webrtc():

    while True:

        try:

            asyncio.run(
                webrtc_sender.run()
            )

        except Exception as e:

            print(
                "[WebRTC Thread ERROR]",
                e
            )

            time.sleep(3)


def run_mqtt():

    while True:

        try:

            mqtt_sender.main()

        except Exception as e:

            print(
                "[MQTT Thread ERROR]",
                e
            )

            time.sleep(3)


if __name__ == "__main__":

    print("================================")
    print(" Smart Helmet Raspberry Pi Node ")
    print("================================")

    mqtt_thread = threading.Thread(
        target=run_mqtt,
        daemon=True
    )

    webrtc_thread = threading.Thread(
        target=run_webrtc,
        daemon=True
    )

    mqtt_thread.start()

    webrtc_thread.start()

    print("[SYSTEM] All threads started")

    try:

        while True:
            time.sleep(1)

    except KeyboardInterrupt:

        print("[SYSTEM] Shutdown")