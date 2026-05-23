import json
import math
import os

# ================================================
# 1) CASE LIBRARY LOAD
# ================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASE_LIBRARY_PATH = os.path.join(BASE_DIR, "case_library.json")
NOISE_DBFS_OFFSET = 100.0


def normalize_helmet(value):
    if value is None:
        return 1

    return 0 if int(value) == 0 else 1


def normalize_noise(value):
    noise = float(value)
    return noise + NOISE_DBFS_OFFSET if noise < 0 else noise


def normalize_case(case):
    return {
        "helmet": normalize_helmet(case.get("helmet", 1)),
        "pose": case.get("pose", 0),
        "noise": normalize_noise(case.get("noise", 50.0)),
        "temp": float(case.get("temp", 25.0)),
        "label": case.get("label"),
    }


with open(CASE_LIBRARY_PATH, "r") as f:
    try:
        CASES = [
            normalize_case(case)
            for case in json.load(f)
            if case.get("label") in ("LOW", "MID", "HIGH")
        ]
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

    new_case = normalize_case(new_case)
    ranked = sorted(CASES, key=lambda c: similarity(c, new_case))
    top = ranked[:k]
    levels = [c["label"] for c in top]

    return max(set(levels), key=levels.count)

# ================================================
# 4) Rule-based (가중치 낮게)
# ================================================
def rule_cbr(case):
    case = normalize_case(case)

    if case["helmet"] == 0:
        return "HIGH"
    if case["noise"] > 85:
        return "HIGH"
    if case["temp"] > 60:
        return "HIGH"
    if case["noise"] > 70 or case["temp"] > 40:
        return "MID"

    return "LOW"

# ================================================
# 5) Weighted CBR (보조 모델)
# ================================================
def weighted_cbr(case):
    case = normalize_case(case)

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
    case = normalize_case(case)

    if case["helmet"] == 0:
        return "HIGH", {
            "knn": None,
            "weighted": None,
            "rule": "HIGH",
            "score": {"LOW": 0, "MID": 0, "HIGH": 1.0},
        }

    if case["temp"] > 60 or case["noise"] > 85:
        return "HIGH", {
            "knn": None,
            "weighted": None,
            "rule": "HIGH",
            "score": {"LOW": 0, "MID": 0, "HIGH": 1.0},
        }

    knn = knn_cbr(case)
    rule = rule_cbr(case)
    wcb = weighted_cbr(case)

    # 위험도별 합산 점수 계산
    score = {"LOW": 0, "MID": 0, "HIGH": 0}
    score[knn] += 0.5
    score[wcb] += 0.3
    score[rule] += 0.2

    # 최종 라벨 선택
    final = max(score, key=score.get)

    if final == "LOW" and (case["temp"] > 40 or case["noise"] > 70):
        final = "MID"

    return final, {"knn": knn, "weighted": wcb, "rule": rule, "score": score}

#이 파일은 여러 판단 모델을 결합해서 
#위험도를 결정하는 의사결정 엔진이다
