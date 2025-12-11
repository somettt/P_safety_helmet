import json
import os

def load_cases():
    # 현재 파일 기준 상위 폴더(Safety)로 이동하여 case_library.json 찾기
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_path, "case_library.json")

    with open(json_path, "r") as f:
        return json.load(f)
