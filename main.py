"""
================================================================================
가족 LLM WIKI & 가계부/영수증 통합 대시보드 - FastAPI 백엔드
================================================================================
Python 3.11+ | FastAPI | SQLAlchemy 2.0 (AsyncIO) |
PostgreSQL 16 + pgvector | Ollama (Llama3) | EasyOCR(선택)

실행 방법:
    pip install -r requirements.txt
    cp .env.example .env   # DATABASE_URL, OLLAMA_BASE_URL 등 설정
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

API 문서: http://localhost:8000/docs
================================================================================
"""

import json
import os
import re
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

import httpx
from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
    select,
    text,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from config import DATABASE_URL, EMBEDDING_MODEL, OLLAMA_BASE_URL, OLLAMA_MODEL
import schemas

# ---------------------------------------------------------------------------
# 데이터베이스 엔진 / 세션
# ---------------------------------------------------------------------------
engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# ORM 모델
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="family")
    avatar_color: Mapped[str] = mapped_column(String(20), default="#F7F2E9")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    calendar_events: Mapped[List["CalendarEvent"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    todos: Mapped[List["Todo"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    transactions: Mapped[List["FinanceTransaction"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_all_day: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user: Mapped["User"] = relationship(back_populates="calendar_events")


class Todo(Base):
    __tablename__ = "todos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    task: Mapped[str] = mapped_column(String(300), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user: Mapped["User"] = relationship(back_populates="todos")


class TravelChecklist(Base):
    __tablename__ = "travel_checklists"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_checked: Mapped[bool] = mapped_column(Boolean, default=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class FinanceTransaction(Base):
    __tablename__ = "finance_transactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    transaction_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # INCOME | EXPENSE
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user: Mapped["User"] = relationship(back_populates="transactions")

    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('INCOME', 'EXPENSE')",
            name="ck_transaction_type",
        ),
    )


class Receipt(Base):
    __tablename__ = "receipts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("finance_transactions.id", ondelete="SET NULL"), nullable=True
    )
    store_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    scanned_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    total_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    payment_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    raw_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    items: Mapped[List["ReceiptItem"]] = relationship(
        back_populates="receipt", cascade="all, delete-orphan"
    )


class ReceiptItem(Base):
    __tablename__ = "receipt_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    receipt_id: Mapped[int] = mapped_column(
        ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False
    )
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    item_price: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    receipt: Mapped["Receipt"] = relationship(back_populates="items")


class WikiDocument(Base):
    __tablename__ = "wiki_documents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    chunks: Mapped[List["WikiDocumentChunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class WikiDocumentChunk(Base):
    __tablename__ = "wiki_document_chunks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doc_id: Mapped[int] = mapped_column(
        ForeignKey("wiki_documents.id", ondelete="CASCADE"), nullable=False
    )
    chunk_content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # pgvector
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    document: Mapped["WikiDocument"] = relationship(back_populates="chunks")


# ---------------------------------------------------------------------------
# FastAPI 앱
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 테이블 생성 및 시드 데이터 삽입
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await seed_data(session)
    yield
    await engine.dispose()


app = FastAPI(
    title="가족 LLM WIKI & 가계부/영수증 통합 대시보드 API",
    version="1.0.0",
    description="가족 스마트 거실 월패드 및 모바일용 웹 대시보드 백엔드",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# 유틸리티 함수
# ---------------------------------------------------------------------------
def _money(v: Any) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _parse_korean_price(text: str) -> Optional[float]:
    """OCR 텍스트에서 금액 추출 (천단위 콤마, 원, OCR 오류 보정)"""
    if not text:
        return None
    cleaned = re.sub(r"[^\d.,]", "", text)
    # OCR 오류 보정: 영문자가 숫자로 오인된 경우 간단 처리
    cleaned = cleaned.replace("O", "0").replace("o", "0").replace("l", "1")
    cleaned = cleaned.replace(",", "")
    if not cleaned or cleaned == ".":
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _infer_category(store_name: str, items: List[Dict[str, Any]]) -> str:
    """상호명/품목 기반 가계부 카테고리 추론"""
    text = f"{store_name} {' '.join(i.get('item_name','') for i in items)}".lower()
    kw_map = {
        "식비": ["마트", "수퍼", "슈퍼", "편의점", "식당", "카페", "음식", "분식", "치킨", "피자", "한식", "중식", "일식"],
        "육아/교육": ["학원", "교육", "서점", "어린이집", "유치원", "도서", "학습", "수영", "피아노", "미술"],
        "주거/통신": ["아파트", "관리비", "통신", "전기", "가스", "수도", "인터넷", "핸드폰", "모바일", "임대"],
        "쇼핑/생활": ["백화점", "쇼핑몰", "쿠팡", "마켓", "생활용품", "화장품", "의류", "약국", "병원", "편의"],
    }
    for category, keywords in kw_map.items():
        for kw in keywords:
            if kw in text:
                return category
    return "기타"


async def ollama_embedding(text: str) -> Optional[List[float]]:
    """Ollama 임베딩 생성 (실패 시 None)"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{OLLAMA_BASE_URL}/api/embeddings",
                json={"model": EMBEDDING_MODEL, "prompt": text},
            )
            if resp.status_code == 200:
                data = resp.json()
                emb = data.get("embedding")
                if emb:
                    return [float(x) for x in emb]
    except Exception:
        pass
    return None


async def ollama_chat(messages: List[Dict[str, str]], temperature: float = 0.3) -> str:
    """Ollama 채팅 호출 (비스트리밍)"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": temperature},
                },
            )
            if resp.status_code == 200:
                return resp.json().get("message", {}).get("content", "")
    except Exception:
        pass
    return ""


