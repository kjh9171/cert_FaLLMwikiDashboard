# 🏡 가족 LLM WIKI 대시보드 & 가계/영수증 관리 시스템

> **Local-First RAG & Finance Intelligence Dashboard for Family**  
> 온디바이스 AI, OCR 영수증 파싱, 가계 수입/지출 관리, 캘린더/할 일 및 아이 성장 기록이 결합된 통합 가족 지식 대시보드 및 서비스 시스템 (Web & Mobile App 완벽 지원)

---

## 📱 웹(Web) & 모바일 앱(Mobile App) 듀얼 지원

클라이언트 유저는 PC 웹 브라우저뿐만 아니라 **스마트폰(iOS/Android)과 거실 월패드 태블릿**에서 완전한 네이티브 앱 형태로 언제 어디서나 편리하게 이용할 수 있습니다.

- **안드로이드 스마트폰**: 화면 상단의 **[📲 앱 설치]** 버튼 클릭 또는 크롬 메뉴에서 **[홈 화면에 추가/앱 설치]** 시 독립형 앱으로 즉시 설치.
- **아이폰 & 아이패드 (iOS)**: 사파리(Safari)에서 **[공유 버튼] > [홈 화면에 추가]** 시 노치 및 다이내믹 아일랜드 영역까지 풀스크린으로 네이티브 앱 구동.
- **모바일 네이티브 UX 탑재**: 모바일 화면에서는 상단 메뉴 대신 화면 하단에 스마트폰 전용 **하단 바텀 탭바(Bottom Navigation Bar)**가 노출되어 한 손 엄지손가락으로 손쉽게 조작 가능.
- **거실 월패드 상시 화면 유지**: 상단 헤더의 **[💡 화면 켜짐 유지]** 버튼을 통해 Screen Wake Lock API를 활성화하여 365일 24시간 화면 꺼짐 없이 캘린더/시계/날씨 상시 표시.
- **오프라인 서비스 워커(`sw.js`)**: 네트워크 연결이 불안정하거나 단절되어도 서비스 워커와 LocalStorage 캐시를 통해 앱이 0.1초 만에 즉시 켜짐.
- 📖 **[상세 모바일 앱 & 월패드 가이드 바로가기 (docs/06_MOBILE_APP_PWA_GUIDE.md)](docs/06_MOBILE_APP_PWA_GUIDE.md)**

---

## 🔒 포트 충돌 방지 클린 포트 설계 (Port Conflict-Free Architecture)

기존 호스트 및 도커 환경에서 실행 중인 서비스들(80, 8000, 8080, 8081, 8090, 5432, 5433, 6379, 6380 등)과의 충돌을 전면 방지하기 위해, 본 프로젝트는 **미사용 청정 포트(Clean Dedicated Ports)**를 전용으로 배정하였습니다.

| 서비스 구분 | 컴포넌트 | 내부 포트 | 외부/호스트 포트 | 상태 및 충돌 회피 |
| :--- | :--- | :--- | :--- | :--- |
| **FastAPI Backend** | `family-backend` | `8000/tcp` | **`8088`** | 8000(solocorp), 8080(secushield), 8081(assetledger) 충돌 회피 |
| **Web Dashboard** | `family-web` (Nginx) | `80/tcp` | **`8085`** | 80(secuprivacy-nginx), 8080, 8081, 8090 충돌 회피 |
| **PostgreSQL 16** | `family-db` (pgvector) | `5432/tcp` | **`5435`** | 5432(offboarding), 5433(secuprivacy), 15432(secuxpert) 충돌 회피 |
| **Redis Broker** | `family-redis` | `6379/tcp` | **`6385`** | 6379(secuprivacy), 6380(offboarding), 16379(secuxpert) 충돌 회피 |
| **Ollama Service** | `family-ollama` | `11434/tcp` | **`11438`** | 11434(호스트 Ollama), 11435(Antigravity) 충돌 회피 |

---

## 🚀 빠른 서비스 시작 (Quick Start)

