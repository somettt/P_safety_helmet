import sqlite3
from datetime import datetime

DB_PATH = "server/db/smart_helmet.db"

def insert_sensor(temp, noise, timestamp=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if timestamp is None:
        timestamp = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO sensor_log (timestamp, temp, noise)
        VALUES (?, ?, ?)
    """, (timestamp, temp, noise))

    conn.commit()
    conn.close()


def insert_risk(risk_level, reason, timestamp=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if timestamp is None:
        timestamp = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO risk_result (timestamp, risk_level, reason)
        VALUES (?, ?, ?)
    """, (timestamp, risk_level, reason))

    conn.commit()
    conn.close()
