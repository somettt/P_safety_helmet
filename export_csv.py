import sqlite3
import csv
import os
from server.db.config import DB_PATH

def export_table_to_csv(table_name, csv_filename):
    """
    SQLite 테이블을 CSV 파일로 내보내는 함수
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 테이블 전체 조회
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()

    col_names = [desc[0] for desc in cur.description]

    export_dir = os.path.join(os.path.dirname(DB_PATH), "log_csv")
    os.makedirs(export_dir, exist_ok=True)

    csv_path = os.path.join(export_dir, csv_filename)

    # CSV 파일 쓰기
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(col_names)   # header
        writer.writerows(rows)

    conn.close()
    print(f"[CSV EXPORT] {table_name} → {csv_path}")

def export_all():
    export_table_to_csv("sensor_log", "sensor_log.csv")
    export_table_to_csv("risk_result", "risk_result.csv")

if __name__ == "__main__":
    export_all()