### 방법 1. 원클릭 스크립트로 백엔드 및 서비스 시작 (권장)
```bash
# 터미널에서 프로젝트 디렉토리로 이동
cd /Users/gimjonghwan319/Downloads/cert_FaLLMwikiDashboard

# 원클릭 실행 스크립트 가동 (포트 8088 자동 바인딩)
./run.sh
```
- **FastAPI 대화형 Swagger API 문서**: [http://localhost:8088/docs](http://localhost:8088/docs)
- **시스템 헬스체크**: [http://localhost:8088/api/v1/health](http://localhost:8088/api/v1/health)
- **웹 대시보드 열람**: 브라우저에서 `index.html`을 열면 헤더에 `🟢 Backend API Online (Port 8088)` 상태가 점등되며 백엔드와 실시간 양방향 동기화됩니다.

### 방법 2. 무설치 로컬 단독 실행 (Local-First Offline Mode)
- 백엔드 서버가 구동되지 않더라도 `index.html` 파일을 브라우저에서 바로 열면, 내장된 `LocalStorage` 엔진을 통해 모든 기능(영수증 OCR 스캔 시뮬레이션, 수입/지출 CRUD, Chart.js 동적 갱신, RAG 대화, WIKI 문서 등록)이 매끄럽게 구동됩니다.

### 방법 3. Docker Compose 홈서버 배포
기존 도커 서비스와 충돌 없이 독립된 포트로 일괄 구동됩니다:
```bash
docker-compose up -d --build
```
- **웹 대시보드 (Nginx)**: [http://localhost:8085](http://localhost:8085)
- **백엔드 API**: [http://localhost:8088](http://localhost:8088)

---

## 📂 프로젝트 구조 및 구현 산출물 명세

```
cert_FaLLMwikiDashboard/
├── index.html                           # 🌟 프론트엔드 대시보드 (PWA & 모바일 하단 탭바 탑재)
├── manifest.json                        # 📱 Web App Manifest (홈 화면 추가, 독립 실행형 앱 스펙)
├── sw.js                                # ⚡ Service Worker (오프라인 캐싱 및 빠른 기동)
├── capacitor.config.json                # 📦 Capacitor 네이티브 앱(APK/IPA) 패키징 설정
├── assets/
│   └── icons/                           # 🎨 고해상도 앱 아이콘 (192x192, 512x512, apple-touch-icon)
├── run.sh                               # 🚀 백엔드 원클릭 실행 스크립트 (Port 8088 바인딩)
├── Dockerfile                           # 🐳 FastAPI 백엔드 컨테이너 빌드 파일
├── docker-compose.yml                   # 🏗️ 충돌 방지 클린 포트(8085, 8088, 5435, 6385, 11438) 배포 구성
├── README.md                            # 📖 프로젝트 가이드 및 종합 안내서
│
├── backend/                             # ⚡ FastAPI 백엔드 서비스 구현체
│   ├── family_wiki.db                   # 🗄️ 즉시 실행 가능한 SQLite 데이터베이스
│   ├── test_api.py                      # 🧪 엔드포인트 전체 통합/스모크 테스트 스크립트
│   ├── requirements.txt                 # 📦 파이썬 의존성 패키지 목록
│   ├── uploads/                         # 📸 영수증 이미지 파일 저장소
│   └── app/
│       ├── main.py                      # FastAPI 메인 애플리케이션 & CORS & 라우터 등록
│       ├── config.py                    # 환경변수 및 설정 (Port 8088, Ollama Base, DB URL 등)
│       ├── db/
│       │   ├── session.py               # SQLAlchemy DB 엔진 & 세션 풀
│       │   ├── models.py                # 명세서 기반 13개 테이블 ORM 모델 정의
│       │   └── init_db.py               # 데이터베이스 및 가족 초기 시드 데이터 자동 적재
│       ├── schemas/                     # Pydantic Schemas (Finance, Receipt, Wiki, Chat 등)
│       ├── services/                    # 비즈니스 로직 및 AI 엔진 (OCR, 1536d 임베딩, Ollama RAG Agent)
│       └── api/                         # REST API 라우터 (Finance, Receipts, Wiki, LLM, Calendar, Todos, Health)
│
├── database/
│   └── schema.sql                       # 🗄️ PostgreSQL 16 + pgvector DDL 스크립트 및 시드 데이터
│
└── docs/                                # 📚 정밀 시스템 명세서 세트
    ├── 01_FUNCTIONAL_SPECIFICATION.md   # 1. 기능 정의서 (모듈별 세부 요구사항 & DFD)
    ├── 02_API_OPERATIONS_SPECIFICATION.md# 2. API 및 운영 명세서 (엔드포인트, 응답 규격, 런북)
    ├── 03_DESIGN_SYSTEM_SPECIFICATION.md# 3. 디자인 정의서 (컬러 토큰, 타이포그래피, 컴포넌트)
    ├── 04_DATABASE_ERD_SPECIFICATION.md # 4. DB-ERD 및 스키마 명세서 (13개 테이블 관계도)
    ├── 05_SYSTEM_ARCHITECTURE.md        # 5. 시스템 아키텍처 & 충돌 방지 배포 가이드
    └── 06_MOBILE_APP_PWA_GUIDE.md       # 6. 모바일 앱 & 거실 월패드 PWA 이용 가이드
```

---

## 🧪 백엔드 API 테스트 실행

```bash
cd /Users/gimjonghwan319/Downloads/cert_FaLLMwikiDashboard
PYTHONPATH=. .venv/bin/python3 backend/test_api.py
```
**테스트 결과**:
- `Health check OK: UP`
- `Summary OK: Total Income=5,800,000, Total Expense=563,900`
- `Transactions OK: count=5`
- `Wiki docs OK: count=3`
- `Checklist OK: count=17`
- `LLM Chat OK Answer: ...`
- `Receipt Scan OK: Store=이마트 속초점, Total=50,900`
- `ALL API ENDPOINT TESTS PASSED!`
