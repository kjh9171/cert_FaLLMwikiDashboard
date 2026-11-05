-- ============================================================================
# 家族 LLM WIKI & 가계부/영수증 통합 대시보드
-- PostgreSQL 16 + pgvector 스키마
-- 실행: psql -U <사용자> -d <데이터베이스> -f init.sql
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ---------------------------------------------------------------------------
-- 1. 사용자 (가족 구성원)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50) DEFAULT 'family',
    avatar_color VARCHAR(20) DEFAULT '#F7F2E9',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- 2. 캘린더 일정
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS calendar_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    event_date DATE NOT NULL,
    category VARCHAR(50),
    is_all_day BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- 3. 할 일 (To-do)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS todos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    task VARCHAR(300) NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    category VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- 4. 여행 준비물 체크리스트
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS travel_checklists (
    id SERIAL PRIMARY KEY,
    item_name VARCHAR(200) NOT NULL,
    is_checked BOOLEAN DEFAULT FALSE,
    category VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- 5. 가계부 거래 내역
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS finance_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('INCOME', 'EXPENSE')),
    amount NUMERIC(15, 2) NOT NULL,
    category VARCHAR(100),
    transaction_date DATE NOT NULL,
    payment_method VARCHAR(100),
    title VARCHAR(300),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- 6. 영수증
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS receipts (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER REFERENCES finance_transactions(id) ON DELETE SET NULL,
    store_name VARCHAR(200),
    scanned_at TIMESTAMPTZ,
    total_amount NUMERIC(15, 2),
    payment_method VARCHAR(100),
    raw_image_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- 7. 영수증 품목
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS receipt_items (
    id SERIAL PRIMARY KEY,
    receipt_id INTEGER REFERENCES receipts(id) ON DELETE CASCADE,
    item_name VARCHAR(200),
    item_price NUMERIC(15, 2),
    quantity INTEGER DEFAULT 1
);

-- ---------------------------------------------------------------------------
-- 8. 위키 문서
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS wiki_documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    content TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- 9. 위키 문서 청크 (벡터 임베딩, dimension 1536)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS wiki_document_chunks (
    id SERIAL PRIMARY KEY,
    doc_id INTEGER REFERENCES wiki_documents(id) ON DELETE CASCADE,
    chunk_content TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- 인덱스 (검색 성능)
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_calendar_events_user_date
    ON calendar_events(user_id, event_date);
CREATE INDEX IF NOT EXISTS idx_todos_user
    ON todos(user_id);
CREATE INDEX IF NOT EXISTS idx_todos_completed
    ON todos(is_completed);
CREATE INDEX IF NOT EXISTS idx_finance_transactions_user_date
    ON finance_transactions(user_id, transaction_date);
CREATE INDEX IF NOT EXISTS idx_receipts_scanned_at
    ON receipts(scanned_at);
CREATE INDEX IF NOT EXISTS idx_wiki_chunks_embedding
    ON wiki_document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ---------------------------------------------------------------------------
-- 샘플 데이터 (선택 실행: 주석 해제하여 사용)
-- ---------------------------------------------------------------------------
/*
INSERT INTO users (name, role, avatar_color) VALUES
('하늘','child','#FBCFE8'),
('바다','child','#FDE047'),
('지훈','father','#BFDBFE'),
('민서','mother','#A7F3D0'),
('가족','family','#E9D5FF');

INSERT INTO finance_transactions (user_id, transaction_type, amount, category, transaction_date, payment_method, title) VALUES
(5,'INCOME',3500000,'급여',CURRENT_DATE,'계좌이체','11월 월급'),
(5,'EXPENSE',120000,'식비',CURRENT_DATE,'신한카드','마트 장보기'),
(5,'EXPENSE',45000,'식비',CURRENT_DATE,'현금','점심 외식'),
(5,'EXPENSE',80000,'육아/교육',CURRENT_DATE - INTERVAL '3 days','국민카드','학원비'),
(5,'EXPENSE',150000,'주거/통신',CURRENT_DATE - INTERVAL '5 days','계좌이체','아파트 관리비'),
(5,'EXPENSE',60000,'쇼핑/생활',CURRENT_DATE - INTERVAL '7 days','신한카드','생필품 구매'),
(5,'EXPENSE',30000,'기타',CURRENT_DATE - INTERVAL '10 days','현금','용돈');
*/
