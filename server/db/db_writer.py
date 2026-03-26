import os
import sqlite3

# --------------------------------------------------
# 1) DB 절대경로 설정
# --------------------------------------------------
# 이 파일(db_writer.py)이 위치한 폴더의 절대경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
# → C:/Users/parkn/OneDrive/CLOUD/VSCODE/PYTHON/Safety/server/db

# DB 파일 실제 위치
DB_PATH = os.path.join(BASE_DIR, "smart_helmet.db")

# --------------------------------------------------
# 2) DB 파일이 있는 폴더가 없으면 생성 (예외 방지)
# --------------------------------------------------
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# --------------------------------------------------
# 3) INSERT 함수들
# --------------------------------------------------
def insert_sensor(temp, noise):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO sensor_data (temp, noise)
            VALUES (?, ?)
        """, (temp, noise))

        conn.commit()
        conn.close()

    except Exception as e:
        print("[DB ERROR] Sensor Insert Error:", e)


def insert_risk(level, reason):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO risk_data (level, reason)
            VALUES (?, ?)
        """, (level, reason))

        conn.commit()
        conn.close()

    except Exception as e:
        print("[DB ERROR] Risk Insert Error:", e)
