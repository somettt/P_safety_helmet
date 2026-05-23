import time
import cv2

import threading
import queue
import asyncio
import websockets
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

# ==========================================
# WebSocket 전역 변수
# ==========================================

connected_websocket_clients = set()

websocket_loop = None

# ==========================================
# Queue
# ==========================================

sync_queue = queue.Queue(maxsize=10)

processor = VideoProcessor()

# ==========================================
# Risk Mapping
# ==========================================

def map_risk_level(level):

    if level in ("위험", "HIGH"):

        return "HIGH"

    if level in ("경고", "MID"):

        return "MID"

    return "LOW"

# ==========================================
# WebSocket
# ==========================================

async def echo_server(
    websocket,
    *_args
):

    connected_websocket_clients.add(
        websocket
    )

    try:

        async for _message in websocket:

            pass

    except websockets.exceptions.ConnectionClosed:

        pass

    finally:

        connected_websocket_clients.discard(
            websocket
        )

# ==========================================
# WebSocket Server
# ==========================================

def start_websocket_server():

    global websocket_loop

    websocket_loop = asyncio.new_event_loop()

    asyncio.set_event_loop(
        websocket_loop
    )

    async def main_serve():

        async with websockets.serve(
            echo_server,
            "0.0.0.0",
            8765
        ):

            await asyncio.Future()

    websocket_loop.run_until_complete(
        main_serve()
    )

# ==========================================
# AI Worker
# ==========================================

def data_fusion_worker():

    print(
        "[Worker] Data Fusion / AI Inference Thread: On"
    )

    while True:

        frame, sensor, frame_meta = (
            sync_queue.get()
        )

        try:

            result = processor.process(
                frame,
                frame_meta,
                sensor
            )

            if result is None:

                continue

            # ==================================
            # 영상 출력
            # ==================================

            if "frame" in result:

                cv2.imshow(
                    "Smart Helmet Monitoring",
                    result["frame"]
                )

                key = cv2.waitKey(1)

                # ESC 종료
                if key == 27:

                    cv2.destroyAllWindows()

            # ==================================
            # 콘솔 출력
            # ==================================

            print(
                "\n============ RESULT ==========="
            )

            print(
                f"device_id : {result['device_id']}"
            )

            if result["helmet"] is None:

                print("person    : 없음")

            else:

                print("person    : 있음")

                print(
                    f"helmet    : {result['helmet']}"
                )

            print(
                f"temp      : {result['sensor']['temp']}"
            )

            print(
                f"noise     : {result['sensor']['noise']}"
            )

            print(
                f"risk      : {result['risk']}"
            )

            print(
                "================================\n"
            )

            # ==================================
            # DB 저장
            # ==================================

            insert_sensor(
                result["sensor"]["temp"],
                result["sensor"]["noise"]
            )

            insert_risk(
                map_risk_level(
                    result["risk"]
                ),
                str(
                    result["detail"]
                )
            )

        except Exception as e:

            print(
                f"[Error] 분석 중 오류 발생: {e}"
            )

        finally:

            sync_queue.task_done()

# ==========================================
# Data Polling
# ==========================================

def data_polling_manager():

    print(
        "[Manager] Data Polling Manager: On"
    )

    last_frame_id = None

    while True:

        frame_packet = get_frame()

        sensor = (
            sensor_receiver.get_sensor_data()
        )

        if (
            frame_packet is not None
            and sensor is not None
        ):

            frame = frame_packet["frame"]

            video_device_id = (
                frame_packet.get(
                    "device_id"
                )
            )

            sensor_device_id = (
                sensor.get(
                    "device_id"
                )
            )

            # device mismatch 방지
            if (
                sensor_device_id
                and video_device_id
                and sensor_device_id
                != video_device_id
            ):

                time.sleep(0.01)

                continue

            current_frame_id = (
                frame_packet.get(
                    "frame_id",
                    id(frame)
                )
            )

            # 중복 frame 방지
            if (
                current_frame_id
                != last_frame_id
            ):

                try:

                    sync_queue.put_nowait(
                        (
                            frame,
                            sensor,
                            frame_packet
                        )
                    )

                except queue.Full:

                    pass

                last_frame_id = (
                    current_frame_id
                )

        time.sleep(0.01)

# ==========================================
# Frontend
# ==========================================

def start_frontend():

    try:

        FRONTEND_PATH = (
            r"C:\Users\parkn\OneDrive\CLOUD\VSCODE\PYTHON\Safety\SW"
        )

        print(
            "[Frontend] Next.js Frontend Starting..."
        )

        subprocess.Popen(
            'start cmd /k "npm run dev"',
            cwd=FRONTEND_PATH,
            shell=True
        )

    except Exception as e:

        print(
            "[Frontend Error]",
            e
        )

# ==========================================
# Main
# ==========================================

def main():

    print(
        "========================================="
    )

    print(
        "   안전모 실시간 관제 시스템 (Optimized)"
    )

    print(
        "========================================="
    )

    # ======================================
    # Frontend
    # ======================================

    start_frontend()

    # ======================================
    # MQTT
    # ======================================

    start_mqtt()

    print(
        "MQTT Receiver: On"
    )

    time.sleep(1)

    # ======================================
    # WebRTC
    # ======================================

    start_webrtc_server()

    print(
        "WebRTC Receiver: On (Port 8080)"
    )

    # ======================================
    # WebSocket
    # ======================================

    ws_thread = threading.Thread(
        target=start_websocket_server,
        daemon=True
    )

    ws_thread.start()

    print(
        "WebSocket Server: On (Port 8765)"
    )

    # ======================================
    # AI Worker
    # ======================================

    fusion_thread = threading.Thread(
        target=data_fusion_worker,
        daemon=True
    )

    fusion_thread.start()

    # ======================================
    # Polling Loop
    # ======================================

    data_polling_manager()

# ==========================================
# Run
# ==========================================

if __name__ == "__main__":

    main()