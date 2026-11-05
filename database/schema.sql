-- ====================================================================
-- Family LLM WIKI & Household Finance Platform Database DDL Script
-- Target Engine: PostgreSQL 16+ with pgvector extension
-- Author: Family AI Engineering Team
-- Date: 2026-11-05
-- Mode: Clean Schema Only (No Seed/Mock Data)
--       실제 데이터는 API를 통해 직접 입력하세요.
-- ====================================================================

-- 1. Enable Required Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 2. Drop Tables if Exists (Clean Environment)
DROP TABLE IF EXISTS llm_chat_messages CASCADE;
DROP TABLE IF EXISTS llm_chat_sessions CASCADE;
DROP TABLE IF EXISTS wiki_document_chunks CASCADE;
DROP TABLE IF EXISTS wiki_documents CASCADE;
DROP TABLE IF EXISTS child_growth_logs CASCADE;
DROP TABLE IF EXISTS checklist_items CASCADE;
DROP TABLE IF EXISTS todos CASCADE;
DROP TABLE IF EXISTS calendar_events CASCADE;
DROP TABLE IF EXISTS receipt_items CASCADE;
DROP TABLE IF EXISTS finance_transactions CASCADE;
DROP TABLE IF EXISTS receipts CASCADE;
DROP TABLE IF EXISTS finance_budgets CASCADE;
DROP TABLE IF EXISTS finance_categories CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 3. Create Core Tables

-- (1) Family Members (users)
CREATE TABLE users (
    user_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('ADMIN', 'MEMBER', 'CHILD')),
    color_code VARCHAR(20) NOT NULL,
    avatar_initial VARCHAR(5) NOT NULL,
    birth_date DATE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- (2) Financial Categories (finance_categories)
CREATE TABLE finance_categories (
    category_code VARCHAR(30) PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('INCOME', 'EXPENSE')),
    icon_symbol VARCHAR(10),
    display_order INT DEFAULT 0
);

-- (3) Monthly Budgets (finance_budgets)
CREATE TABLE finance_budgets (
    budget_id VARCHAR(36) PRIMARY KEY,
    year_month VARCHAR(7) NOT NULL, -- e.g. '2026-11'
    category_code VARCHAR(30) REFERENCES finance_categories(category_code) ON DELETE CASCADE,
    budget_amount NUMERIC(12, 0) NOT NULL CHECK (budget_amount >= 0),
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_budget_month_cat UNIQUE (year_month, category_code)
);

-- (4) Scanned OCR Receipts (receipts)
CREATE TABLE receipts (
    receipt_id VARCHAR(36) PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    transaction_datetime TIMESTAMPTZ NOT NULL,
    total_amount NUMERIC(12, 0) NOT NULL CHECK (total_amount >= 0),
    tax_amount NUMERIC(12, 0) DEFAULT 0,
    image_url VARCHAR(255),
    ocr_confidence FLOAT CHECK (ocr_confidence BETWEEN 0 AND 1),
    scan_status VARCHAR(20) DEFAULT 'PARSED' CHECK (scan_status IN ('PENDING', 'PARSED', 'CONFIRMED')),
    scanned_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- (5) Receipt Detail Items (receipt_items)
CREATE TABLE receipt_items (
    item_id VARCHAR(36) PRIMARY KEY,
    receipt_id VARCHAR(36) NOT NULL REFERENCES receipts(receipt_id) ON DELETE CASCADE,
    item_name VARCHAR(100) NOT NULL,
    quantity INT DEFAULT 1 CHECK (quantity > 0),
    unit_price NUMERIC(12, 0) NOT NULL,
    total_price NUMERIC(12, 0) NOT NULL
);

-- (6) Household Financial Ledger (finance_transactions)
CREATE TABLE finance_transactions (
    transaction_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(user_id) ON DELETE SET NULL,
    category_code VARCHAR(30) NOT NULL REFERENCES finance_categories(category_code),
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('INCOME', 'EXPENSE')),
    title VARCHAR(100) NOT NULL,
    amount NUMERIC(12, 0) NOT NULL CHECK (amount > 0),
    transaction_date DATE NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    receipt_id VARCHAR(36) REFERENCES receipts(receipt_id) ON DELETE SET NULL,
    memo TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- (7) Family Calendar Events (calendar_events)
CREATE TABLE calendar_events (
    event_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(user_id) ON DELETE SET NULL,
    title VARCHAR(100) NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    is_all_day BOOLEAN DEFAULT FALSE,
    category VARCHAR(30) NOT NULL,
    color_tag VARCHAR(20) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- (8) Member Todos (todos)
CREATE TABLE todos (
    todo_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- (9) Smart Checklist Items (checklist_items)
CREATE TABLE checklist_items (
    item_id VARCHAR(36) PRIMARY KEY,
    context_type VARCHAR(50) NOT NULL DEFAULT 'ONBOARDING',
    category VARCHAR(50) NOT NULL,
    item_name VARCHAR(100) NOT NULL,
    is_checked BOOLEAN DEFAULT FALSE,
    sort_order INT DEFAULT 0
);

-- (10) Child Growth & Vaccination Logs (child_growth_logs)
CREATE TABLE child_growth_logs (
    log_id VARCHAR(36) PRIMARY KEY,
    child_user_id VARCHAR(36) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    record_date DATE NOT NULL,
    height_cm NUMERIC(5, 1) NOT NULL,
    weight_kg NUMERIC(5, 1),
    vaccine_name VARCHAR(100),
    doctor_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- (11) Family WIKI Markdown Documents (wiki_documents)
CREATE TABLE wiki_documents (
    doc_id VARCHAR(36) PRIMARY KEY,
    author_id VARCHAR(36) REFERENCES users(user_id) ON DELETE SET NULL,
    title VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    raw_markdown TEXT NOT NULL,
    version INT DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- (12) RAG Vector Chunks with pgvector (wiki_document_chunks)
CREATE TABLE wiki_document_chunks (
    chunk_id VARCHAR(36) PRIMARY KEY,
    doc_id VARCHAR(36) NOT NULL REFERENCES wiki_documents(doc_id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- (13) LLM Chat Sessions & Message History
CREATE TABLE llm_chat_sessions (
    session_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(user_id) ON DELETE SET NULL,
    title VARCHAR(100) DEFAULT '새로운 대화',
    started_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE llm_chat_messages (
    message_id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES llm_chat_sessions(session_id) ON DELETE CASCADE,
    sender_role VARCHAR(20) NOT NULL CHECK (sender_role IN ('USER', 'ASSISTANT', 'SYSTEM', 'TOOL')),
    message_text TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. Create Indexes
CREATE INDEX idx_finance_trans_date_cat ON finance_transactions(transaction_date DESC, category_code, transaction_type);
CREATE INDEX idx_calendar_event_timerange ON calendar_events(start_time, end_time);
CREATE INDEX idx_todos_user_completed ON todos(user_id, is_completed);
CREATE INDEX idx_wiki_doc_category ON wiki_documents(category);

-- HNSW Vector Index for Cosine Distance Search
CREATE INDEX idx_wiki_embedding_hnsw 
ON wiki_document_chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- ====================================================================
-- NOTE: 시드/목 데이터는 더 이상 삽입하지 않습니다.
--       모든 데이터는 API 엔드포인트를 통해 직접 입력/관리하세요.
--       예: POST /api/v1/finance/transactions (가계부 거래 등록)
-- ====================================================================
