# 🎨 가족 LLM WIKI 대시보드 디자인 정의서 (Design System Specification)

- **디자인 컨셉**: Warm Natural Cream & Soft Pastel Accents
- **목표 경험**: 거실 월패드(Wallpad) 및 개인 스마트폰에서 가족 모두가 편안함과 신뢰감을 느낄 수 있는 따뜻하고 직관적인 내추럴 디자인
- **적용 프레임워크**: Tailwind CSS (Utility-First System)

---

## 1. 디자인 철학 및 비주얼 원칙

1. **Warmth & Naturality**: 기계적이고 차가운 회색 대신 은은한 웜 크림 베이스(`#F5F2EC`)를 사용하여 가정 환경에 자연스럽게 녹아드는 시각적 안정감 제공.
2. **Member Color Identity**: 가족 구성원(하늘, 바다, 지훈, 민서)에게 직관적인 고유 파스텔 컬러 코드를 부여하여 일정과 할 일을 한눈에 식별.
3. **Clarity & Glanceability**: 1~2초의 가벼운 눈길(Glance)만으로도 시계, 미세먼지, 여행 준비물, 당월 예산 소진율을 파악할 수 있는 고대비 타이포그래피 및 게이지 바 구성.
4. **Clean Craftsmanship (No Visual Noise)**: 불필요한 장식과 그래픽 요소를 배제하고, 여백과 정갈한 보더(Border `#E2E8F0`), 부드러운 곡률(Border Radius `16px~24px`)로 단정한 완성도 구현.

---

## 2. 디자인 토큰 및 컬러 팔레트 (Color Palette)

### 2.1 베이스 & 뉴트럴 컬러
| 토큰 명 | Hex 코드 | 용도 |
| :--- | :--- | :--- |
| `brand-bg` | `#F5F2EC` | 전체 페이지 백그라운드 캔버스 |
| `brand-card` | `#FFFFFF` | 위젯 카드, 모달 팝업의 기본 표면 |
| `brand-text` | `#2D3748` | 본문 기본 텍스트, 주요 제목 |
| `brand-muted` | `#718096` | 보조 텍스트, 날짜, 단위, 캡션 |
| `brand-border`| `#EDF2F7` | 카드 테두리, 구분선, 테이블 라인 |
| `dock-bg` | `#1A202C` | 하단 금융 티커 및 음악 플레이어 전용 다크 배경 |

### 2.2 가족 구성원별 퍼스널 컬러 (Family Identity)
| 구성원 | 역할 / 나이 | 배경색 (`bg`) | 텍스트색 (`text`) | 보더색 (`border`) | 메인 포인트 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **하늘** | 첫째 (6세) | `#FFF5F5` | `#C53030` | `#FEB2B2` | `Rose Pink` |
| **바다** | 둘째 (3세) | `#FEFCBF` | `#9B6D00` | `#F6E05E` | `Warm Amber` |
| **지훈** | 아빠 | `#EBF8FF` | `#2B6CB0` | `#63B3ED` | `Sky Blue` |
| **민서** | 엄마 | `#F0FFF4` | `#276749` | `#68D391` | `Forest Emerald`|
| **가족 공통**| 전체 이벤트 | `#FAF5FF` | `#6B46C1` | `#D6BCFA` | `Gentle Purple`|

### 2.3 시맨틱 컬러 (Status & Finance)
| 상태 | Hex 코드 | 용도 |
| :--- | :--- | :--- |
| **수입 (Income)** | `#3182CE` (Blue 600) | 월급, 금융소득, 수입 지표 강조 |
| **지출 (Expense)**| `#E53E3E` (Red 600) | 식비, 결제 내역, 예산 초과 주의 |
| **성공/완료 (Success)**| `#38A169` (Green 600) | 준비물 챙김 완료, OCR 스캔 성공, 저축 달성 |
| **경고/주의 (Warning)**| `#DD6B20` (Orange 600)| 예산 80% 이상 소진, D-Day 임박 |

---

## 3. 타이포그래피 (Typography System)

- **기본 폰트**: `-apple-system, BlinkMacSystemFont, "Pretendard", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`
- **고정폭(Mono) 폰트**: `SFMono-Regular, Menlo, Monaco, Consolas, monospace` (금액, 시간, 코드)

