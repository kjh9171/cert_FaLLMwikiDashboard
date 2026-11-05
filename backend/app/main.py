from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from backend.app.config import settings
from backend.app.db.init_db import init_database
from backend.app.api import (
    finance, receipts, wiki, llm, calendar, todos, health
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database and Seed Baseline Data
    print("🚀 Initializing Family LLM WIKI Database & Seed Data...")
    init_database()
    print("✅ Database ready.")
    yield
    print("🛑 Shutting down Family LLM WIKI Backend Service.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="가족 WIKI 비서 및 가계/영수증 통합 인텔리전스 백엔드 API",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Uploads directory for uploaded receipt images
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(finance.router, prefix=f"{settings.API_V1_STR}/finance", tags=["Finance"])
app.include_router(receipts.router, prefix=f"{settings.API_V1_STR}/receipts", tags=["Receipts"])
app.include_router(wiki.router, prefix=f"{settings.API_V1_STR}/wiki", tags=["Wiki"])
app.include_router(llm.router, prefix=f"{settings.API_V1_STR}/llm", tags=["LLM & RAG"])
app.include_router(calendar.router, prefix=f"{settings.API_V1_STR}/calendar", tags=["Calendar"])
app.include_router(todos.router, prefix=f"{settings.API_V1_STR}", tags=["Todos & Checklist"])
app.include_router(health.router, prefix=f"{settings.API_V1_STR}", tags=["Health"])

@app.get("/")
def root():
    return {
        "message": f"{settings.PROJECT_NAME} v{settings.VERSION} is running.",
        "docs_url": "/docs",
        "health_check": f"{settings.API_V1_STR}/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)

