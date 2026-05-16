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


# --------------------------------------------------
# DB 폴더 생성
# --------------------------------------------------

if not os.path.exists(BASE_DIR):

    os.makedirs(BASE_DIR)


# --------------------------------------------------
# Sensor INSERT
# --------------------------------------------------

def insert_sensor(temp, noise):

    conn = None

    try:

        conn = sqlite3.connect(
            DB_PATH,
            timeout=5
        )

        cur = conn.cursor()

        cur.execute("""
            INSERT INTO sensor_data
            (temp, noise)
            VALUES (?, ?)
        """, (temp, noise))

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

        conn = sqlite3.connect(
            DB_PATH,
            timeout=5
        )

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