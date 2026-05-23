from db_writer import (
    DB_PATH,
    get_connection,
    insert_analysis_result,
    insert_risk,
    insert_sensor,
)


def fetch_count(conn, table_name):
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cur.fetchone()[0]


def fetch_latest(conn, table_name):
    cur = conn.cursor()
    cur.execute(
        f"""
            SELECT *
            FROM {table_name}
            ORDER BY id DESC
            LIMIT 1
        """
    )
    return cur.fetchone()


def main():
    print(f"[DB TEST] path={DB_PATH}")

    insert_sensor(26.5, 72.3)
    insert_risk("MID", "DB writer direct insert test")
    insert_analysis_result({
        "device_id": "helmet_test",
        "helmet": 0,
        "risk": "HIGH",
        "sensor": {
            "temp": "41.2",
            "noise": "86.7",
        },
    })

    conn = get_connection()

    try:
        sensor_count = fetch_count(conn, "sensor_data")
        risk_count = fetch_count(conn, "risk_data")
        latest_sensor = fetch_latest(conn, "sensor_data")
        latest_risk = fetch_latest(conn, "risk_data")

        assert sensor_count > 0
        assert risk_count > 0
        assert latest_sensor is not None
        assert latest_risk is not None

        print(f"[DB TEST] sensor_data count={sensor_count}")
        print(f"[DB TEST] risk_data count={risk_count}")
        print(f"[DB TEST] latest sensor={latest_sensor}")
        print(f"[DB TEST] latest risk={latest_risk}")
        print("[DB TEST] PASS")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