# ---------------------------------------------------------------------------
# 시드 데이터 (초기 샘플)
# ---------------------------------------------------------------------------
async def seed_data(session: AsyncSession):
    from sqlalchemy import select as _select

    result = await session.execute(_select(User).limit(1))
    if result.scalar_one_or_none():
        return  # 이미 데이터 존재

    members = [
        User(name="하늘", role="child", avatar_color="#FBCFE8"),  # 핑크
        User(name="바다", role="child", avatar_color="#FDE047"),  # 노랑
        User(name="지훈", role="father", avatar_color="#BFDBFE"),  # 파랑
        User(name="민서", role="mother", avatar_color="#A7F3D0"),  # 초록
        User(name="가족", role="family", avatar_color="#E9D5FF"),  # 보라
    ]
    session.add_all(members)
    await session.flush()

    today = date.today()
    cal_events = [
        CalendarEvent(user_id=3, title="수영 수업", event_date=today, category="운동"),
        CalendarEvent(user_id=4, title="민서 생일파티 준비", event_date=today + timedelta(days=2), category="가족"),
        CalendarEvent(user_id=5, title="가족 외식", event_date=today + timedelta(days=5), category="외식"),
        CalendarEvent(user_id=1, title="하늘 소풍", event_date=today + timedelta(days=7), category="교육"),
        CalendarEvent(user_id=2, title="바다 병원 진료", event_date=today + timedelta(days=10), category="의료"),
        CalendarEvent(user_id=3, title="지훈 휴가", event_date=today + timedelta(days=15), category="휴가"),
    ]
    session.add_all(cal_events)

    todos = [
        Todo(user_id=3, task="수영가방 챙기기", is_completed=False, category="지훈 할 일"),
        Todo(user_id=3, task="수영복 확인", is_completed=True, category="지훈 할 일"),
        Todo(user_id=3, task="간식 준비", is_completed=False, category="지훈 할 일"),
        Todo(user_id=3, task="수건 챙기기", is_completed=False, category="지훈 할 일"),
        Todo(user_id=4, task="한글 숙제", is_completed=False, category="민서 할 일"),
        Todo(user_id=4, task="수학 문제집", is_completed=True, category="민서 할 일"),
        Todo(user_id=4, task="그림일기", is_completed=False, category="민서 할 일"),
        Todo(user_id=4, task="피아노 연습", is_completed=False, category="민서 할 일"),
        Todo(user_id=4, task="책가방 정리", is_completed=False, category="민서 할 일"),
        Todo(user_id=5, task="주말 장보기 목록 작성", is_completed=False, category="공통 할 일"),
        Todo(user_id=1, task="우유 사기", is_completed=False, category="장보기 리스트"),
        Todo(user_id=2, task="계란 사기", is_completed=False, category="장보기 리스트"),
        Todo(user_id=3, task="채소 사기", is_completed=False, category="장보기 리스트"),
        Todo(user_id=4, task="과일 사기", is_completed=False, category="장보기 리스트"),
    ]
    session.add_all(todos)

    checklist_items = [
        TravelChecklist(item_name="수영복", is_checked=False, category="의류"),
        TravelChecklist(item_name="수건", is_checked=False, category="위생"),
        TravelChecklist(item_name="세면도구", is_checked=False, category="위생"),
        TravelChecklist(item_name="썬크림", is_checked=False, category="피부"),
        TravelChecklist(item_name="모자", is_checked=False, category="의류"),
        TravelChecklist(item_name="간식", is_checked=False, category="식품"),
        TravelChecklist(item_name="물", is_checked=False, category="식품"),
        TravelChecklist(item_name="갈아입을 옷", is_checked=False, category="의류"),
        TravelChecklist(item_name="비치볼", is_checked=False, category="놀이"),
        TravelChecklist(item_name="카메라", is_checked=False, category="기타"),
        TravelChecklist(item_name="보조배터리", is_checked=False, category="전자"),
        TravelChecklist(item_name="우산", is_checked=False, category="기타"),
        TravelChecklist(item_name="담요", is_checked=False, category="침구"),
        TravelChecklist(item_name="세면타월", is_checked=False, category="위생"),
        TravelChecklist(item_name="바지", is_checked=False, category="의류"),
        TravelChecklist(item_name="양말", is_checked=False, category="의류"),
        TravelChecklist(item_name="속옷", is_checked=False, category="의류"),
        TravelChecklist(item_name="물티슈", is_checked=False, category="위생"),
        TravelChecklist(item_name="비상약", is_checked=False, category="의료"),
        TravelChecklist(item_name="현금", is_checked=False, category="기타"),
    ]
    session.add_all(checklist_items)

    transactions = [
        FinanceTransaction(user_id=5, transaction_type="INCOME", amount=3500000,
                           category="급여", transaction_date=today.replace(day=1),
                           payment_method="계좌이체", title="11월 월급"),
        FinanceTransaction(user_id=5, transaction_type="EXPENSE", amount=120000,
                           category="식비", transaction_date=today,
                           payment_method="신한카드", title="마트 장보기"),
        FinanceTransaction(user_id=5, transaction_type="EXPENSE", amount=45000,
                           category="식비", transaction_date=today,
                           payment_method="현금", title="점심 외식"),
        FinanceTransaction(user_id=5, transaction_type="EXPENSE", amount=80000,
                           category="육아/교육", transaction_date=today - timedelta(days=3),
                           payment_method="국민카드", title="학원비"),
        FinanceTransaction(user_id=5, transaction_type="EXPENSE", amount=150000,
                           category="주거/통신", transaction_date=today - timedelta(days=5),
                           payment_method="계좌이체", title="아파트 관리비"),
        FinanceTransaction(user_id=5, transaction_type="EXPENSE", amount=60000,
                           category="쇼핑/생활", transaction_date=today - timedelta(days=7),
                           payment_method="신한카드", title="생필품 구매"),
        FinanceTransaction(user_id=5, transaction_type="EXPENSE", amount=30000,
                           category="기타", transaction_date=today - timedelta(days=10),
                           payment_method="현금", title="용돈"),
        FinanceTransaction(user_id=5, transaction_type="EXPENSE", amount=220000,
                           category="쇼핑/생활", transaction_date=today - timedelta(days=12),
                           payment_method="국민카드", title="아동 의류"),
    ]
    session.add_all(transactions)

    wiki_docs = [
        WikiDocument(title="육아 매뉴얼", category="육아",
                     content="아이들 간식 시간은 오후 3시입니다. 알레르기 확인 필수. 수영 수업은 매주 화요일, 토요일 오후 4시."),
        WikiDocument(title="비상 연락처", category="비상",
                     content="119 소방서, 112 경찰서, 아이들 주치의 02-1234-5678, 동네 약국 02-2345-6789."),
        WikiDocument(title="여행 정보", category="여행",
                     content="바닷가 여행 준비물: 수영복, 타월, 썬크림, 모자, 간식, 물. 내일 출발 예정."),
        WikiDocument(title="가계부 가이드", category="가계",
                     content="식비, 육아/교육, 주거/통신, 쇼핑/생활, 기타 카테고리로 지출을 기록하세요."),
    ]
    session.add_all(wiki_docs)
    await session.flush()

    chunks = [
        WikiDocumentChunk(doc_id=1, chunk_content="아이들 간식 시간은 오후 3시입니다. 알레르기 확인 필수.", embedding=None),
        WikiDocumentChunk(doc_id=1, chunk_content="수영 수업은 매주 화요일, 토요일 오후 4시입니다.", embedding=None),
        WikiDocumentChunk(doc_id=2, chunk_content="119 소방서, 112 경찰서, 아이들 주치의 02-1234-5678, 약국 02-2345-6789.", embedding=None),
        WikiDocumentChunk(doc_id=3, chunk_content="바닷가 여행 준비물: 수영복, 타월, 썬크림, 모자, 간식, 물.", embedding=None),
        WikiDocumentChunk(doc_id=4, chunk_content="식비, 육아/교육, 주거/통신, 쇼핑/생활, 기타 카테고리로 지출을 기록하세요.", embedding=None),
    ]
    session.add_all(chunks)
    await session.commit()


