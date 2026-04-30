import asyncio
import json
import aiohttp
import os
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

SIGNALING_SERVER_URL = "http://127.0.0.1:8080/offer"
DEVICE_ID = "helmet_001"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUMMY_VIDEO_PATH = os.path.join(BASE_DIR, "sample.mp4")

async def run():
    pc = RTCPeerConnection()

    player = MediaPlayer(DUMMY_VIDEO_PATH)

    if player.video:
        pc.addTrack(player.video)
    else:
        print("[ERR] video track not found in file")
        return

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    async with aiohttp.ClientSession() as session:
        payload = {
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type,
            "device_id": DEVICE_ID,
        }
        async with session.post(SIGNALING_SERVER_URL, json=payload) as resp:
            answer_json = await resp.json()

    answer = RTCSessionDescription(
        sdp=answer_json["sdp"],
        type=answer_json["type"],
    )
    await pc.setRemoteDescription(answer)

    print("[WebRTC] Connected, streaming dummy video...")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("[WebRTC] Closing...")
    finally:
        await pc.close()


if __name__ == "__main__":
    asyncio.run(run())
