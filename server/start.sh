#!/bin/bash

# 서버 시작 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Interactive AI Canvas Server 시작 ==="

# 가상환경 활성화 (있는 경우)
if [ -d "venv" ]; then
    echo "가상환경 활성화 중..."
    source venv/bin/activate
else
    echo "가상환경이 없습니다. 생성 중..."
    python3 -m venv venv
    source venv/bin/activate
fi

# 서버 디렉토리로 이동
cd api

# 서버 실행
echo "서버 시작 중... (포트 8000)"
echo "종료하려면 Ctrl+C를 누르세요."
echo ""

python app.py

