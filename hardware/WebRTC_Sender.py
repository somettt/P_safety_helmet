import asyncio
import json
import aiohttp
import cv2
import numpy as np

from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    VideoStreamTrack,
)

from av import VideoFrame


SERVER_IP = "172.20.10.2"

SIGNALING_SERVER_URL = (
    f"http://{SERVER_IP}:8080/offer"
)

DEVICE_ID = "helmet_001"
CAMERA_INDEXES = (0, 1, 2)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FRAME_FPS = 15


class CameraStreamTrack(VideoStreamTrack):

    def __init__(self):

        super().__init__()

        self.cap = self.open_camera()

        if not self.cap.isOpened():
            print("[ERR] Camera open failed")

        else:
            print("[INFO] Camera opened")

    def open_camera(self):

        for index in CAMERA_INDEXES:

            cap = cv2.VideoCapture(index)

            if not cap.isOpened():

                cap.release()

                continue

            cap.set(
                cv2.CAP_PROP_FRAME_WIDTH,
                FRAME_WIDTH
            )

            cap.set(
                cv2.CAP_PROP_FRAME_HEIGHT,
                FRAME_HEIGHT
            )

            cap.set(
                cv2.CAP_PROP_FPS,
                FRAME_FPS
            )

            ret, _frame = cap.read()

            if ret:

                print(f"[INFO] Camera index {index} opened")

                return cap

            cap.release()

        return cv2.VideoCapture(-1)

    async def recv(self):

        pts, time_base = await self.next_timestamp()

        ret, frame = self.cap.read()

        if not ret:

            print("[ERR] Camera read failed")

            await asyncio.sleep(0.01)

            blank_frame = np.zeros(
                (
                    FRAME_HEIGHT,
                    FRAME_WIDTH,
                    3
                ),
                dtype=np.uint8
            )

            blank = VideoFrame.from_ndarray(
                blank_frame,
                format="rgb24"
            )

            blank.pts = pts
            blank.time_base = time_base

            return blank

        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        video_frame = VideoFrame.from_ndarray(
            frame,
            format="rgb24"
        )

        video_frame.pts = pts
        video_frame.time_base = time_base

        return video_frame

    def stop(self):

        super().stop()

        if self.cap.isOpened():

            print("[INFO] Camera released")

            self.cap.release()


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

            async with session.post(
                SIGNALING_SERVER_URL,
                json=payload
            ) as resp:

                print("[DEBUG] status:", resp.status)

                text = await resp.text()

                print("[DEBUG] response:", text)

                if resp.status != 200:

                    raise RuntimeError(
                        f"Signaling failed: {resp.status} {text}"
                    )

                answer_json = json.loads(text)

    except Exception as e:

        print("[WebRTC ERROR]:", e)

        track.stop()

        await pc.close()

        return

    answer = RTCSessionDescription(
        sdp=answer_json["sdp"],
        type=answer_json["type"],
    )

    await pc.setRemoteDescription(answer)

    print("[WebRTC] Connected")

    try:

        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:

        print("[INFO] 종료")

    finally:

        track.stop()

        await pc.close()

        print("[INFO] WebRTC closed")


if __name__ == "__main__":

    asyncio.run(run())