# ---------------------------------------------------------------------------
# RAG: 벡터 유사도 검색 (pgvector 코사인 유사도)
# ---------------------------------------------------------------------------
async def rag_search(session: AsyncSession, query: str, top_k: int = 3) -> List[str]:
    """쿼리 임베딩으로 상위 K 청크 검색. 임베딩 불가 시 키워드 ILIKE 폴백."""
    embedding = await ollama_embedding(query)
    if embedding is not None:
        emb_str = "[" + ",".join(str(x) for x in embedding) + "]"
        sql = text(
            """
            SELECT chunk_content
            FROM wiki_document_chunks
            WHERE embedding IS NOT NULL
            ORDER BY embedding::vector <=> :q::vector
            LIMIT :k
            """
        )
        result = await session.execute(sql, {"q": emb_str, "k": top_k})
        rows = [r[0] for r in result.fetchall()]
        if rows:
            return rows

    # 폴백: 키워드 부분 일치
    like = f"%{query}%"
    result = await session.execute(
        select(WikiDocumentChunk.chunk_content).where(
            WikiDocumentChunk.chunk_content.ilike(like)
        ).limit(top_k)
    )
    rows = [r[0] for r in result.fetchall()]
    if rows:
        return rows

    # 전체 중 상위 K 반환
    result = await session.execute(
        select(WikiDocumentChunk.chunk_content).limit(top_k)
    )
    return [r[0] for r in result.fetchall()]


