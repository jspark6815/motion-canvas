#!/bin/bash

# 라즈베리파이 실행 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Interactive AI Canvas 시작 ==="

# 가상환경 활성화
if [ -d "venv" ]; then
    echo "가상환경 활성화 중..."
    source venv/bin/activate
else
    echo "가상환경이 없습니다. 먼저 ./setup.sh를 실행하세요."
    exit 1
fi

# 서버 URL 확인
if grep -q "http://localhost:8000" main.py; then
    echo ""
    echo "⚠ 경고: main.py에서 SERVER_URL이 localhost로 설정되어 있습니다."
    echo "   서버 IP 주소로 변경해주세요."
    echo ""
    read -p "계속하시겠습니까? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 실행
echo "시작 중... (종료하려면 Ctrl+C)"
echo ""

python main.py

