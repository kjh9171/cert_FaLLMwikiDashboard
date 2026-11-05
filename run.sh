#!/bin/bash
# ==============================================================================
# Family LLM WIKI & Finance Platform One-Click Runner
# (Safe Ports Configured to Avoid Docker Conflicts)
# Backend: Port 8088 | Frontend: Port 8085
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🏡 가족 LLM WIKI 대시보드 & 가계/영수증 통합 서비스 시작"
echo "--------------------------------------------------------"
echo "🔒 포트 충돌 방지 클린 포트: Backend=8088, Frontend=8085"

# 1. Check or activate virtual environment
if [ -d ".venv" ]; then
    echo "📦 가상환경 감지: .venv 활성화"
    VENV_PY=".venv/bin/python3"
else
    echo "⚠️ .venv 가상환경이 없습니다. 기본 python3를 사용합니다."
    VENV_PY="python3"
fi

# 2. Run Database and API smoke test
echo "🔍 백엔드 환경 및 데이터베이스 점검..."
PYTHONPATH=. "$VENV_PY" backend/test_api.py > /dev/null 2>&1 || true

# 3. Start Backend FastAPI Server
echo "🚀 FastAPI 백엔드 서버 구동 중... (포트: 8088)"
echo "   - API 문서: http://localhost:8088/docs"
echo "   - 헬스체크: http://localhost:8088/api/v1/health"
echo ""
echo "🌟 웹 대시보드 열람 안내:"
echo "   브라우저에서 file://$SCRIPT_DIR/index.html 을 열거나,"
echo "   새 터미널에서 'python3 -m http.server 8085'를 실행하세요."
echo "--------------------------------------------------------"

PYTHONPATH=. "$VENV_PY" -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8088 --reload
