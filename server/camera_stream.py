import asyncio
import threading
import time
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiohttp import web

# 🔥 최신 프레임 저장
latest_frame = None

# 연결 관리 (선택이지만 안정성 ↑)
pcs = set()


# ============================================
# 영상 수신 처리
# ============================================
async def consume_video(track, device_id):
    global latest_frame

    print(f"[WebRTC] Receiving video from {device_id}")

    while True:
        frame = await track.recv()

        img = frame.to_ndarray(format="bgr24")

        now_ms = int(time.time() * 1000)

        latest_frame = {
            "frame": img,
            "device_id": device_id,
            "frame_id": f"{device_id}-{now_ms}",
            "arrival_utc_ms": now_ms,
        }

        # 🔥 디버깅용 (너무 많으면 주석)
        # print("Frame received")


# ============================================
# WebRTC offer 처리
# ============================================
async def offer(request):
    params = await request.json()

    device_id = params.get("device_id", "unknown_device")

    pc = RTCPeerConnection()
    pcs.add(pc)

    print(f"[WebRTC] Client connected: {device_id}")

    @pc.on("track")
    def on_track(track):
        if track.kind == "video":
            print("[WebRTC] Video track received")

            # 🔥 핵심: addTrack ❌ → consume만
            asyncio.create_task(consume_video(track, device_id))

    # SDP 처리
    offer = RTCSessionDescription(
        sdp=params["sdp"],
        type=params["type"]
    )

    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })


# ============================================
# 서버 실행
# ============================================
def start_webrtc_server():
    app = web.Application()
    app.router.add_post("/offer", offer)

    async def on_shutdown(app):
        coros = [pc.close() for pc in pcs]
        await asyncio.gather(*coros)

    app.on_shutdown.append(on_shutdown)

    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        print("[WebRTC] Server started (port 8080)")
        web.run_app(app, port=8080, handle_signals=False)

    t = threading.Thread(target=run, daemon=True)
    t.start()


# ============================================
# 외부에서 프레임 가져오기
# ============================================
def get_frame():
    global latest_frame
    return latest_frame