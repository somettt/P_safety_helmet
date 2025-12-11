import os

# ==============================================
# 프로젝트 루트(Safety 폴더) 절대경로 계산
# ==============================================
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

# ==============================================
# SQLite DB 파일 경로
# ==============================================
DB_PATH = os.path.join(BASE_DIR, "server", "db", "smart_helmet.db")

# 디버깅 용 출력
print(f"[DB CONFIG] Loaded DB_PATH: {DB_PATH}")
