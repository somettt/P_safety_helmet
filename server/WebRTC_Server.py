import asyncio
import json
import logging

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("signaling")

pcs = set()
async def offer(request: web.Request) -> web.Response:
    """
    라즈베리파이에서 보내는 SDP offer를 받고
    SDP answer를 반환하는 엔드포인트
    """
    params = await request.json()
    logger.info("Received offer: %s", params.get("type"))

    offer = RTCSessionDescription(
        sdp=params["sdp"],
        type=params["type"],
    )

    pc = RTCPeerConnection()
    pcs.add(pc)
    logger.info("Created PeerConnection %s", id(pc))

    # 영상은 일단 버리는 싱크 (나중에 여기서 프레임 뽑아서 AI 분석하면 됨)
    media_sink = MediaBlackhole()

    @pc.on("track")
    async def on_track(track):
        logger.info("Track %s received", track.kind)
        await media_sink.start()
        try:
            while True:
                frame = await track.recv()
                # TODO: 여기서 frame을 AI 분석 레이어로 넘길 수 있음
                # 일단은 버림
        except Exception as e:
            logger.info("Track %s finished (%s)", track.kind, e)

    # remote(=Pi) SDP 적용
    await pc.setRemoteDescription(offer)

    # answer 생성 및 적용
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
    # 서버 내려갈 때 열린 PeerConnection 정리
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


def main():
    app = web.Application()
    app.router.add_post("/offer", offer)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()