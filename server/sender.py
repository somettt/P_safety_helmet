# sender_test.py
import asyncio
import aiohttp
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
import cv2
import av
import numpy as np

SIGNALING_URL = "http://127.0.0.1:8080/offer"

class DummyVideo(VideoStreamTrack):
    async def recv(self):
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 200
        frame = av.VideoFrame.from_ndarray(frame, format="bgr24")
        frame.pts, frame.time_base = await self.next_timestamp()
        return frame

async def run():
    pc = RTCPeerConnection()

    pc.addTrack(DummyVideo())

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    async with aiohttp.ClientSession() as session:
        answer = await session.post(SIGNALING_URL, json={
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        })
        ans = await answer.json()

    await pc.setRemoteDescription(
        RTCSessionDescription(sdp=ans["sdp"], type=ans["type"])
    )

    print("Dummy video streaming...")

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(run())
