import json
import os

def load_cases():
    # 현재 파일 기준 상위 폴더(Safety)로 이동하여 case_library.json 찾기
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_path, "case_library.json")

    with open(json_path, "r") as f:
        return json.load(f)

#현재 .py 파일 위치
#   ↓
#상위 폴더(Safety)로 이동
#   ↓
#case_library.json 찾기
#   ↓
#파일 읽기
#   ↓
#Python dict로 반환

#현재 파일 위치 기준으로 상위 폴더의 
#JSON 파일을 안정적으로 읽어오는 함수