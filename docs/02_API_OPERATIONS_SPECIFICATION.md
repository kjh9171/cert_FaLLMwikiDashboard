# ⚡ 가족 LLM WIKI & 가계/영수증 통합 API 및 운영 명세서 (API & Operations Manual)

- **버전**: v1.3.0
- **기본 베이스 URL**: `https://api.family-wiki.local/api/v1` (또는 로컬 개발: `http://localhost:8088/api/v1`)
- **통신 프로토콜**: HTTPS, WebSocket (실시간 스트리밍 및 월패드 브로드캐스트)
- **인증 방식**: Bearer JWT (가족 단말용 상시 토큰 또는 세션 인증)

---

## 1. 공통 응답 규격 및 에러 코드 체계

### 1.1 표준 성공 응답 형식
```json
{
  "success": true,
  "code": "SUCCESS",
  "message": "요청이 성공적으로 처리되었습니다.",
  "data": {},
  "timestamp": "2026-11-05T14:30:00Z"
}
```

### 1.2 표준 에러 응답 형식
```json
{
  "success": false,
  "code": "INVALID_TRANSACTION_AMOUNT",
  "message": "거래 금액은 0보다 큰 숫자여야 합니다.",
  "error_details": {
    "field": "amount",
    "rejected_value": -5000
  },
  "timestamp": "2026-11-05T14:30:00Z"
}
```

### 1.3 표준 에러 코드 표
| HTTP 상태 | 비즈니스 코드 | 설명 |
| :--- | :--- | :--- |
| `400 Bad Request` | `INVALID_INPUT_PARAMETER` | 입력 파라미터 유효성 검증 실패 |
| `401 Unauthorized`| `AUTH_TOKEN_EXPIRED` | 인증 토큰 만료 또는 인증 실패 |
| `404 Not Found`   | `RESOURCE_NOT_FOUND` | 요청한 엔티티(영수증, 문서, 거래 등) 부재 |
| `422 Unprocessable`| `OCR_PARSING_FAILED` | 영수증 이미지 해상도 불량으로 텍스트 추출 실패 |
| `500 Server Error`| `LLM_INFERENCE_TIMEOUT` | 로컬 LLM 추론 시간 초과 (30초 초과) |
| `503 Unavailable` | `VECTOR_DB_UNAVAILABLE`| pgvector 인스턴스 연결 지연 또는 다운 |

---

## 2. API 엔드포인트 세부 명세

### 2.1 가계 재정 관리 API (Finance Module)

#### [POST] `/finance/transactions` - 신규 거래 내역 등록
- **설명**: 수동 또는 영수증 파싱 후 확정된 수입/지출 내역을 원장에 기록합니다.
- **Request Body**:
```json
{
  "user_id": "usr_jihoon_01",
  "type": "EXPENSE",
  "category": "식비",
  "title": "하나로마트 장보기",
  "amount": 36100,
  "transaction_date": "2026-11-05",
  "payment_method": "신한카드",
  "receipt_id": "rcpt_20261105_001",
  "memo": "속초 여행용 장보기"
}
```
- **Response (201 Created)**:
```json
{
  "success": true,
  "code": "CREATED",
  "data": {
    "transaction_id": "tx_20261105_9981",
    "recorded_at": "2026-11-05T15:40:00Z",
    "updated_balance_summary": {
      "monthly_total_expense": 2471100,
      "remaining_budget": 528900
    }
  }
}
```

#### [GET] `/finance/summary` - 월별 재정 요약 KPI 조회
- **설명**: 특정 연월의 총 수입, 총 지출, 순수 저축액, 카테고리별 지출 비율을 조회합니다.
- **Query Parameters**: `year_month=2026-11`
- **Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "year_month": "2026-11",
    "total_income": 5800000,
    "total_expense": 2435000,
    "net_savings": 3365000,
    "budget_limit": 3000000,
    "budget_utilization_rate": 81.1,
    "category_breakdown": [
      { "category": "식비", "amount": 780000, "percentage": 32.0 },
      { "category": "육아/교육", "amount": 650000, "percentage": 26.7 },
      { "category": "주거/통신", "amount": 480000, "percentage": 19.7 },
      { "category": "쇼핑/생활", "amount": 320000, "percentage": 13.1 },
      { "category": "기타", "amount": 205000, "percentage": 8.5 }
    ]
  }
}
```

---

### 2.2 영수증 OCR 엔진 API (Receipts Module)

#### [POST] `/receipts/scan` - 영수증 이미지 OCR 자동 분석
- **설명**: 업로드된 영수증 이미지(Multipart Form)를 PaddleOCR/EasyOCR 엔진으로 텍스트 및 레이아웃을 분석하여 구조화된 JSON으로 반환합니다.
- **Request Headers**: `Content-Type: multipart/form-data`
- **Request Body**: `file: receipt_20261105.jpg` (Binary)
- **Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "receipt_id": "rcpt_temp_91823",
    "store_name": "하나로마트 속초농협점",
    "transaction_datetime": "2026-11-04T15:42:00",
    "business_number": "128-82-01923",
    "total_amount": 36100,
    "tax_amount": 3281,
    "items": [
      { "name": "강원도 한우 국거리", "quantity": 1, "unit_price": 24000, "total_price": 24000 },
      { "name": "신선 사과 1봉", "quantity": 1, "unit_price": 8900, "total_price": 8900 },
      { "name": "생수 2L 6팩", "quantity": 1, "unit_price": 3200, "total_price": 3200 }
    ],
    "ocr_confidence": 0.965,
    "recommended_category": "식비"
  }
}
```

