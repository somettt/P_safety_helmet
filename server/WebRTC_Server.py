import asyncio
import json
import logging
import threading

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("signaling")

pcs = set()

async def offer(request: web.Request) -> web.Response:
 
    params = await request.json()
    logger.info("Received offer: %s", params.get("type"))

    offer = RTCSessionDescription(
        sdp=params["sdp"],
        type=params["type"],
    )

    pc = RTCPeerConnection()
    pcs.add(pc)
    logger.info("Created PeerConnection %s", id(pc))

    # 현재는 영상 프레임을 버림
    media_sink = MediaBlackhole()

    @pc.on("track")
    async def on_track(track):
        logger.info("Track %s received", track.kind)
        print("수신 연결 완료 (WebRTC)")
        await media_sink.start()
        try:
            while True:
                frame = await track.recv()
                print("정상 수신 중 (WebRTC)")
        except Exception as e:
            logger.info("Track %s finished (%s)", track.kind, e)
            print(">>> 영상 수신 종료")

    # Remote SDP 적용
    await pc.setRemoteDescription(offer)

    # Answer 생성 및 적용
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    logger.info("Sending answer")

    return web.json_response(
        {
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type,
        }
    )

async def on_shutdown(app: web.Application):
    # 서버 종료 시 열린 PeerConnection 정리
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


def start_webrtc_signaling_server():

    def run():
        app = web.Application()
        app.router.add_post("/offer", offer)
        app.on_shutdown.append(on_shutdown)

        web.run_app(app, host="0.0.0.0", port=8080)

    t = threading.Thread(target=run, daemon=True)
    t.start()
    print("[WebRTC] On (Port: 8080)")
