import asyncio
import json
import aiohttp
import cv2

from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    VideoStreamTrack,
)

from av import VideoFrame


SERVER_IP = "192.168.72.123"

SIGNALING_SERVER_URL = (
    f"http://{SERVER_IP}:8080/offer"
)

DEVICE_ID = "helmet_001"


class CameraStreamTrack(VideoStreamTrack):

    def __init__(self):

        super().__init__()

        # 라즈베리파이 카메라 안정성 향상
        self.cap = cv2.VideoCapture(
            0,
            cv2.CAP_V4L2
        )

        if not self.cap.isOpened():
            print("[ERR] Camera open failed")

        else:
            print("[INFO] Camera opened")

    async def recv(self):

        pts, time_base = await self.next_timestamp()

        ret, frame = self.cap.read()

        if not ret:

            print("[ERR] Camera read failed")

            await asyncio.sleep(0.01)

            # 재귀 호출 제거
            blank = VideoFrame.from_ndarray(
                cv2.cvtColor(
                    cv2.imread("black.jpg")
                    if cv2.imread("black.jpg") is not None
                    else
                    cv2.cvtColor(
                        cv2.UMat(480, 640, cv2.CV_8UC3).get(),
                        cv2.COLOR_BGR2RGB
                    ),
                    cv2.COLOR_BGR2RGB
                ),
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