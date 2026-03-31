import asyncio
import threading
import cv2
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaStreamTrack
from aiohttp import web

latest_frame = None  # WebRTC로 받은 최신 프레임 저장

#WebRTC영상을 가로채서 처리
#
#
#
#
class VideoReceiver(MediaStreamTrack):
    kind = "video"

    def __init__(self, track):
        super().__init__()
        self.track = track

    async def recv(self):
        global latest_frame
        frame = await self.track.recv()     #원본영상 받음

        img = frame.to_ndarray(format="bgr24")  #OpenCV용 ndarray로 변환
        latest_frame = img      #최신프레임 저장

        return frame            #원본프레임 반환


async def offer(request):   #WebRTC 연결을 시작
    params = await request.json()   #클라이언트 offer 받기
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()    #연결

    @pc.on("track")     #클라이언트가 영상을 보내면 실행
    def on_track(track):
        if track.kind == "video":
            pc.addTrack(VideoReceiver(track))

    await pc.setRemoteDescription(offer)    #WebRTC 표준 절차
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response(
        {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
    )   #클라이언트로 SDP 대답 전달


def start_webrtc_server():  #WebRTC 서버 실행
    app = web.Application()
    app.router.add_post("/offer", offer)

    # aiohttp 서버를 새 스레드에서 실행
    def run():
        web.run_app(app, port=8080)

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