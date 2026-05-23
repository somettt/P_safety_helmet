import os
import sqlite3


# --------------------------------------------------
# DB 절대경로 설정
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_PATH = os.path.join(
    BASE_DIR,
    "smart_helmet.db"
)

CREATE_SENSOR_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        temp REAL,
        noise REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
"""

CREATE_RISK_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS risk_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        level TEXT,
        reason TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
"""


# --------------------------------------------------
# DB 폴더 생성
# --------------------------------------------------

if not os.path.exists(BASE_DIR):

    os.makedirs(BASE_DIR)


def get_connection():
    conn = sqlite3.connect(
        DB_PATH,
        timeout=5
    )

    conn.execute(CREATE_SENSOR_TABLE_SQL)
    conn.execute(CREATE_RISK_TABLE_SQL)

    return conn


def to_float(value):
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# --------------------------------------------------
# Sensor INSERT
# --------------------------------------------------

def insert_sensor(temp, noise):

    conn = None

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""
            INSERT INTO sensor_data
            (temp, noise)
            VALUES (?, ?)
        """, (
            float(temp),
            float(noise)
        ))

        conn.commit()

    except Exception as e:

        print(
            "[DB ERROR] Sensor Insert Error:",
            e
        )

    finally:

        if conn:

            conn.close()


# --------------------------------------------------
# Risk INSERT
# --------------------------------------------------

def insert_risk(level, reason):

    conn = None

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""
            INSERT INTO risk_data
            (level, reason)
            VALUES (?, ?)
        """, (level, reason))

        conn.commit()

    except Exception as e:

        print(
            "[DB ERROR] Risk Insert Error:",
            e
        )

    finally:

        if conn:

            conn.close()


def insert_analysis_result(result):
    sensor = result.get("sensor", {})
    temp = to_float(sensor.get("temp"))
    noise = to_float(sensor.get("noise"))

    if temp is not None and noise is not None:
        insert_sensor(temp, noise)

    risk = result.get("risk", "LOW")
    helmet = result.get("helmet")

    reasons = []

    if helmet == 0:
        reasons.append("헬멧 미착용")

    if temp is not None and temp > 40:
        reasons.append(f"고온({temp:.1f}°C)")

    if noise is not None and noise > 70:
        reasons.append(f"고소음({noise:.1f}dB)")

    if not reasons:
        reasons.append("안전 상태")

    insert_risk(
        risk,
        ", ".join(reasons)
    )
