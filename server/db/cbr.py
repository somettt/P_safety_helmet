from collections import Counter
import math
import db


def _distance(case, helmet: int, temp: float, noise: float) -> float:
    """헬멧/온도/소음을 이용한 간단 가중 유클리드 거리"""
    w_helmet = 2.0
    w_temp = 1.0
    w_noise = 1.0

    dh = (case["helmet"] - helmet) * w_helmet
    dt = (case["temp"] - temp) * w_temp
    dn = (case["noise"] - noise) * w_noise
    return math.sqrt(dh * dh + dt * dt + dn * dn)


def _cbr_from_cases(helmet: int, temp: float, noise: float, k: int = 3):
    """case_library에서 k개 이웃 찾아 다수결 위험도 리턴"""
    cases = db.get_all_cases()
    if not cases:
        return None, []

    scored = []
    for c in cases:
        dist = _distance(c, helmet, temp, noise)
        scored.append((dist, c["risk_level"]))

    scored.sort(key=lambda x: x[0])
    topk = [lvl for _, lvl in scored[:k]]

    counter = Counter(topk)
    majority = counter.most_common(1)[0][0]
    return majority, topk


def evaluate_risk(sensor: dict):
    """
    센서 JSON을 받아 CBR + 룰을 이용해
    (risk_level, risk_score, reason) 을 리턴
    """
    helmet = int(sensor.get("helmet", 0))
    temp = float(sensor.get("temp", 0.0))
    noise = float(sensor.get("noise", 0.0))

    # 1) CBR로 다수결 위험도 판단
    cbr_level, cbr_list = _cbr_from_cases(helmet, temp, noise, k=3)

    # 2) 아직 case_library가 비어있으면 룰 기반으로 판단
    if cbr_level is None:
        if helmet == 0:
            cbr_level = "HIGH"
        elif temp >= 35 or noise >= 85:
            cbr_level = "HIGH"
        elif temp >= 30 or noise >= 75:
            cbr_level = "MID"
        else:
            cbr_level = "LOW"
        cbr_list = [cbr_level]

    score_map = {"LOW": 0.2, "MID": 0.6, "HIGH": 0.9}
    score = score_map.get(cbr_level, 0.0)

    reason = (
        f"CBR 결과들={cbr_list}, 최종={cbr_level}, "
        f"helmet={helmet}, temp={temp}, noise={noise}"
    )
    return cbr_level, score, reason