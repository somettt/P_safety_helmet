# import_raw.py
import csv
from datetime import datetime
import db   # 이미 있는 db.py 사용

RAW_FILE = "raw_data.csv" 


def load_raw_data(csv_path: str):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # CSV 문자열을 float/int로 변환
            data = {
                "helmet": int(row["helmet"]),
                "temp": float(row["temp"]),
                "noise": float(row["noise"]),
                # timestamp도 넘기고 싶으면 여기에 추가
                "timestamp": row["timestamp"],
            }

            # db.py 안에 있던 함수 사용 
            sensor_id = db.insert_sensor_log(data)

            print(f"[IMPORT] sensor_id={sensor_id}, data={data}")


if __name__ == "__main__":
    print("=== RAW DATA IMPORT START ===")
    load_raw_data(RAW_FILE)
    print("=== DONE ===")