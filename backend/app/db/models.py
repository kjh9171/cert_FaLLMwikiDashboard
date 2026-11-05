import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean, Date, DateTime, Float, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(50), nullable=False)
    role = Column(String(20), nullable=False)  # ADMIN, MEMBER, CHILD
    color_code = Column(String(20), nullable=False)
    avatar_initial = Column(String(5), nullable=False)
    birth_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("FinanceTransaction", back_populates="user")
    todos = relationship("Todo", back_populates="user")
    calendar_events = relationship("CalendarEvent", back_populates="user")
    growth_logs = relationship("ChildGrowthLog", back_populates="child_user")

class FinanceCategory(Base):
    __tablename__ = "finance_categories"

    category_code = Column(String(30), primary_key=True)
    category_name = Column(String(50), nullable=False)
    transaction_type = Column(String(10), nullable=False)  # INCOME, EXPENSE
    icon_symbol = Column(String(10), nullable=True)
    display_order = Column(Integer, default=0)

    transactions = relationship("FinanceTransaction", back_populates="category_rel")
    budgets = relationship("FinanceBudget", back_populates="category_rel")

class FinanceBudget(Base):
    __tablename__ = "finance_budgets"

    budget_id = Column(String(36), primary_key=True, default=generate_uuid)
    year_month = Column(String(7), nullable=False)  # e.g. '2026-11'
    category_code = Column(String(30), ForeignKey("finance_categories.category_code", ondelete="CASCADE"), nullable=False)
    budget_amount = Column(Numeric(12, 0), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category_rel = relationship("FinanceCategory", back_populates="budgets")

class Receipt(Base):
    __tablename__ = "receipts"

    receipt_id = Column(String(36), primary_key=True, default=generate_uuid)
    store_name = Column(String(100), nullable=False)
    transaction_datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    total_amount = Column(Numeric(12, 0), nullable=False)
    tax_amount = Column(Numeric(12, 0), default=0)
    image_url = Column(String(255), nullable=True)
    ocr_confidence = Column(Float, default=0.95)
    scan_status = Column(String(20), default="PARSED")  # PENDING, PARSED, CONFIRMED
    scanned_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("ReceiptItem", back_populates="receipt", cascade="all, delete-orphan")
    transaction = relationship("FinanceTransaction", back_populates="receipt_rel", uselist=False)

class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    item_id = Column(String(36), primary_key=True, default=generate_uuid)
    receipt_id = Column(String(36), ForeignKey("receipts.receipt_id", ondelete="CASCADE"), nullable=False)
    item_name = Column(String(100), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(12, 0), nullable=False)
    total_price = Column(Numeric(12, 0), nullable=False)

    receipt = relationship("Receipt", back_populates="items")

class FinanceTransaction(Base):
    __tablename__ = "finance_transactions"

    transaction_id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    category_code = Column(String(30), ForeignKey("finance_categories.category_code"), nullable=False)
    transaction_type = Column(String(10), nullable=False)  # INCOME, EXPENSE
    title = Column(String(100), nullable=False)
    amount = Column(Numeric(12, 0), nullable=False)
    transaction_date = Column(Date, nullable=False)
    payment_method = Column(String(30), nullable=False)
    receipt_id = Column(String(36), ForeignKey("receipts.receipt_id", ondelete="SET NULL"), nullable=True)
    memo = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")
    category_rel = relationship("FinanceCategory", back_populates="transactions")
    receipt_rel = relationship("Receipt", back_populates="transaction")

class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    event_id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    title = Column(String(100), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_all_day = Column(Boolean, default=False)
    category = Column(String(30), nullable=False)
    color_tag = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="calendar_events")

class Todo(Base):
    __tablename__ = "todos"

    todo_id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="todos")

class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    item_id = Column(String(36), primary_key=True, default=generate_uuid)
    context_type = Column(String(50), default="TRIP_SOKCHO")
    category = Column(String(50), nullable=False)
    item_name = Column(String(100), nullable=False)
    is_checked = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)

class ChildGrowthLog(Base):
    __tablename__ = "child_growth_logs"

    log_id = Column(String(36), primary_key=True, default=generate_uuid)
    child_user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    record_date = Column(Date, nullable=False)
    height_cm = Column(Numeric(5, 1), nullable=False)
    weight_kg = Column(Numeric(5, 1), nullable=True)
    vaccine_name = Column(String(100), nullable=True)
    doctor_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    child_user = relationship("User", back_populates="growth_logs")

class WikiDocument(Base):
    __tablename__ = "wiki_documents"

    doc_id = Column(String(36), primary_key=True, default=generate_uuid)
    author_id = Column(String(36), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    title = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False)
    raw_markdown = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chunks = relationship("WikiDocumentChunk", back_populates="document", cascade="all, delete-orphan")

class WikiDocumentChunk(Base):
    __tablename__ = "wiki_document_chunks"

    chunk_id = Column(String(36), primary_key=True, default=generate_uuid)
    doc_id = Column(String(36), ForeignKey("wiki_documents.doc_id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    # 1536차원 임베딩 벡터를 JSON 문자열로 저장 (SQLite/PostgreSQL 양방향 호환)
    embedding_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("WikiDocument", back_populates="chunks")

class LlmChatSession(Base):
    __tablename__ = "llm_chat_sessions"

    session_id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    title = Column(String(100), default="새로운 대화")
    started_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("LlmChatMessage", back_populates="session", cascade="all, delete-orphan")

class LlmChatMessage(Base):
    __tablename__ = "llm_chat_messages"

    message_id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("llm_chat_sessions.session_id", ondelete="CASCADE"), nullable=False)
    sender_role = Column(String(20), nullable=False)  # USER, ASSISTANT, SYSTEM, TOOL
    message_text = Column(Text, nullable=False)
    tool_calls = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("LlmChatSession", back_populates="messages")

