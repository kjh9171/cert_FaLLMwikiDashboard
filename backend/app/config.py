"""
백엔드 설정 (환경변수 우선, 미설정 시 기본값)

Docker Compose 주입 환경 변수 예시:
    DATABASE_URL=postgresql://family_admin:super_secure_family_password_2026@family-db:5432/family_wiki_db
    OLLAMA_API_BASE=http://family-ollama:11434
    OLLAMA_MODEL=llama3
    EMBEDDING_MODEL=nomic-embed-text
    OCR_ENGINE=easyocr
    SECRET_KEY=dev-secret-change-in-production
"""
import os

def _normalize_database_url(url: str | None) -> str:
    """SQLAlchemy asyncpg 엔진용으로 postgresql:// -> postgresql+asyncpg:// 정규화."""
    if not url:
        return "postgresql+asyncpg://family_admin:super_secure_family_password_2026@localhost:5435/family_wiki_db"
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url

DATABASE_URL: str = _normalize_database_url(os.getenv("DATABASE_URL"))
# Docker Compose는 OLLAMA_API_BASE, 로컬 실행은 OLLAMA_BASE_URL을 사용
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_API_BASE") or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
OCR_ENGINE: str = os.getenv("OCR_ENGINE", "easyocr")
SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
API_V1_STR: str = "/api/v1"
