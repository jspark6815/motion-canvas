#!/bin/bash

# 라즈베리파이 환경 설정 스크립트

set -e  # 오류 발생 시 중단

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== 라즈베리파이 환경 설정 시작 ==="
echo ""

# 1. 가상환경 생성
if [ ! -d "venv" ]; then
    echo "1. 가상환경 생성 중..."
    python3 -m venv venv
    echo "   ✓ 가상환경 생성 완료"
else
    echo "1. 가상환경이 이미 존재합니다."
fi

# 2. 가상환경 활성화
echo ""
echo "2. 가상환경 활성화 중..."
source venv/bin/activate
echo "   ✓ 가상환경 활성화 완료"

# 3. pip 업그레이드
echo ""
echo "3. pip 업그레이드 중..."
pip install --upgrade pip > /dev/null 2>&1
echo "   ✓ pip 업그레이드 완료"

# 4. 패키지 설치
echo ""
echo "4. 필수 패키지 설치 중..."
echo "   - opencv-python"
pip install opencv-python > /dev/null 2>&1 || echo "   ⚠ opencv-python 설치 실패 (계속 진행)"

echo "   - mediapipe"
pip install mediapipe > /dev/null 2>&1 || echo "   ⚠ mediapipe 설치 실패 (계속 진행)"

echo "   - numpy"
pip install numpy > /dev/null 2>&1 || echo "   ⚠ numpy 설치 실패 (계속 진행)"

echo "   - requests"
pip install requests > /dev/null 2>&1 || echo "   ⚠ requests 설치 실패 (계속 진행)"

echo "   - pillow (한글 폰트 지원)"
pip install pillow > /dev/null 2>&1 || echo "   ⚠ pillow 설치 실패 (계속 진행)"

echo "   ✓ 패키지 설치 완료"

# 5. 설치 확인
echo ""
echo "5. 설치 확인 중..."
python3 -c "import cv2; print('   ✓ OpenCV:', cv2.__version__)" 2>/dev/null || echo "   ⚠ OpenCV 확인 실패"
python3 -c "import mediapipe; print('   ✓ MediaPipe 설치됨')" 2>/dev/null || echo "   ⚠ MediaPipe 확인 실패"
python3 -c "import numpy; print('   ✓ NumPy:', numpy.__version__)" 2>/dev/null || echo "   ⚠ NumPy 확인 실패"
python3 -c "import requests; print('   ✓ Requests:', requests.__version__)" 2>/dev/null || echo "   ⚠ Requests 확인 실패"
python3 -c "from PIL import Image; print('   ✓ Pillow 설치됨')" 2>/dev/null || echo "   ⚠ Pillow 확인 실패"

echo ""
echo "=== 환경 설정 완료 ==="
echo ""
echo "다음 단계:"
echo "1. main.py에서 SERVER_URL을 서버 IP로 설정"
echo "2. 카메라 모듈이 활성화되어 있는지 확인"
echo "3. ./start.sh 또는 python main.py로 실행"
echo ""