# ---------------------------------------------------------------------------
# 1) GET /api/v1/dashboard/summary
# ---------------------------------------------------------------------------
@app.get("/api/v1/dashboard/summary", response_model=schemas.DashboardSummary)
async def dashboard_summary(session: AsyncSession = Depends(get_session)):
    today = date.today()
    end = today + timedelta(days=14)

    # 캘린더 (향후 14일)
    cal_result = await session.execute(
        select(CalendarEvent)
        .where(CalendarEvent.event_date >= today, CalendarEvent.event_date <= end)
        .order_by(CalendarEvent.event_date, CalendarEvent.id)
    )
    calendar_events = cal_result.scalars().all()

    # 할 일 전체
    todo_result = await session.execute(select(Todo).order_by(Todo.id))
    todos = todo_result.scalars().all()

    # 여행 준비물 및 진행률
    cl_result = await session.execute(select(TravelChecklist).order_by(TravelChecklist.id))
    checklist = cl_result.scalars().all()
    total_items = len(checklist)
    checked_items = sum(1 for c in checklist if c.is_checked)
    progress = {
        "checked": checked_items,
        "total": total_items,
        "percent": round((checked_items / total_items) * 100, 1) if total_items else 0.0,
    }

    # D-Day (샘플 기념일/생일)
    dday_list = [
        {"title": "민서 생일", "date": (today.replace(month=11, day=10)), "days": (today.replace(month=11, day=10) - today).days, "category": "생일"},
        {"title": "결혼기념일", "date": (today.replace(month=11, day=20)), "days": (today.replace(month=11, day=20) - today).days, "category": "기념일"},
        {"title": "하늘 생일", "date": (today.replace(month=6, day=15)), "days": ((today.replace(month=6, day=15) if today <= today.replace(month=6, day=15) else today.replace(year=today.year + 1, month=6, day=15)) - today).days, "category": "생일"},
        {"title": "바다 생일", "date": (today.replace(month=3, day=22)), "days": ((today.replace(month=3, day=22) if today <= today.replace(month=3, day=22) else today.replace(year=today.year + 1, month=3, day=22)) - today).days, "category": "생일"},
    ]
    dday_list = [d for d in dday_list if d["days"] >= 0][:5]

    # 재무 요약 (당월)
    month_str = today.strftime("%Y-%m")
    fin_summary = await finance_summary_internal(session, month_str)

    # 날씨 (정적 데모; 실제 연동 시 기상청 API 교체)
    weather = {
        "today": {"temp": "18°", "condition": "맑음", "dust": "좋음"},
        "forecast": [
            {"day": "오늘", "temp": "18°/12°", "icon": "☀️", "dust": "좋음"},
            {"day": "금", "temp": "16°/10°", "icon": "⛅", "dust": "보통"},
            {"day": "토", "temp": "15°/9°", "icon": "🌤️", "dust": "좋음"},
            {"day": "일", "temp": "14°/8°", "icon": "🌥️", "dust": "보통"},
            {"day": "월", "temp": "13°/7°", "icon": "🌦️", "dust": "나쁨"},
            {"day": "화", "temp": "12°/6°", "icon": "☁️", "dust": "보통"},
            {"day": "수", "temp": "11°/5°", "icon": "🌧️", "dust": "보통"},
        ],
    }

    return schemas.DashboardSummary(
        calendar_events=[schemas.CalendarEvent.model_validate(e) for e in calendar_events],
        todos=[schemas.Todo.model_validate(t) for t in todos],
        travel_checklist=[schemas.TravelChecklist.model_validate(c) for c in checklist],
        travel_progress=progress,
        d_day=dday_list,
        finance=fin_summary,
        weather=weather,
    )


