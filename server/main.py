import time

import threading
import queue
import asyncio
import websockets
import json
import subprocess
import os

from video_processor import VideoProcessor
from camera_stream import get_frame, start_webrtc_server
from risk_analyzer import analyze
import sensor_receiver
from sensor_receiver import start_mqtt

from db.db_writer import insert_sensor, insert_risk

# 웹소켓 전역 변수 설정
connected_websocket_clients = set()
websocket_loop = None


def map_risk_level(level):
    if level in ("위험", "HIGH"):
        return "HIGH"
    if level in ("경고", "MID"):
        return "MID"
    return "LOW"


async def echo_server(websocket, *_args):
    connected_websocket_clients.add(websocket)

    try:
        async for message in websocket:
            pass

    except websockets.exceptions.ConnectionClosed:
        pass

    finally:
        connected_websocket_clients.discard(websocket)


async def broadcast_dashboard(payload):
    if not connected_websocket_clients:
        return

    message = json.dumps(payload)

    await asyncio.gather(
        *[
            websocket.send(message)
            for websocket in connected_websocket_clients
        ],
        return_exceptions=True
    )


def send_dashboard_update(result):
    if websocket_loop is None:
        return

    sensor = result["sensor"]
    payload = {
        "device_id": result["device_id"],
        "riskLevel": map_risk_level(result["risk"]),
        "temperature": sensor["temp"],
        "noise": sensor["noise"],
        "helmet": result["helmet"],
        "timestamp": result["timestamp"],
    }

    websocket_loop.call_soon_threadsafe(
        lambda: asyncio.create_task(
            broadcast_dashboard(payload)
        )
    )


def get_sensor_risk_level(sensor):
    temp = sensor.get("temp", 25.0)
    noise = sensor.get("noise", 50.0)

    if temp > 60 or noise > 85:
        return "HIGH"

    if temp > 40 or noise > 70:
        return "MID"

    return "LOW"


def send_sensor_dashboard_update(sensor):
    if websocket_loop is None:
        return

    payload = {
        "device_id": sensor.get("device_id", "helmet_001"),
        "riskLevel": get_sensor_risk_level(sensor),
        "temperature": sensor.get("temp", 25.0),
        "noise": sensor.get("noise", 50.0),
        "helmet": None,
        "timestamp": int(time.time() * 1000),
    }

    websocket_loop.call_soon_threadsafe(
        lambda: asyncio.create_task(
            broadcast_dashboard(payload)
        )
    )


def start_websocket_server():
    global websocket_loop

    websocket_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(websocket_loop)

    async def main_serve():
        async with websockets.serve(
            echo_server,
            "0.0.0.0",
            8765
        ):
            await asyncio.Future()

    websocket_loop.run_until_complete(main_serve())


# 데이터를 비동기로 동기화 및 처리하기 위한 큐
sync_queue = queue.Queue(maxsize=10)

processor = VideoProcessor()


def data_fusion_worker():
    print("[Worker] Data Fusion / AI Inference Thread: On")

    while True:

        frame, sensor, frame_meta = sync_queue.get()

        try:
            result = processor.process(
                frame,
                frame_meta,
                sensor
            )

            if result is None:
                continue

            print("\n========== AI RESULT ==========")
            print(f"device_id : {result['device_id']}")

            if result["helmet"] is None:
                print("person    : 없음")

            else:
                print("person    : 있음")
                print(f"helmet    : {result['helmet']}")

            print(f"temp      : {result['sensor']['temp']}")
            print(f"noise     : {result['sensor']['noise']}")
            print(f"risk      : {result['risk']}")

            print("================================\n")

            send_dashboard_update(result)

        except Exception as e:
            print(f"[Error] 분석 중 오류 발생: {e}")

        finally:
            sync_queue.task_done()


def data_polling_manager():

    print("[Manager] Data Polling Manager: On")

    last_frame_id = None
    last_sensor_seq = None

    while True:

        frame_packet = get_frame()
        sensor = sensor_receiver.get_sensor_data()

        if sensor is not None:
            current_sensor_seq = (
                sensor.get("device_id"),
                sensor.get("seq"),
                sensor.get("timestamp"),
            )

            if current_sensor_seq != last_sensor_seq:
                send_sensor_dashboard_update(sensor)
                last_sensor_seq = current_sensor_seq

        if frame_packet is not None and sensor is not None:

            frame = frame_packet["frame"]

            video_device_id = frame_packet.get("device_id")
            sensor_device_id = sensor.get("device_id")

            if (
                sensor_device_id
                and video_device_id
                and sensor_device_id != video_device_id
            ):
                time.sleep(0.01)
                continue

            current_frame_id = frame_packet.get(
                "frame_id",
                id(frame)
            )

            if current_frame_id != last_frame_id:

                try:
                    sync_queue.put_nowait(
                        (frame, sensor, frame_packet)
                    )

                except queue.Full:
                    pass

                last_frame_id = current_frame_id

        time.sleep(0.01)


def start_frontend():

    FRONTEND_PATH = (
        r"C:\Users\parkn\OneDrive\CLOUD\VSCODE\PYTHON\Safety\SW"
    )

    print("[Frontend] Next.js Frontend Starting...")

    subprocess.Popen(
        'start cmd /k "npm run dev"',
        cwd=FRONTEND_PATH,
        shell=True
    )


def main():

    print("=========================================")
    print("   안전모 실시간 관제 시스템 (Optimized) ")
    print("=========================================")

    # 0) 프론트엔드 자동 실행
    start_frontend()

    # 1) MQTT 시작
    start_mqtt()

    print("MQTT Receiver: On")

    time.sleep(1)

    # 2) WebRTC 영상 수신 서버 시작
    start_webrtc_server()

    print("WebRTC Receiver: On (Port 8080)")

    # 3) 웹소켓 서버 시작
    ws_thread = threading.Thread(
        target=start_websocket_server,
        daemon=True
    )

    ws_thread.start()

    print("WebSocket Server: On (Port 8765)")

    # 4) AI 분석 쓰레드 시작
    fusion_thread = threading.Thread(
        target=data_fusion_worker,
        daemon=True
    )

    fusion_thread.start()

    # 5) 데이터 수집 루프 시작
    data_polling_manager()


if __name__ == "__main__":
    main()
