# 📱 가족 LLM WIKI 웹 & 모바일 앱(App) 통합 이용 가이드 (PWA & Native App)

- **적용 대상**: 모든 클라이언트 유저 (스마트폰 iOS/Android, 태블릿, 거실 벽면 안드로이드 월패드, PC 웹 브라우저)
- **앱 아키텍처**: Responsive Progressive Web App (PWA) + Hybrid Native App (Capacitor Ready)
- **핵심 목표**: 별도의 앱스토어 심사 대기 없이 모든 스마트폰과 거실 월패드에 네이티브 앱과 동일한 전체화면(Standalone) 앱 경험 제공

---

## 1. 플랫폼별 이용 방법 (Web & Mobile App)

### 1.1 안드로이드 스마트폰 & 태블릿 (Android Chrome / Samsung Internet)
1. 브라우저에서 서비스 주소(`http://<홈서버_IP>:8085` 또는 로컬 `http://localhost:8085`)에 접속합니다.
2. 화면 상단 헤더의 **[📲 앱 설치]** 버튼을 터치하거나, 브라우저 우측 상단 더보기(`⋮`) > **[앱 설치]** 또는 **[홈 화면에 추가]**를 누릅니다.
3. 바탕화면에 **"가족대시보드"** 아이콘이 생성되며, 터치 시 주소창이 없는 **100% 순수 네이티브 앱 화면**으로 실행됩니다.
4. 스마트폰 화면 하단에 **전용 바텀 탭 네비게이션(Bottom Navigation Bar)**이 활성화되어 한 손으로 엄지손가락 조작이 가능합니다.

---

### 1.2 아이폰 & 아이패드 (iOS Safari)
1. **사파리(Safari) 브라우저**로 서비스 주소에 접속합니다.
2. 사파리 하단 중앙의 **[공유 버튼(네모에 위쪽 화살표)]**을 누릅니다.
3. 스크롤을 내려 **[홈 화면에 추가 (Add to Home Screen)]**를 선택합니다.
4. 홈 화면에 아이폰 전용 고화질 터치 아이콘(`apple-touch-icon.png`)이 등록되며, 실행 시 노치 및 다이내믹 아일랜드 영역까지 커버되는 풀스크린 네이티브 앱 경험을 제공합니다.

---

### 1.3 거실 월패드 (Wallpad Kiosk Mode)
1. 거실 벽면에 부착된 태블릿 또는 전용 월패드에서 앱을 실행합니다.
2. 상단 헤더의 **[💡 화면 켜짐 유지]** 버튼을 탭하면 **Screen Wake Lock API**가 동작하여 화면이 자동으로 꺼지지 않고 365일 24시간 가족 일정/날씨/시계가 상시 표시됩니다.
3. 네트워크가 일시 단절되더라도 **서비스 워커(`sw.js`)**와 **LocalStorage 캐시**를 통해 중단 없이 즉시 켜집니다.

---

### 1.4 PC / Mac 데스크탑 브라우저
- Chrome, Edge, Safari, Whale 등 모든 모던 브라우저에서 반응형 12열 와이드 그리드로 쾌적하게 이용 가능합니다.
- 크롬 주소창 우측의 [컴퓨터에 앱 설치] 아이콘을 클릭하여 독립 데스크탑 앱 창으로 분리 사용 가능합니다.

---

## 2. 모바일 앱 친화적 핵심 기능 (Mobile-First UX)

1. **스마트폰 전용 하단 바텀 탭 (Mobile Bottom Bar)**:
   - 모바일 화면(`md:hidden`)에서는 상단 메뉴 대신 하단 바텀 탭바(`📌대시보드`, `💰가계/영수증`, `🤖AI비서`, `📖시스템명세`)로 자동 전환되어 엄지손가락 동선 최적화.
2. **영수증 카메라 즉시 촬영 연동**:
   - 모바일에서 [사진 파일 선택] 터치 시 스마트폰 카메라가 즉시 실행되어 종이 영수증을 촬영하는 즉시 서버 OCR 엔진으로 업로드 및 자동 파싱.
3. **Safe Area Inset (아이폰 노치/하단 홈바 대응)**:
   - `viewport-fit=cover` 및 `pb-[env(safe-area-inset-bottom)]` 설계를 통해 최신 아이폰과 안드로이드 제스처 바에 콘텐츠가 가려지지 않음.
4. **오프라인 서비스 워커 (`sw.js`)**:
   - 정적 자산(HTML, CSS, JS, 아이콘)을 자동 프리캐싱하여 네트워크가 불안정한 환경에서도 0.1초 만에 앱 스플래시 및 대시보드 기동.

---

## 3. Capacitor 기반 네이티브 APK / IPA 앱 패키징 가이드 (선택사항)

구글 플레이스토어나 애플 앱스토어에 정식 앱으로 배포하고자 할 경우 프로젝트에 포함된 `capacitor.config.json`을 사용하여 즉시 네이티브 프로젝트로 변환할 수 있습니다:

```bash
# 1. Capacitor CLI 설치 (글로벌 또는 로컬)
npm install @capacitor/core @capacitor/cli @capacitor/android @capacitor/ios

# 2. 안드로이드 / iOS 플랫폼 추가
npx cap add android
npx cap add ios

# 3. 안드로이드 스튜디오에서 열기 (APK / AAB 빌드)
npx cap open android

# 4. Xcode에서 열기 (iOS IPA 빌드)
npx cap open ios
```

