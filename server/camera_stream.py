import asyncio
import threading
import cv2
import numpy as np
import time
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaStreamTrack
from aiohttp import web

latest_frame = None  # {"frame", "device_id", "frame_id", "arrival_utc_ms"}

#WebRTC영상을 가로채서 처리
#
#
#
#
class VideoReceiver(MediaStreamTrack):
    kind = "video"

    def __init__(self, track, device_id):
        super().__init__()
        self.track = track
        self.device_id = device_id

    async def recv(self):
        global latest_frame
        frame = await self.track.recv()     #원본영상 받음

        img = frame.to_ndarray(format="bgr24")  #OpenCV용 ndarray로 변환
        now_ms = int(time.time() * 1000)
        latest_frame = {
            "frame": img,
            "device_id": self.device_id,
            "frame_id": f"{self.device_id}-{now_ms}",
            "arrival_utc_ms": now_ms,
        }

        return frame            #원본프레임 반환


async def offer(request):   #WebRTC 연결을 시작
    params = await request.json()   #클라이언트 offer 받기
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    device_id = params.get("device_id", "unknown_device")

    pc = RTCPeerConnection()    #연결

    @pc.on("track")     #클라이언트가 영상을 보내면 실행
    def on_track(track):
        if track.kind == "video":
            pc.addTrack(VideoReceiver(track, device_id))

    await pc.setRemoteDescription(offer)    #WebRTC 표준 절차
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response(
        {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
    )   #클라이언트로 SDP 대답 전달


def start_webrtc_server():  #WebRTC 서버 실행
    app = web.Application()
    app.router.add_post("/offer", offer)

    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        web.run_app(app, port=8080, handle_signals=False)

    t = threading.Thread(target=run, daemon=True)
    t.start()


def get_frame():
    global latest_frame
    return latest_frame

#[클라이언트]
#   ↓ (SDP offer)
#POST /offer
#   ↓
#[서버]
#RTCPeerConnection 생성
#   ↓
#영상 track 수신
#   ↓
#VideoReceiver.recv()
#   ↓
#frame → ndarray 변환
#   ↓
#latest_frame 저장
#   ↓
#(SDP answer 반환)

#WebRTC로 들어온 영상 프레임을 
#OpenCV 이미지로 변환해서 실시간으로 
#가져다 쓸 수 있게 만든 서버 코드