---

### 2.3 가족 LLM & RAG 비서 API (LLM Module)

#### [POST] `/llm/chat` - 자연어 RAG 질의 및 Agent Action 실행
- **설명**: 사용자의 자연어 질문을 받아 pgvector에서 관련 문서를 검색하고, 필요시 가계부/캘린더 도구를 호출하여 최종 답변을 생성합니다.
- **Request Body**:
```json
{
  "user_id": "usr_minseo_02",
  "session_id": "sess_20261105_01",
  "prompt": "내일 속초 여행 가는데 우리가 아직 안 챙긴 물품 목록 정리해줘.",
  "enable_agent_action": true
}
```
- **Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "answer": "속초 바닷가 여행 체크리스트를 확인한 결과, 총 17개 항목 중 14개 항목이 아직 미체크 상태입니다.\n\n주요 미체크 품목:\n• 수영복, 카메라, 간식통, 과일\n• 세면도구, 모자, 튜브, 충전기\n• 현지 구매 예정: 아이스팩, 생수, 컵라면\n\n지금 바로 챙기시겠습니까?",
    "retrieved_context": [
      {
        "doc_title": "2026 가을 바닷가 여행 계획",
        "score": 0.912,
        "matched_chunk": "목적지: 속초 해수욕장, 필수 준비물: 비상약, 수영복, 아이스팩..."
      }
    ],
    "tool_calls_executed": [
      {
        "tool_name": "query_checklist",
        "arguments": { "category": "여행 준비물", "status": "unchecked" },
        "execution_result": "14 items pending"
      }
    ]
  }
}
```

#### [POST] `/wiki/documents` - WIKI 마크다운 지식 문서 등록 및 색인
- **설명**: 가족 규칙, 육아 지침, 매뉴얼 문서를 등록하고 텍스트 청킹 및 임베딩을 수행하여 벡터 스토어에 저장합니다.
- **Request Body**:
```json
{
  "title": "바다 소아과 백신 접종 매뉴얼",
  "category": "육아/건강",
  "author_id": "usr_minseo_02",
  "content": "# 바다 예방접종 안내\n- 접종 주기: 11월 20일 생일 직후 방문 예정\n- 병원: 행복 소아청소년과의원 (033-631-0000)\n- 필수 준비물: 아기 수첩, 여벌 옷"
}
```
- **Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "doc_id": "doc_20261105_091",
    "chunks_created": 2,
    "embedding_dimension": 1536,
    "indexed_at": "2026-11-05T15:45:10Z"
  }
}
```

---

### 2.4 캘린더 & 할 일 API (Calendar & Tasks)

#### [GET] `/calendar/events` - 일정 목록 조회
- **Query Parameters**: `start_date=2026-11-01&end_date=2026-11-30`
- **Response (200 OK)**:
```json
{
  "success": true,
  "data": [
    {
      "event_id": "evt_101",
      "title": "가족 바닷가 여행",
      "start_time": "2026-11-06T09:00:00",
      "end_time": "2026-11-07T18:00:00",
      "is_all_day": true,
      "category": "가족",
      "color_tag": "#805AD5",
      "created_by": "usr_jihoon_01"
    }
  ]
}
```

---

## 3. 시스템 운영 정책 및 런북 (Operations Manual)

### 3.1 서비스 가용성 및 성능 목표 (SLA/SLO)
- **가용성 목표**: 월간 가용률 99.8% (월 패드 상시 가동 지원)
- **API 응답 시간 목표**:
  - 일반 CRUD API: `p95 < 150ms`
  - 영수증 OCR 스캔 분석: `p95 < 2.5s`
  - LLM RAG 하이브리드 질의: `p95 < 3.5s` (로컬 GPU 가속 기준)

### 3.2 백업 및 데이터 보존 정책
1. **일일 스냅샷 백업**: 매일 새벽 04:00 자동 실행 (`pg_dump` 기반 수입/지출 원장 및 WIKI 문서)
2. **영수증 원본 이미지 아카이빙**: `/data/receipts/{YYYY}/{MM}/` 디렉토리 보관 (최대 3년간 보관)
3. **벡터 인덱스 재생성**: 매주 일요일 03:00 `REINDEX INDEX idx_wiki_embedding_hnsw;` 실행

### 3.3 장애 유형별 대응 런북 (Incident Response Runbook)

| 장애 상황 | 증상 | 긴급 조치 절차 |
| :--- | :--- | :--- |
| **LLM 추론 지연/무응답** | 채팅창 로딩 인디케이터 10초 이상 지속 | 1. `docker restart family-ollama-service`<br>2. GPU VRAM 점유율 확인 (`nvidia-smi` 또는 Metal 메모리 확인)<br>3. 필요시 가계부 SQL 직결 모드로 자동 폴백(Fallback) |
| **영수증 OCR 파싱 실패율 급증** | OCR 후 품목 누락 또는 금액 0원 발생 | 1. 입력 이미지 해상도 필터링 점검 (최소 1024x768 권장)<br>2. 전처리 그레이스케일/대비증폭(CLAHE) 알고리즘 재활성화 |
| **DB 디스크 임계치 초과 (90% 이상)** | 신규 거래 등록 시 I/O 에러 발생 | 1. 30일 경과 로그 데이터 청소 (`docker logs --prune`)<br>2. 임시 캐시 디렉토리 정리 (`/tmp/receipt_cache/`) |

