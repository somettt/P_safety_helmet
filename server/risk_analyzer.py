# risk_analyzer.py

import math
from case_library import load_cases
from feature_extractor import detect_helmet


# ======================================================
# 1) KNN CBR
# ======================================================
def cbr_knn(case, library, k=3):
    distances = []

    for lib_case in library:
        dist = math.sqrt(
            (case["helmet"] - lib_case["helmet"]) ** 2 +
            (case["temp"] - lib_case["temp"]) ** 2 +
            (case["noise"] - lib_case["noise"]) ** 2
        )
        distances.append((dist, lib_case["label"]))

    distances.sort(key=lambda x: x[0])
    neighbors = distances[:k]
    labels = [label for _, label in neighbors]

    if labels.count("HIGH") >= 2:
        return "HIGH"
    elif labels.count("MID") >= 2:
        return "MID"
    else:
        return "LOW"


# ======================================================
# 2) Rule-based CBR
# ======================================================
def cbr_rule(case):

    # 헬멧 미착용은 최우선 규칙 (여기선 사용되지 않지만 참고)
    if case["helmet"] == 0:
        return "HIGH"

    if case["temp"] > 60:
        return "HIGH"

    if case["noise"] > 85:
        return "HIGH"

    if case["temp"] > 40 or case["noise"] > 70:
        return "MID"

    return "LOW"


# ======================================================
# 3) Weighted CBR
# ======================================================
def cbr_weighted(case, library):
    score = (
        (1 - case["helmet"]) * 30 +    # 헬멧 미착용 → 위험 점수 크게
        case["temp"] * 0.4 +
        case["noise"] * 0.4
    )

    if score > 60:
        return "HIGH"
    elif score > 40:
        return "MID"
    else:
        return "LOW"


# ======================================================
# 4) CBR 통합 판단
# ======================================================
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


# ======================================================
# 5) 실제 시스템용 최종 분석 함수
# ======================================================
def analyze(frame, latest_sensor):

    # ------------------------------------------------------
    # YOLO 헬멧 탐지 (0 = 미착용, 1 = 착용)
    # ------------------------------------------------------
    helmet_status = detect_helmet(frame)

    temp = latest_sensor.get("temp", 25.0)
    noise = latest_sensor.get("noise", 50.0)

    reasons = []

    # ------------------------------------------------------------------
    # 1) 헬멧 미착용 → 시스템 최우선 규칙 = 무조건 HIGH
    # ------------------------------------------------------------------
    if helmet_status == 0:
        reasons.append("헬멧 미착용")

        # 추가 센서 위험 요소가 있다면 사유에 포함
        if temp > 30:
            reasons.append(f"고온({temp}°C)")
        if noise > 75:
            reasons.append(f"고소음({noise}dB)")

        return {
            "level": "HIGH",
            "reason": ", ".join(reasons),
            "raw_results": ["NO_HELMET_OVERRIDE"]
        }

    # ------------------------------------------------------
    # 2) 헬멧 착용한 경우 → CBR 기반 통합 판단 사용
    # ------------------------------------------------------
    cbr_case = {
        "helmet": helmet_status,
        "temp": temp,
        "noise": noise
    }

    cbr_result = analyze_cbr(cbr_case)
    final_risk = cbr_result["final_risk"]

    # ------------------------------------------------------
    # 3) 이유 텍스트 생성
    # ------------------------------------------------------
    if temp > 30:
        reasons.append(f"고온({temp}°C)")
    if noise > 75:
        reasons.append(f"고소음({noise}dB)")
    if not reasons:
        reasons.append("안전 상태")

    return {
        "level": final_risk,
        "reason": ", ".join(reasons),
        "raw_results": cbr_result["cbr_results"]
    }
