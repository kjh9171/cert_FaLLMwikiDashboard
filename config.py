"""
애플리케이션 설정 (.env 우선, 기본값은 개발 환경용)

필수 환경 변수 예시 (.env):
    DATABASE_URL=postgresql+asyncpg://fallm:fallm@localhost:5432/fallm_db
    OLLAMA_BASE_URL=http://localhost:11434
    OLLAMA_MODEL=llama3
    EMBEDDING_MODEL=nomic-embed-text
    OCR_ENGINE=easyocr          # easyocr | paddleocr | none
    SECRET_KEY=dev-secret-change-in-production
"""
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://fallm:fallm@localhost:5432/fallm_db",
)
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
OCR_ENGINE: str = os.getenv("OCR_ENGINE", "easyocr")
SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
API_V1_STR: str = "/api/v1"
