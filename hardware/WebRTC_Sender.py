import asyncio
import json
import aiohttp
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

SIGNALING_SERVER_URL = "http://172.20.10.5:8080/offer"  # 시그널링 서버
DUMMY_VIDEO_PATH = "sample.mp4"  # 데모임

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