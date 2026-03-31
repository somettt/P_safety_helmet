import time

import threading
import queue
import asyncio
import websockets
import json

from camera_stream import get_frame, start_webrtc_server
from risk_analyzer import analyze
from sensor_receiver import start_mqtt, latest_sensor

from PYTHON.Safety.server.db.db_writer import insert_sensor, insert_risk

import sensor_receiver
import cv2
from camera_stream import get_frame, start_webrtc_server
from risk_analyzer import analyze
from db.db_writer import insert_sensor, insert_risk

from db.db_writer import insert_sensor, insert_risk

# 웹소켓 전역 변수 설정
connected_websocket_clients = set()
websocket_loop = None

async def echo_server(websocket, path):
    connected_websocket_clients.add(websocket)
    try:
        async for message in websocket:
            pass # 클라이언트의 메시지는 무시
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_websocket_clients.remove(websocket)

def start_websocket_server():
    global websocket_loop
    websocket_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(websocket_loop)
    start_server = websockets.serve(echo_server, "0.0.0.0", 8765)
    websocket_loop.run_until_complete(start_server)
    websocket_loop.run_forever()

# 데이터를 비동기로 동기화 및 처리하기 위한 큐 (최신 프레임 10개만 유지, 밀리면 버림)
sync_queue = queue.Queue(maxsize=10)

def data_fusion_worker():
    """
    영상과 센서 데이터를 실시간으로 합친 후 AI 분석(YOLO 등)으로 넘기는 처리 워커
    지연 시간(time.sleep) 없이 큐에 데이터가 들어오자마자 즉시 처리함.
    """
    print("[Worker] Data Fusion / AI Inference Thread: On")
    while True:
        # 큐에 들어올 때까지 대기(Blocking)하므로 CPU를 낭비하지 않음
        frame, sensor = sync_queue.get()
        
        try:
            # 실시간 AI 분석 수행
            result = analyze(frame, sensor)
            
            print(f"[AI 분석 완료] 위험도: {result['level']} | 사유: {result['reason']}")
            
            # 실시간 웹소켓 브로드캐스트
            if websocket_loop is not None and websocket_loop.is_running():
                payload = json.dumps({
                    "riskLevel": "HIGH" if result["level"] == "위험" else "MID" if result["level"] == "경고" else "LOW",
                    "temperature": sensor["temp"],
                    "noise": sensor["noise"],
                    "reason": result["reason"]
                })
                for client in list(connected_websocket_clients):
                    try:
                        asyncio.run_coroutine_threadsafe(client.send(payload), websocket_loop)
                    except Exception as e:
                        print(f"Websocket send error: {e}")
            
            # DB 저장 성능 향상을 원할 경우 이 부분도 비동기로 빼는 것이 좋습니다.
            insert_sensor(sensor["temp"], sensor["noise"])
            insert_risk(result["level"], result["reason"])
            
        except Exception as e:
            print(f"[Error] 분석 중 오류 발생: {e}")
        finally:
            sync_queue.task_done()

def data_polling_manager():
    """
    현재 camera_stream.py의 전역 변수 방식(latest_frame)과
    sensor_receiver.py(latest_sensor)를 엮어주는 브릿지 역할.
    """
    print("[Manager] Data Polling Manager: On")
    last_frame_id = None
    
    while True:
        frame = get_frame()
        sensor = latest_sensor
        
        # 두 데이터가 모두 존재하고, 이전과 다른 '새로운 프레임'일 때만 동기화 큐에 삽입
        if frame is not None and sensor is not None:
            current_frame_id = id(frame)
            if current_frame_id != last_frame_id: 
                try:
                    # (추후 과제: 이 곳에서 frame의 타임스탬프와 sensor의 타임스탬프가 ±30ms 이내인지 검사)
                    sync_queue.put_nowait((frame, sensor))
                except queue.Full:
                    pass  # 큐가 꽉 찼다면 초과된(오래된) 데이터는 안전하게 버림(Drop)
                
                last_frame_id = current_frame_id
                
        # 기존: time.sleep(1) -> FPS를 1로 강제로 낮췄던 원인
        # 개선: 10ms 단위의 짧은 슬립으로 실시간(30fps 연산)에 대응
        time.sleep(0.01)

def main():
    print("=========================================")
    print("   안전모 실시간 관제 시스템 (Optimized) ")
    print("=========================================")

    # 1) MQTT 시작 (라즈베리파이 센서 데이터 수신)
    start_mqtt()
    print("MQTT Receiver: On")
    time.sleep(1) # MQTT 연결 안정화 대기

def main():

    sensor_receiver.start_dummy_sensor()

    print("MQTT Receiver: On")
    time.sleep(1)

    start_webrtc_server()
    print("WebRTC Receiver: On")

    while True:

        frame = get_frame()
        sensor = sensor_receiver.latest_sensor

        # --------------------------
        # 프레임 상태 출력
        # --------------------------
        if frame is None:
            print("프레임 수신(x)")
        else:
            print("프레임 수신(o):", frame.shape)

        # --------------------------
        # 센서 상태 출력
        # --------------------------
        if not sensor_receiver.got_sensor:
            print("센서 데이터(x)")
        else:
            print("센서 수신(o):", sensor)

        # --------------------------
        # CBR 실행 조건 (둘 다 있음)
        # --------------------------
        if frame is not None and sensor_receiver.got_sensor:
            print("CBR 분석 실행!")
            try:
                result = analyze(frame, sensor)

                print("위험도:", result["level"])
                print("판단 사유:", result["reason"])
                print("=========================")

                insert_sensor(sensor["temp"], sensor["noise"])
                insert_risk(result["level"], result["reason"])

            except Exception as e:
                print("CBR/DB Error:", e)


        time.sleep(0.2)

        time.sleep(1)

    # 2) WebRTC 영상 수신 서버 시작 (포트 8081)
    # 기존에 포트 8080을 열던 불필요한 WebRTC_Server 로직은 제거했습니다.
    start_webrtc_server()
    print("WebRTC Receiver: On (Port 8081)")

    # 3) 실시간 웹소켓(포트 8765) 서버 쓰레드 시작
    ws_thread = threading.Thread(target=start_websocket_server, daemon=True)
    ws_thread.start()
    print("WebSocket Server: On (Port 8765)")

    # 4) 실시간 분석 워커 쓰레드 시작 (데몬 쓰레드)
    # 백그라운드에서 계속 돌면서 큐에 들어오는 즉시 위험도를 분석합니다.
    fusion_thread = threading.Thread(target=data_fusion_worker, daemon=True)
    fusion_thread.start()

    # 4) 데이터 수집 및 동기화 무한 루프 시작 (메인 쓰레드)
    data_polling_manager()

if __name__ == "__main__":
    main()
