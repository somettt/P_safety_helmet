import sys
import gi
import cv2
import numpy as np

gi.require_version('Gst', '1.0')
gi.require_version('GstWebRTC', '1.0')
gi.require_version('GstSdp', '1.0')
from gi.repository import Gst, GObject, GstWebRTC, GstSdp

Gst.init(sys.argv)

class WebRTCReceiverGeneric:
    def __init__(self):
        # decodebin을 사용하여 시스템에 맞는 최적의 디코더(Mac의 vtdec, Linux의 avdec_h264 등)를 자동 선택합니다.
        pipeline_desc = (
            "webrtcbin name=recv_webrtc "
            "! decodebin " # 범용 디코더 자동 할당
            "! videoconvert "
            "! video/x-raw, format=BGR "
            "! appsink name=appsink emit-signals=True sync=False max-buffers=1 drop=True"
        )
        
        print("[WebRTC] GStreamer 파이프라인 생성 중...")
        self.pipeline = Gst.parse_launch(pipeline_desc)
        
        # WebRTC 객체 가져오기
        self.webrtc = self.pipeline.get_by_name("recv_webrtc")
        
        # WebRTC 연결 이벤트를 위한 Signal 연결 (예시)
        # self.webrtc.connect("on-negotiation-needed", self.on_negotiation_needed)
        # self.webrtc.connect("on-ice-candidate", self.on_ice_candidate)
        
        # appsink에서 디코딩 완료된 프레임 가져오기
        self.appsink = self.pipeline.get_by_name("appsink")
        self.appsink.connect("new-sample", self.on_new_sample)
        
        # 파이프라인 실행
        self.pipeline.set_state(Gst.State.PLAYING)

    def on_new_sample(self, sink):
        # appsink로부터 샘플 하나를 뽑아냄
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()
        
        # 메타데이터 (가로/세로)
        width = caps.get_structure(0).get_value('width')
        height = caps.get_structure(0).get_value('height')
        
        # 메모리 블록을 numpy 배열로 변환
        success, map_info = buf.map(Gst.MapFlags.READ)
        if success:
            ndarray = np.ndarray(
                (height, width, 3),
                buffer=map_info.data,
                dtype=np.uint8
            )
            # 수신된 프레임을 YOLO 추론 로직으로 전달
            self.run_yolo_inference(ndarray)
            buf.unmap(map_info)
        return Gst.FlowReturn.OK

    def run_yolo_inference(self, frame):
        # TODO: YOLO 모델 추론 로직 삽입
        # 이 프레임은 MQTT 타임스탬프와 동기화하여 처리해야 합니다.
        
        # 화면 출력 테스트용 (GUI 환경에서만 동작)
        cv2.imshow("WebRTC Generic Decoded", frame)
        cv2.waitKey(1)

# 메인 루프 실행
if __name__ == '__main__':
    demo = WebRTCReceiverGeneric()
    loop = GObject.MainLoop()
    try:
        print("[WebRTC] 대기 중... (범용 디코더 사용)")
        loop.run()
    except KeyboardInterrupt:
        print("[WebRTC] 종료 중...")
        demo.pipeline.set_state(Gst.State.NULL)
