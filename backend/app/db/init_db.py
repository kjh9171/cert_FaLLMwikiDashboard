import time
from datetime import date
from sqlalchemy import text
from backend.app.db.session import engine, SessionLocal, Base
from backend.app.db.models import FinanceCategory

MAX_DB_RETRIES = 10
DB_RETRY_DELAY = 2  # seconds


def wait_for_db():
    """데이터베이스 연결이 가능할 때까지 재시도 (Docker Compose 시작 순서 대응)"""
    for attempt in range(1, MAX_DB_RETRIES + 1):
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            print(f"✅ 데이터베이스 연결 성공 (시도 {attempt}/{MAX_DB_RETRIES})")
            return True
        except Exception as e:
            print(f"⏳ 데이터베이스 연결 대기 중... (시도 {attempt}/{MAX_DB_RETRIES}): {e}")
            if attempt < MAX_DB_RETRIES:
                time.sleep(DB_RETRY_DELAY)
    print("❌ 데이터베이스 연결 실패 - 최대 재시도 횟수 초과")
    return False


DEFAULT_CATEGORIES = [
    FinanceCategory(category_code="식비", category_name="식비", transaction_type="EXPENSE", icon_symbol="🍲", display_order=1),
    FinanceCategory(category_code="육아/교육", category_name="육아/교육", transaction_type="EXPENSE", icon_symbol="👶", display_order=2),
    FinanceCategory(category_code="주거/통신", category_name="주거/통신", transaction_type="EXPENSE", icon_symbol="🏠", display_order=3),
    FinanceCategory(category_code="쇼핑/생활", category_name="쇼핑/생활", transaction_type="EXPENSE", icon_symbol="🛒", display_order=4),
    FinanceCategory(category_code="기타", category_name="기타 지출", transaction_type="EXPENSE", icon_symbol="💸", display_order=5),
    FinanceCategory(category_code="월급/수입", category_name="월급/수입", transaction_type="INCOME", icon_symbol="💰", display_order=6),
]


def ensure_default_categories():
    """실제 사용을 위해 최소한의 기본 재무 카테고리만 보장 (시드 데이터 아님)"""
    db = SessionLocal()
    try:
        if db.query(FinanceCategory).count() == 0:
            db.add_all(DEFAULT_CATEGORIES)
            db.commit()
            print("✅ 기본 재무 카테고리 생성 완료 (실제 데이터 입력 준비)")
        else:
            print("✅ 기존 재무 카테고리 유지됨")
    finally:
        db.close()


def reset_and_init_database():
    """데이터베이스 테이블만 재생성 (목/시드 데이터 없음).

    실제 운영 데이터는 API를 통해 직접 입력하세요.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ensure_default_categories()
    print("✅ Database tables created (no mock/seed data).")


def init_database():
    """앱 시작 시 호출: 테이블 생성 및 기본 카테고리 보장.

    DB 연결 실패 시 앱이 크래시하지 않고 재시도 후 계속 진행합니다.
    """
    wait_for_db()
    Base.metadata.create_all(bind=engine)
    ensure_default_categories()


if __name__ == "__main__":
    reset_and_init_database()