async def finance_summary_internal(session: AsyncSession, month: str) -> schemas.FinanceSummary:
    year, mon = month.split("-")
    start_date = date(int(year), int(mon), 1)
    if int(mon) == 12:
        end_date = date(int(year) + 1, 1, 1)
    else:
        end_date = date(int(year), int(mon) + 1, 1)

    result = await session.execute(
        select(FinanceTransaction).where(
            FinanceTransaction.transaction_date >= start_date,
            FinanceTransaction.transaction_date < end_date,
        )
    )
    txs = result.scalars().all()

    total_income = sum(_money(t.amount) for t in txs if t.transaction_type == "INCOME")
    total_expense = sum(_money(t.amount) for t in txs if t.transaction_type == "EXPENSE")

    exp_by_cat: Dict[str, float] = {}
    inc_by_cat: Dict[str, float] = {}
    for t in txs:
        amt = _money(t.amount)
        cat = t.category or "기타"
        if t.transaction_type == "EXPENSE":
            exp_by_cat[cat] = exp_by_cat.get(cat, 0) + amt
        else:
            inc_by_cat[cat] = inc_by_cat.get(cat, 0) + amt

    budget = 3000000  # 예산 기준 (원)
    budget_usage = round((total_expense / budget) * 100, 1) if budget else 0.0

    return schemas.FinanceSummary(
        month=month,
        total_income=round(total_income, 2),
        total_expense=round(total_expense, 2),
        net_savings=round(total_income - total_expense, 2),
        expense_by_category=[schemas.CategoryAggregate(category=k, total=round(v, 2)) for k, v in exp_by_cat.items()],
        income_by_category=[schemas.CategoryAggregate(category=k, total=round(v, 2)) for k, v in inc_by_cat.items()],
        budget_usage_percent=budget_usage,
    )