| 계층 | 폰트 크기 | 웨이트 | 용도 |
| :--- | :--- | :--- | :--- |
| **Clock Display** | `60px` (`text-6xl`) | Black (`900`) | 메인 시계 시간 표시 |
| **Page Title** | `24px` (`text-2xl`) | Bold (`700`) | 글로벌 헤더 로고 및 주요 뷰 헤딩 |
| **KPI Headline** | `24px` (`text-2xl`) | Black (`900`) | 월 총 지출, 총 수입 금액 |
| **Section Title** | `18px` (`text-lg`) | Bold (`700`) | 캘린더 월 표시, 위젯 메인 제목 |
| **Card Header** | `14px` (`text-sm`) | Bold (`700`) | 구성원 할 일 카드, 영수증 스캐너 헤더 |
| **Body (Normal)** | `12px` (`text-xs`) | Regular (`400`) / Medium (`500`) | 테이블 본문, 체크리스트 항목, 채팅 내용 |
| **Caption / Tag** | `10px` (`text-[10px]`)| SemiBold (`600`) | 레벨 뱃지, 시간 캡션, 툴팁 |

---

## 4. 컴포넌트 규격 및 UI 가이드라인

### 4.1 카드 컨테이너 (Card Surface)
- `background`: `#FFFFFF`
- `border-radius`: `16px` (`rounded-2xl`)
- `border`: `1px solid #EDF2F7` (`border border-gray-100`)
- `box-shadow`: `0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)`
- `padding`: `20px` (`p-5`) 기본

### 4.2 글로벌 탭 버튼 (Global Navigation Tabs)
- **컨테이너**: `bg-gray-100 p-1 rounded-xl gap-1`
- **비활성 상태**: `text-gray-600 hover:text-gray-900 px-3.5 py-1.5 text-xs rounded-lg font-medium`
- **활성 상태 (`.active`)**: `bg-[#2D3748] text-white font-semibold shadow-xs`

### 4.3 프로그레스 바 (Progress Bars)
- **트랙 (Track)**: `bg-gray-100 h-2 rounded-full overflow-hidden`
- **인디케이터 (Bar)**: `h-full rounded-full transition-all duration-300 ease-out`
  - 여행 체크리스트: `bg-emerald-500`
  - 예산 소진율: 정상 `<70%` (`bg-blue-500`), 주의 `70~90%` (`bg-amber-500`), 위험 `>90%` (`bg-red-500`)

### 4.4 모달 다이얼로그 (Modal Surface)
- **오버레이**: `fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center z-50 p-4`
- **모달 바디**: `bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl`
- **헤더**: `text-base font-bold text-gray-800`

---

## 5. 마이크로 인터랙션 및 모션 가이드 (Motion & Animations)

1. **실시간 티커 롤링 (`.ticker-move`)**:
   - `animation: ticker 35s linear infinite;`
   - 금융 지수 및 가족 뉴스 롤링이 끊김 없이 부드럽게 좌측으로 연속 이동.
2. **영수증 OCR 레이저 스캔 이펙트**:
   - 스캔 버튼 클릭 시 영수증 프리뷰 영역에 수직 방향으로 위아래 왕복하는 반투명 보라색 레이저 빔 애니메이션 구동 (`duration: 0.8s`).
3. **체크리스트 토글 모션**:
   - 체크박스 클릭 시 0.15s 스케일 바운스 피드백 및 텍스트 취소선(Strike-through) 애니메이션.
4. **AI 챗 타이핑 스트리밍**:
   - LLM 답변 시 글자 단위 또는 토큰 단위 순차 렌더링 효과로 실시간 생각하고 답변하는 지능형 감성 부여.

---

## 6. 반응형 브레이크포인트 (Responsive Grid System)

- **Mobile View (`< 768px`)**:
  - 단일 컬럼 수직 스택 (`grid-cols-1`)
  - 글로벌 네비게이션 탭 가로 스크롤 허용
  - 시계 및 날씨 카드 1열 배치
- **Tablet / 월패드 View (`768px ~ 1024px`)**:
  - 2열 그리드 분할
  - 캘린더와 할 일 카드 좌우 분할
- **Desktop / 거실 와이드 월패드 (`> 1024px`)**:
  - 12열 비대칭 그리드 (좌측 5열: 캘린더/체크리스트/타임라인, 우측 7열: 할일/성장/D-Day)
  - 최대 너비: `max-w-7xl (1280px)` 중앙 정렬

