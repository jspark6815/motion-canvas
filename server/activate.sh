#!/bin/bash

# 가상환경 활성화 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"

if [ ! -d "$VENV_PATH" ]; then
    echo "가상환경이 없습니다. 생성 중..."
    python3 -m venv "$VENV_PATH"
fi

echo "가상환경 활성화 중..."
source "$VENV_PATH/bin/activate"

echo "가상환경이 활성화되었습니다."
echo "비활성화하려면 'deactivate'를 입력하세요."