# ---------------------------------------------------------------------------
# 2) POST /api/v1/receipts/scan
# ---------------------------------------------------------------------------
@app.post("/api/v1/receipts/scan", response_model=schemas.ReceiptParseResult)
async def receipt_scan(
    file: Optional[UploadFile] = File(None),
    ocr_text: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session),
):
    """
    영수증 이미지 OCR 파싱.
    - file 업로드 시 EasyOCR(설치됨)이 있으면 이미지 -> 텍스트 변환 후 파싱.
    - ocr_text 직접 전달 또는 데모 모드(텍스트 없음) 시 샘플 텍스트 파싱.
    """
    raw_text = ocr_text or ""

    if file is not None and not raw_text:
        contents = await file.read()
        # EasyOCR 선택적 사용
        try:
            import easyocr  # type: ignore
            import numpy as np
            from PIL import Image
            import io

            reader = easyocr.Reader(["ko", "en"], gpu=False)
            image = Image.open(io.BytesIO(contents)).convert("RGB")
            result = reader.readtext(np.array(image))
            raw_text = "\n".join([item[1] for item in result])
        except Exception:
            # EasyOCR unavailable -> 파일명 기반 데모 텍스트
            raw_text = f"""
            {file.filename or '영수증'}
            2026-11-05 14:30
            마트 상점명
            우유 2,500 x 2
            계란 6,000
            채소 12,000
            합계 23,000
            신한카드
            """

    if not raw_text.strip():
        raw_text = """
        샘플 마트
        2026-11-05 14:30
        우유 2500 x 2 = 5000
        계란 6000
        채소 12000
        총 합계 23000
        결제: 신한카드
        """

    # LLM 기반 정밀 파싱 시도 (Ollama 사용 가능 시)
    parsed: Optional[Dict[str, Any]] = None
    system_prompt_path = os.path.join("prompts", "receipt_parser_system_prompt.md")
    system_prompt = ""
    if os.path.exists(system_prompt_path):
        with open(system_prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

    chat_response = await ollama_chat(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"OCR 텍스트:\n{raw_text}"},
        ],
        temperature=0.1,
    )

    if chat_response:
        json_match = re.search(r"```json\n(.*?)\n```", chat_response, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                parsed = None

    # 폴백: 정규식 기반 단순 파서
    if not parsed:
        total_match = re.search(r"(?:총\s*합계|합계|total|총액)\D*([\d,]+)", raw_text, re.IGNORECASE)
        total_amount = _parse_korean_price(total_match.group(1)) if total_match else 0.0

        date_match = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", raw_text)
        time_match = re.search(r"(\d{1,2}):(\d{2})", raw_text)
        scanned_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        if date_match:
            scanned_at = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
            if time_match:
                scanned_at += f" {time_match.group(1).zfill(2)}:{time_match.group(2)}"

        payment = "현금"
        for pm in ["신한카드", "국민카드", "현금", "계좌이체", "삼성카드", "현대카드", "롯데카드"]:
            if pm in raw_text:
                payment = pm
                break

        store_name = "Unknown"
        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
        for l in lines[:3]:
            if not re.search(r"\d", l) and len(l) > 1:
                store_name = l
                break

        items = []
        for l in lines:
            price = _parse_korean_price(l)
            if price is not None:
                name = re.sub(r"[\d,\s]+", "", l).strip()
                if name:
                    items.append({"item_name": name or "품목", "item_price": price, "quantity": 1})

        category = _infer_category(store_name, items)

        parsed = {
            "store_name": store_name,
            "scanned_at": scanned_at,
            "total_amount": total_amount,
            "payment_method": payment,
            "items": items,
            "suggested_category": category,
        }

    # 필수 필드 보정
    parsed.setdefault("store_name", "Unknown")
    parsed.setdefault("scanned_at", datetime.now().strftime("%Y-%m-%d %H:%M"))
    parsed.setdefault("total_amount", 0.0)
    parsed.setdefault("payment_method", "현금")
    parsed.setdefault("items", [])
    parsed.setdefault("suggested_category", "기타")

    # 항목 합계가 total과 다르면 보정 (간단: 품목 중 가장 큰 값 또는 합계 사용)
    try:
        items_sum = sum(float(it.get("item_price", 0)) * int(it.get("quantity", 1)) for it in parsed["items"])
        if items_sum > 0 and float(parsed["total_amount"]) == 0:
            parsed["total_amount"] = items_sum
    except Exception:
        pass

    return schemas.ReceiptParseResult(**parsed)


# ---------------------------------------------------------------------------
# 3) GET /api/v1/finance/summary?month=YYYY-MM
# ---------------------------------------------------------------------------
@app.get("/api/v1/finance/summary", response_model=schemas.FinanceSummary)
async def finance_summary(
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$", description="YYYY-MM"),
    session: AsyncSession = Depends(get_session),
):
    return await finance_summary_internal(session, month)


# ---------------------------------------------------------------------------
# 4) POST /api/v1/llm/chat (RAG + Function Calling)
# ---------------------------------------------------------------------------
@app.post("/api/v1/llm/chat", response_model=schemas.ChatResponse)
async def llm_chat(
    payload: schemas.ChatMessage,
    session: AsyncSession = Depends(get_session),
):
    system_prompt_path = os.path.join("prompts", "ollama_family_agent_system_prompt.md")
    system_prompt = ""
    if os.path.exists(system_prompt_path):
        with open(system_prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

    # RAG: 관련 청크 검색
    context_chunks = await rag_search(session, payload.message, top_k=3)
    context_text = "\n".join(f"- {c}" for c in context_chunks) if context_chunks else "(관련 문서 없음)"

    messages = [
        {"role": "system", "content": system_prompt + "\n\n### 컨텍스트 (RAG):\n" + context_text},
        {"role": "user", "content": payload.message},
    ]

    response_text = await ollama_chat(messages, temperature=0.4)

    # Function Call 파싱
    function_call: Optional[schemas.FunctionCall] = None
    json_match = re.search(r"```json\n(.*?)\n```", response_text, re.DOTALL)
    if json_match:
        try:
            fc = json.loads(json_match.group(1))
            if "tool" in fc and "arguments" in fc:
                function_call = schemas.FunctionCall(name=fc["tool"], arguments=fc["arguments"])
                # 텍스트에서 JSON 블록 제거하여 순수 응답만 남김
                response_text = response_text.replace(json_match.group(0), "").strip()
        except json.JSONDecodeError:
            pass

    # Function Call 후속 처리 (DB 반영)
    if function_call:
        try:
            await handle_function_call(session, function_call)
        except Exception as exc:
            response_text += f"\n\n(도구 실행 중 오류: {exc})"

    return schemas.ChatResponse(
        response=response_text or "죄송합니다. 잠시 후 다시 시도해 주세요.",
        function_call=function_call,
        context_chunks=context_chunks,
    )


async def handle_function_call(session: AsyncSession, fc: schemas.FunctionCall):
    name = fc.name
    args = fc.arguments or {}

    if name == "add_calendar_event":
        user_name = args.get("user_name", "가족")
        # 사용자 조회/생성
        result = await session.execute(select(User).where(User.name == user_name).limit(1))
        user = result.scalar_one_or_none()
        if not user:
            user = User(name=user_name, role="family")
            session.add(user)
            await session.flush()
        event = CalendarEvent(
            user_id=user.id,
            title=args.get("title", "일정"),
            event_date=date.fromisoformat(args.get("date", date.today().isoformat())),
            category=args.get("category", "일정"),
            is_all_day=False,
        )
        session.add(event)
        await session.commit()

    elif name == "add_todo_item":
        user_name = args.get("user_name", "가족")
        result = await session.execute(select(User).where(User.name == user_name).limit(1))
        user = result.scalar_one_or_none()
        if not user:
            user = User(name=user_name, role="family")
            session.add(user)
            await session.flush()
        todo = Todo(
            user_id=user.id,
            task=args.get("task", "할 일"),
            category="할 일",
        )
        session.add(todo)
        await session.commit()

    elif name == "query_finance_summary":
        # 조회 전용: 변경 없음
        pass

    else:
        raise ValueError(f"Unknown tool: {name}")


# ---------------------------------------------------------------------------
# 보조 CRUD 엔드포인트 (프론트엔드 데이터 연동용)
# ---------------------------------------------------------------------------

@app.get("/api/v1/users", response_model=List[schemas.User])
async def list_users(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).order_by(User.id))
    return result.scalars().all()


@app.get("/api/v1/calendar/events", response_model=List[schemas.CalendarEvent])
async def list_calendar_events(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(CalendarEvent).order_by(CalendarEvent.event_date, CalendarEvent.id))
    return result.scalars().all()


@app.post("/api/v1/calendar/events", response_model=schemas.CalendarEvent, status_code=status.HTTP_201_CREATED)
async def create_calendar_event(
    payload: schemas.CalendarEventCreate, session: AsyncSession = Depends(get_session)
):
    event = CalendarEvent(**payload.model_dump())
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


@app.get("/api/v1/todos", response_model=List[schemas.Todo])
async def list_todos(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Todo).order_by(Todo.id))
    return result.scalars().all()


