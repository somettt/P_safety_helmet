import json
import math

# ================================================
# 1) CASE LIBRARY LOAD
# ================================================
with open("case_library.json", "r") as f:
    try:
        CASES = json.load(f)
    except:
        CASES = []

# ================================================
# 2) SIMILARITY FUNCTION
# ================================================
def similarity(case, new):
    score = 0
    score += 0.4 * abs(case["helmet"] - new["helmet"])
    score += 0.3 * (case.get("pose", 0) != new.get("pose", 0))
    score += 0.2 * abs(case["noise"] - new["noise"])
    score += 0.1 * abs(case["temp"] - new["temp"])
    return score

# ================================================
# 3) KNN CBR (핵심 판단)
# ================================================
def knn_cbr(new_case, k=3):
    if len(CASES) == 0:
        return "LOW"

    ranked = sorted(CASES, key=lambda c: similarity(c, new_case))
    top = ranked[:k]
    levels = [c["label"] for c in top]

    return max(set(levels), key=levels.count)

# ================================================
# 4) Rule-based (가중치 낮게)
# ================================================
def rule_cbr(case):
    if case["helmet"] == 0:
        return "HIGH"
    if case["noise"] > 85:
        return "MID"
    if case["temp"] > 37:
        return "MID"

    return "LOW"

# ================================================
# 5) Weighted CBR (보조 모델)
# ================================================
def weighted_cbr(case):
    score = (
        0.5 * (case["helmet"] == 0) +
        0.3 * (case["noise"] / 100) +
        0.2 * (case["temp"] / 50)
    )

    if score > 0.7:
        return "HIGH"
    elif score > 0.4:
        return "MID"
    return "LOW"

# ================================================
# 6) ENSEMBLE (가중 다수결)
# ================================================
def ensemble_cbr(case):
    knn = knn_cbr(case)
    rule = rule_cbr(case)
    wcb = weighted_cbr(case)

    # 가중치 설정
    weights = {
        knn: 0.5,    # 가장 중요
        wcb: 0.3,    # 중간
        rule: 0.2    # 가장 낮음
    }

    # 위험도별 합산 점수 계산
    score = {"LOW": 0, "MID": 0, "HIGH": 0}
    for label, w in weights.items():
        score[label] += w

    # 최종 라벨 선택
    final = max(score, key=score.get)

    return final, {"knn": knn, "weighted": wcb, "rule": rule, "score": score}
