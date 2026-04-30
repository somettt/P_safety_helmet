import asyncio
import json
import aiohttp
import cv2
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from av import VideoFrame

SIGNALING_SERVER_URL = "http://192.168.72.123:8080/offer"
DEVICE_ID = "helmet_001"


class CameraStreamTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            print("[ERR] Camera open failed")

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        ret, frame = self.cap.read()
        if not ret:
            print("[ERR] Camera read failed")
            await asyncio.sleep(0.01)
            return await self.recv()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        return video_frame


async def run():
    print(">>> WebRTC(OpenCV) 시작")

    pc = RTCPeerConnection()

    track = CameraStreamTrack()
    pc.addTrack(track)

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type,
                "device_id": DEVICE_ID,
            }

            async with session.post(SIGNALING_SERVER_URL, json=payload) as resp:
                print("[DEBUG] status:", resp.status)
                text = await resp.text()
                print("[DEBUG] response:", text)

                answer_json = json.loads(text)

    except Exception as e:
        print("[WebRTC ERROR]:", e)
        return

    answer = RTCSessionDescription(
        sdp=answer_json["sdp"],
        type=answer_json["type"],
    )

    await pc.setRemoteDescription(answer)

    print("[WebRTC] Connected (Camera Streaming)")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("종료")
    finally:
        await pc.close()


if __name__ == "__main__":
    asyncio.run(run())