@app.post("/api/v1/todos", response_model=schemas.Todo, status_code=status.HTTP_201_CREATED)
async def create_todo(payload: schemas.TodoCreate, session: AsyncSession = Depends(get_session)):
    todo = Todo(**payload.model_dump())
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return todo


@app.patch("/api/v1/todos/{todo_id}", response_model=schemas.Todo)
async def update_todo(todo_id: int, payload: schemas.TodoUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(todo, k, v)
    await session.commit()
    await session.refresh(todo)
    return todo


@app.get("/api/v1/travel/checklists", response_model=List[schemas.TravelChecklist])
async def list_travel_checklists(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(TravelChecklist).order_by(TravelChecklist.id))
    return result.scalars().all()


@app.post("/api/v1/travel/checklists", response_model=schemas.TravelChecklist, status_code=status.HTTP_201_CREATED)
async def create_travel_checklist(payload: schemas.TravelChecklistCreate, session: AsyncSession = Depends(get_session)):
    item = TravelChecklist(**payload.model_dump())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@app.patch("/api/v1/travel/checklists/{item_id}", response_model=schemas.TravelChecklist)
async def update_travel_checklist(item_id: int, payload: schemas.TravelChecklistUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(TravelChecklist).where(TravelChecklist.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    await session.commit()
    await session.refresh(item)
    return item


@app.get("/api/v1/finance/transactions", response_model=List[schemas.FinanceTransaction])
async def list_transactions(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(FinanceTransaction).order_by(FinanceTransaction.transaction_date.desc(), FinanceTransaction.id))
    return result.scalars().all()


@app.post("/api/v1/finance/transactions", response_model=schemas.FinanceTransaction, status_code=status.HTTP_201_CREATED)
async def create_transaction(payload: schemas.FinanceTransactionCreate, session: AsyncSession = Depends(get_session)):
    tx = FinanceTransaction(**payload.model_dump())
    session.add(tx)
    await session.commit()
    await session.refresh(tx)
    return tx


@app.get("/api/v1/wiki/documents", response_model=List[schemas.WikiDocument])
async def list_wiki_documents(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(WikiDocument).order_by(WikiDocument.id))
    return result.scalars().all()


@app.post("/api/v1/wiki/documents", response_model=schemas.WikiDocument, status_code=status.HTTP_201_CREATED)
async def create_wiki_document(payload: schemas.WikiDocumentCreate, session: AsyncSession = Depends(get_session)):
    doc = WikiDocument(**payload.model_dump())
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return doc


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "service": "family-dashboard-api"}
