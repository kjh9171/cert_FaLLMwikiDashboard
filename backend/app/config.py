import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "가족 LLM WIKI & 가계/영수증 통합 플랫폼"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "1.3.0"
    PORT: int = int(os.getenv("PORT", "8088"))
    
    # Database URL: 기본값으로 sqlite3 파일 사용, PostgreSQL 연결 시 DATABASE_URL 환경변수로 덮어쓰기
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/family_wiki.db")
    
    # Ollama LLM Settings
    OLLAMA_API_BASE: str = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    
    # File Upload Directory
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    class Config:
        case_sensitive = True

settings = Settings()

# Ensure uploads directory exists
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
