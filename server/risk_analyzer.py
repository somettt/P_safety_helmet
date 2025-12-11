# risk_analyzer.py

import math
from case_library import load_cases
from feature_extractor import detect_helmet


def cbr_knn(case, library, k=3):
    distances = []

    for lib_case in library:
        dist = math.sqrt(
            (case["helmet"] - lib_case["helmet"]) ** 2 +
            (case["temp"] - lib_case["temp"]) ** 2 +
            (case["noise"] - lib_case["noise"]) ** 2
        )
        distances.append((dist, lib_case["label"]))

    # 거리 기반 정렬
    distances.sort(key=lambda x: x[0])

    # 상위 K개 선택
    neighbors = distances[:k]
    labels = [label for _, label in neighbors]

    # 다수결
    if labels.count("HIGH") >= 2:
        return "HIGH"
    elif labels.count("MID") >= 2:
        return "MID"
    else:
        return "LOW"



def cbr_rule(case):
    # 상황 1: 헬멧 미착용 + 고온(>30°C)
    if case["helmet"] == 0 and case["temp"] > 30:
        return "HIGH"

    # 상황 2: 75dB 이상 고소음
    if case["noise"] > 75:
        return "MID"

    return "LOW"


def cbr_weighted(case, library):
    score = (
        (1 - case["helmet"]) * 20 +    # 헬멧 미착용: 높은 위험 기여
        case["temp"] * 0.4 +           # 온도 기여
        case["noise"] * 0.4            # 소음 기여
    )

    if score > 60:
        return "HIGH"
    elif score > 40:
        return "MID"
    else:
        return "LOW"


def analyze_cbr(case):
    library = load_cases()

    r1 = cbr_knn(case, library)
    r2 = cbr_rule(case)
    r3 = cbr_weighted(case, library)

    results = [r1, r2, r3]

    if "HIGH" in results:
        final = "HIGH"
    elif "MID" in results:
        final = "MID"
    else:
        final = "LOW"

    return {
        "case": case,
        "cbr_results": results,
        "final_risk": final
    }


def analyze(frame, latest_sensor):
    """
    frame → YOLO 헬멧 탐지
    latest_sensor → MQTT로 들어온 temp + noise
    출력 → 위험도 + 이유
    """

    # 1) YOLO 헬멧 착용 여부 (0 = 미착용, 1 = 착용)
    helmet_status = detect_helmet(frame)

    # 2) CBR 입력 케이스 생성
    cbr_case = {
        "helmet": helmet_status,
        "temp": latest_sensor.get("temp", 25.0),
        "noise": latest_sensor.get("noise", 50.0)
    }

    # 3) CBR 분석
    cbr_result = analyze_cbr(cbr_case)
    final_risk = cbr_result["final_risk"]

    # 4) 위험 판단 사유 텍스트 생성
    reasons = []

    if helmet_status == 0:
        reasons.append("헬멧 미착용")
    if cbr_case["temp"] > 30:
        reasons.append(f"고온({cbr_case['temp']}°C)")
    if cbr_case["noise"] > 75:
        reasons.append(f"고소음({cbr_case['noise']}dB)")

    if not reasons:
        reason_str = "안전 상태"
    else:
        reason_str = ", ".join(reasons)

    # 5) 최종 결과 반환
    return {
        "level": final_risk,
        "reason": reason_str,
        "raw_results": cbr_result["cbr_results"]
    }
