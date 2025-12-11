import sqlite3

db_path = "server/db/smart_helmet.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

with open("server/db/create_tables.sql", "r", encoding="utf-8") as f:
    sql = f.read()

cursor.executescript(sql)
conn.commit()
conn.close()

print("DB 초기화 완료!")
