"""
Pydantic v2 데이터 검증 모델 (요청/응답 스키마)
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# 사용자
# ---------------------------------------------------------------------------
class UserBase(BaseModel):
    name: str
    role: str = "family"
    avatar_color: str = "#F7F2E9"


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# 캘린더 일정
# ---------------------------------------------------------------------------
class CalendarEventBase(BaseModel):
    user_id: int
    title: str
    event_date: date
    category: Optional[str] = None
    is_all_day: bool = False


class CalendarEventCreate(CalendarEventBase):
    pass


class CalendarEvent(CalendarEventBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# 할 일
# ---------------------------------------------------------------------------
class TodoBase(BaseModel):
    user_id: int
    task: str
    is_completed: bool = False
    category: Optional[str] = None


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    task: Optional[str] = None
    is_completed: Optional[bool] = None
    category: Optional[str] = None


class Todo(TodoBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# 여행 준비물 체크리스트
# ---------------------------------------------------------------------------
class TravelChecklistBase(BaseModel):
    item_name: str
    is_checked: bool = False
    category: Optional[str] = None


class TravelChecklistCreate(TravelChecklistBase):
    pass


class TravelChecklistUpdate(BaseModel):
    item_name: Optional[str] = None
    is_checked: Optional[bool] = None
    category: Optional[str] = None


class TravelChecklist(TravelChecklistBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# 가계부 거래 내역
# ---------------------------------------------------------------------------
class FinanceTransactionBase(BaseModel):
    user_id: int
    transaction_type: str = Field(..., pattern="^(INCOME|EXPENSE)$")
    amount: float = Field(..., gt=0)
    category: Optional[str] = None
    transaction_date: date
    payment_method: Optional[str] = None
    title: Optional[str] = None


class FinanceTransactionCreate(FinanceTransactionBase):
    pass


class FinanceTransaction(FinanceTransactionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# 영수증 / 영수증 품목
# ---------------------------------------------------------------------------
class ReceiptItemBase(BaseModel):
    item_name: str
    item_price: float = Field(..., ge=0)
    quantity: int = Field(default=1, ge=1)


class ReceiptBase(BaseModel):
    store_name: Optional[str] = None
    scanned_at: Optional[datetime] = None
    total_amount: Optional[float] = None
    payment_method: Optional[str] = None
    raw_image_url: Optional[str] = None


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptItem(ReceiptItemBase):
    id: int
    receipt_id: int

    model_config = ConfigDict(from_attributes=True)


class Receipt(ReceiptBase):
    id: int
    transaction_id: Optional[int] = None
    items: List[ReceiptItem] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# 영수증 OCR 파싱 결과 (LLM/정규식 파서 출력)
# ---------------------------------------------------------------------------
class ReceiptParseResult(BaseModel):
    store_name: str
    scanned_at: str  # "YYYY-MM-DD HH:MM"
    total_amount: float
    payment_method: str
    items: List[ReceiptItemBase]
    suggested_category: str


# ---------------------------------------------------------------------------
# 위키 문서
# ---------------------------------------------------------------------------
class WikiDocumentBase(BaseModel):
    title: str
    category: Optional[str] = None
    content: str


class WikiDocumentCreate(WikiDocumentBase):
    pass


class WikiDocument(WikiDocumentBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# 위키 청크
# ---------------------------------------------------------------------------
class WikiChunkBase(BaseModel):
    doc_id: int
    chunk_content: str


class WikiChunkCreate(WikiChunkBase):
    pass


class WikiChunk(WikiChunkBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# LLM 챗
# ---------------------------------------------------------------------------
class ChatMessage(BaseModel):
    message: str
    user_name: Optional[str] = "가족"


class FunctionCall(BaseModel):
    name: str
    arguments: dict


class ChatResponse(BaseModel):
    response: str
    function_call: Optional[FunctionCall] = None
    context_chunks: List[str] = []


# ---------------------------------------------------------------------------
# 재무 요약
# ---------------------------------------------------------------------------
class CategoryAggregate(BaseModel):
    category: str
    total: float


class FinanceSummary(BaseModel):
    month: str
    total_income: float
    total_expense: float
    net_savings: float
    expense_by_category: List[CategoryAggregate]
    income_by_category: List[CategoryAggregate]
    budget_usage_percent: float = 0.0


# ---------------------------------------------------------------------------
# 대시보드 요약
# ---------------------------------------------------------------------------
class DashboardSummary(BaseModel):
    calendar_events: List[CalendarEvent]
    todos: List[Todo]
    travel_checklist: List[TravelChecklist]
    travel_progress: dict  # {checked, total, percent}
    d_day: List[dict]
    finance: FinanceSummary
    weather: dict
