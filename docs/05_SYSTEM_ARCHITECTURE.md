# 🏗️ 가족 LLM WIKI & 가계/영수증 시스템 아키텍처 및 배포 가이드 (System Architecture)

- **버전**: v1.3.0
- **배포 타깃**: 홈서버 (Intel NUC / Apple Silicon Mac Mini / 로컬 PC) + 거실 벽면 안드로이드/아이패드 월패드 PWA
- **보안 및 프라이버시 정책**: Local-First, Zero Cloud Data Leakage (가족 금융 및 개인정보의 외부 유출 원천 차단)
- **포트 충돌 방지 클린 포트 정책**: 기존 운영 중인 도커 서비스들과의 포트 충돌을 완벽히 방지하기 위해 독립된 포트 대역 할당

---

## 1. 포트 충돌 분석 및 클린 포트 할당표

호스트 머신에 기존 운영 중인 다수의 도커 컨테이너(80, 8000, 8080, 8081, 8090, 5432, 5433, 6379, 6380, 11434 등)와의 충돌을 원천 차단하기 위해 아래와 같이 안전한 전용 포트를 배정했습니다.

| 서비스 구분 | 컨테이너 명 | 내부 포트 | 호스트 바인딩 포트 | 기존 충돌 회피 대상 |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend Web** | `family-web` | `80/tcp` | **`8085`** | 80(nginx), 8080(saas), 8081(asset), 8090(artex) |
| **FastAPI Backend** | `family-backend` | `8000/tcp` | **`8088`** | 8000(solocorp-backend), 8080, 8081 |
| **PostgreSQL 16** | `family-db` | `5432/tcp` | **`5435`** | 5432(offboarding), 5433(secuprivacy), 15432(secuxpert) |
| **Redis Cache** | `family-redis` | `6379/tcp` | **`6385`** | 6379(secuprivacy), 6380(offboarding), 16379(secuxpert) |
| **Ollama LLM** | `family-ollama` | `11434/tcp` | **`11438`** | 11434(호스트 기본 Ollama), 11435(Antigravity) |

---

## 2. 하이브리드 계층형 아키텍처 (Layered Architecture)

```
┌────────────────────────────────────────────────────────────────────────┐
│                        1. Client Layer (Presentation)                  │
│  - Living Room Wallpad (PWA Kiosk Mode 1920x1080)                     │
│  - Parent Mobile Devices (Responsive Web: iOS Safari / Android Chrome) │
│  - Receipt Camera Scanner UI & Touchpad Checklist                      │
│  - Host Port: 8085 (http://localhost:8085)                             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTPS / REST (Safe Port: 8088)
┌───────────────────────────────────▼────────────────────────────────────┐
│                    2. Application & Intelligence Layer                 │
│  ┌──────────────────────────────┐    ┌──────────────────────────────┐  │
│  │   FastAPI Core Backend       │    │  OCR Pipeline (PaddleOCR)    │  │
│  │   - Finance CRUD & Ledgers   │    │  - Receipt Layout Analyzer   │  │
│  │   - Calendar & Todo Services │    │  - Text Extraction & Normal  │  │
│  │   - Host Port: 8088          │    │  - Item & Price Structurer   │  │
│  └──────────────┬───────────────┘    └──────────────┬───────────────┘  │
│                 │                                   │                  │
│                 ├───────────────────────────────────┘                  │
│                 ▼                                                      │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │   LangChain / Ollama Local LLM Agent Layer                       │  │
│  │   - Local LLM: Llama-3-8B-Instruct (Port: 11438)                 │  │
│  │   - Hybrid Search: BM25 Keyword + pgvector Cosine Similarity     │  │
│  │   - Function Calling Agent: Finance Query / Calendar Action      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ SQL / Vector Embedding (pgvector)
┌───────────────────────────────────▼────────────────────────────────────┐
│                     3. Data & State Storage Layer                      │
│  - PostgreSQL 16 + pgvector Extension (Host Port: 5435)                │
│  - Redis 7.2 (Pub/Sub for Realtime Sync, Host Port: 6385)              │
│  - Local NVMe Storage for Scanned Receipt Image Vault (`/data/vault/`) │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Docker Compose 원클릭 배포 구성 (`docker-compose.yml`)

```yaml
version: '3.8'

services:
  # 1. Database (PostgreSQL + pgvector) - Port 5435
  family-db:
    image: pgvector/pgvector:pg16
    container_name: family_db
    restart: always
    environment:
      POSTGRES_DB: family_wiki_db
      POSTGRES_USER: family_admin
      POSTGRES_PASSWORD: super_secure_family_password_2026
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./database/schema.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "127.0.0.1:5435:5432"

  # 2. Redis Message Broker & Cache - Port 6385
  family-redis:
    image: redis:7.2-alpine
    container_name: family_redis
    restart: always
    ports:
      - "127.0.0.1:6385:6379"

  # 3. Local LLM Service (Ollama) - Port 11438
  family-ollama:
    image: ollama/ollama:latest
    container_name: family_ollama
    restart: always
    volumes:
      - ollamadata:/root/.ollama
    ports:
      - "11438:11434"

  # 4. FastAPI Core & OCR Backend - Port 8088
  family-backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: family_backend
    restart: always
    environment:
      DATABASE_URL: postgresql://family_admin:super_secure_family_password_2026@family-db:5432/family_wiki_db
      REDIS_URL: redis://family-redis:6379/0
      OLLAMA_API_BASE: http://family-ollama:11434
    depends_on:
      - family-db
      - family-redis
      - family-ollama
    ports:
      - "8088:8000"

  # 5. Frontend Web Dashboard - Port 8085
  family-web:
    image: nginx:alpine
    container_name: family_web
    restart: always
    volumes:
      - ./index.html:/usr/share/nginx/html/index.html
    ports:
      - "8085:80"
    depends_on:
      - family-backend

volumes:
  pgdata:
  ollamadata:
```

---

## 4. 거실 월패드(Wallpad) PWA 키오스크 설정 가이드

1. **상시 전원 및 화면 켜짐 유지**:
   - 안드로이드 설정 > 개발자 옵션 > '충전 시 화면 켜짐 유지(Stay Awake)' 활성화
2. **풀스크린 PWA 설치**:
   - 크롬 브라우저에서 `http://<홈서버_IP>:8085` 접속 후 '홈 화면에 추가' 클릭
3. **오프라인 캐싱 (Service Worker & LocalStorage)**:
   - 네트워크 단절 시에도 로컬스토리지에 캐시된 가계부 및 최근 일정을 중단 없이 표시
