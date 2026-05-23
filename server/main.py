import time

import threading
import queue
import asyncio
import websockets
import json
import subprocess

from video_processor import VideoProcessor
from camera_stream import (
    get_frame,
    start_webrtc_server
)

import sensor_receiver
from sensor_receiver import start_mqtt

from db.db_writer import (
    insert_sensor,
    insert_risk
)


# ==================================================
# WebSocket 전역 설정
# ==================================================

connected_websocket_clients = set()

websocket_loop = None


# ==================================================
# Dashboard Risk Mapping
# ==================================================

def map_risk_level(level):

    if level in ("위험", "HIGH"):
        return "HIGH"

    if level in ("경고", "MID"):
        return "MID"

    return "LOW"


# ==================================================
# WebSocket Echo Server
# ==================================================

async def echo_server(websocket, *_args):

    connected_websocket_clients.add(websocket)

    print(
        f"[WebSocket] Client Connected "
        f"({len(connected_websocket_clients)})"
    )

    try:

        async for _message in websocket:
            pass

    except websockets.exceptions.ConnectionClosed:

        print("[WebSocket] Client Disconnected")

    finally:

        connected_websocket_clients.discard(websocket)


# ==================================================
# Dashboard Broadcast
# ==================================================

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


# ==================================================
# Dashboard 전송
# ==================================================

def send_dashboard_update(result):

    if websocket_loop is None:
        return

    sensor = result["sensor"]

    payload = {

        "device_id": result["device_id"],

        "riskLevel": map_risk_level(
            result["risk"]
        ),

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


# ==================================================
# 센서 기반 위험도 계산
# ==================================================

def get_sensor_risk_level(sensor):

    temp = sensor.get("temp", 25.0)

    noise = sensor.get("noise", 50.0)

    if temp > 60 or noise > 85:
        return "HIGH"

    if temp > 40 or noise > 70:
        return "MID"

    return "LOW"


# ==================================================
# 센서 Dashboard 전송
# ==================================================

def send_sensor_dashboard_update(sensor):

    if websocket_loop is None:
        return

    payload = {

        "device_id": sensor.get(
            "device_id",
            "helmet_001"
        ),

        "riskLevel": get_sensor_risk_level(
            sensor
        ),

        "temperature": sensor.get(
            "temp",
            25.0
        ),

        "noise": sensor.get(
            "noise",
            50.0
        ),

        "helmet": None,

        "timestamp": int(
            time.time() * 1000
        ),
    }

    websocket_loop.call_soon_threadsafe(
        lambda: asyncio.create_task(
            broadcast_dashboard(payload)
        )
    )


# ==================================================
# WebSocket Server
# ==================================================

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

            print(
                "[WebSocket] Server Started "
                "(Port 8765)"
            )

            await asyncio.Future()

    websocket_loop.run_until_complete(
        main_serve()
    )


# ==================================================
# Queue
# ==================================================

sync_queue = queue.Queue(maxsize=10)

processor = VideoProcessor()


# ==================================================
# AI 분석 Worker
# ==================================================

def data_fusion_worker():

    print(
        "[Worker] Data Fusion / "
        "AI Inference Thread: On"
    )

    while True:

        frame, sensor, frame_meta = sync_queue.get()

        try:

            result = processor.process(
                frame,
                frame_meta,
                sensor
            )

            print(
                "[DEBUG] result =",
                result
            )

            if result is None:

                print(
                    "[DEBUG] result is None"
                )

                continue

            print(
                "\n========== AI RESULT =========="
            )

            print(
                f"device_id : "
                f"{result['device_id']}"
            )

            # ==========================
            # 사람 / 헬멧 상태
            # ==========================

            if result["helmet"] is None:

                print("person    : 없음")

            else:

                print("person    : 있음")

                print(
                    f"helmet    : "
                    f"{result['helmet']}"
                )

            # ==========================
            # 센서 데이터
            # ==========================

            temp = result["sensor"]["temp"]

            noise = result["sensor"]["noise"]

            print(f"temp      : {temp}")

            print(f"noise     : {noise}")

            # ==========================
            # 위험도
            # ==========================

            risk = result["risk"]

            print(f"risk      : {risk}")

            # ==========================
            # SQLite 저장
            # ==========================

            try:

                print("[DB] inserting...")

                insert_sensor(
                    temp,
                    noise
                )

                insert_risk(
                    risk,
                    f"helmet={result['helmet']}, "
                    f"noise={noise}"
                )

                print(
                    "[DB] 저장 완료"
                )

            except Exception as db_error:

                print(
                    f"[DB ERROR] {db_error}"
                )

            print(
                "================================\n"
            )

            # ==========================
            # Dashboard 전송
            # ==========================

            send_dashboard_update(
                result
            )

        except Exception as e:

            print(
                f"[Error] 분석 중 오류 발생: {e}"
            )

        finally:

            sync_queue.task_done()


# ==================================================
# 데이터 Polling Manager
# ==================================================

def data_polling_manager():

    print(
        "[Manager] Data Polling Manager: On"
    )

    last_frame_id = None

    last_sensor_seq = None

    while True:

        frame_packet = get_frame()

        sensor = sensor_receiver.get_sensor_data()

        # ==========================
        # 센서 Dashboard 갱신
        # ==========================

        if sensor is not None:

            current_sensor_seq = (

                sensor.get("device_id"),

                sensor.get("seq"),

                sensor.get("timestamp"),
            )

            if current_sensor_seq != last_sensor_seq:

                send_sensor_dashboard_update(
                    sensor
                )

                last_sensor_seq = (
                    current_sensor_seq
                )

        # ==========================
        # 영상 + 센서 동기화
        # ==========================

        if (
            frame_packet is not None
            and sensor is not None
        ):

            frame = frame_packet["frame"]

            video_device_id = frame_packet.get(
                "device_id"
            )

            sensor_device_id = sensor.get(
                "device_id"
            )

            if (
                sensor_device_id
                and video_device_id
                and sensor_device_id
                != video_device_id
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
                        (
                            frame,
                            sensor,
                            frame_packet
                        )
                    )

                except queue.Full:

                    print(
                        "[Queue] Full"
                    )

                last_frame_id = (
                    current_frame_id
                )

        time.sleep(0.01)


# ==================================================
# Frontend 실행
# ==================================================

def start_frontend():

    FRONTEND_PATH = (
        r"C:\Users\parkn\OneDrive\CLOUD"
        r"\VSCODE\PYTHON\Safety\SW"
    )

    print(
        "[Frontend] "
        "Next.js Frontend Starting..."
    )

    subprocess.Popen(
        'start cmd /k "npm run dev"',
        cwd=FRONTEND_PATH,
        shell=True
    )


# ==================================================
# MAIN
# ==================================================

def main():

    print(
        "========================================="
    )

    print(
        "   안전모 실시간 관제 시스템 "
        "(Optimized)"
    )

    print(
        "========================================="
    )

    # 1) Frontend 실행
    start_frontend()

    # 2) MQTT 시작
    start_mqtt()

    print("MQTT Receiver: On")

    time.sleep(1)

    # 3) WebRTC 수신 서버
    start_webrtc_server()

    print(
        "WebRTC Receiver: On "
        "(Port 8080)"
    )

    # 4) WebSocket 서버
    ws_thread = threading.Thread(
        target=start_websocket_server,
        daemon=True
    )

    ws_thread.start()

    # 5) AI Worker
    fusion_thread = threading.Thread(
        target=data_fusion_worker,
        daemon=True
    )

    fusion_thread.start()

    # 6) Polling 시작
    data_polling_manager()


if __name__ == "__main__":

    main()