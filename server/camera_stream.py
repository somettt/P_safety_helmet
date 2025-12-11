import asyncio
import threading
import cv2
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaStreamTrack
from aiohttp import web

latest_frame = None  # WebRTC로 받은 최신 프레임 저장

class VideoReceiver(MediaStreamTrack):
    kind = "video"

    def __init__(self, track):
        super().__init__()
        self.track = track

    async def recv(self):
        global latest_frame
        frame = await self.track.recv()

        img = frame.to_ndarray(format="bgr24")
        latest_frame = img

        return frame


async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()

    @pc.on("track")
    def on_track(track):
        if track.kind == "video":
            pc.addTrack(VideoReceiver(track))

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response(
        {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
    )


def start_webrtc_server():
    app = web.Application()
    app.router.add_post("/offer", offer)

    # aiohttp 서버를 새 스레드에서 실행
    def run():
        web.run_app(app, port=8081)

    t = threading.Thread(target=run, daemon=True)
    t.start()


def get_frame():
    global latest_frame
    return latest_frame
