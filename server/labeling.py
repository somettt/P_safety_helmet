import pandas as pd
import json
import random
import os
import pandas as pd

# Case.py 파일이 위치한 폴더 기준으로 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data.csv")

print("CSV PATH:", CSV_PATH)

df = pd.read_csv(CSV_PATH)

# -------------------------
# 1) 위험도 평가 함수
# -------------------------

def temp_risk(temp):
    if temp >= 37:
        return "HIGH"
    elif temp >= 33:
        return "MID"
    else:
        return "LOW"

def noise_risk(noise):
    if noise >= 90:
        return "HIGH"
    elif noise >= 85:
        return "MID"
    else:
        return "LOW"

def final_label(temp, noise):
    t = temp_risk(temp)
    n = noise_risk(noise)

    if t == "HIGH" or n == "HIGH":
        return "HIGH"
    if t == "MID" or n == "MID":
        return "MID"
    return "LOW"


# -------------------------
# 2) CSV 로드
# -------------------------

df = pd.read_csv(CSV_PATH)

# Temperature, Sound_dB 컬럼 포함 가정

case_list = []


# -------------------------
# 3) 각 row를 CBR case로 변환
# -------------------------

for idx, row in df.iterrows():
    temp = float(row["Temperature_C"])
    noise = float(row["Sound_dB"])

    # helmet은 랜덤 0 또는 1 생성
    helmet = random.choice([0, 1])

    label = final_label(temp, noise)

    case = {
        "helmet": helmet,
        "temp": round(temp, 2),
        "noise": round(noise, 2),
        "label": label
    }

    case_list.append(case)


# -------------------------
# 4) JSON 파일로 저장
# -------------------------

with open("case_library.json", "w", encoding="utf-8") as f:
    json.dump(case_list, f, indent=4)

print(f"완료! 총 {len(case_list)}개의 사례가 저장되었습니다.")
