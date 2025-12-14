#!/bin/bash
# Motion Canvas 시작 스크립트
# 라즈베리파이 부팅 시 자동 실행됩니다.

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${GREEN}🎨 Motion Canvas - AI Art Capture System${NC}"
echo -e "${BLUE}=================================================${NC}"

# 프로젝트 디렉토리
PROJECT_DIR=~/motion-canvas
RASPBERRY_DIR="$PROJECT_DIR/raspberry"

# 프로젝트 디렉토리 존재 확인
if [ ! -d "$RASPBERRY_DIR" ]; then
    echo -e "${RED}❌ 오류: $RASPBERRY_DIR 디렉토리가 존재하지 않습니다.${NC}"
    echo -e "${YELLOW}프로젝트를 먼저 클론하세요:${NC}"
    echo "  git clone <repository-url> $PROJECT_DIR"
    exit 1
fi

cd "$RASPBERRY_DIR"
echo -e "${YELLOW}📁 작업 디렉토리: $(pwd)${NC}"

# 가상환경 활성화
VENV_DIR="$RASPBERRY_DIR/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}📦 가상환경 생성 중...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${YELLOW}📥 의존성 설치 중...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo -e "${GREEN}✅ 가상환경 활성화: $VIRTUAL_ENV${NC}"

# 환경변수 파일 확인
if [ -f "$RASPBERRY_DIR/.env" ]; then
    echo -e "${GREEN}✅ .env 파일 로드됨${NC}"
else
    echo -e "${YELLOW}⚠️ .env 파일이 없습니다. 기본 설정으로 실행합니다.${NC}"
fi

# 네트워크 대기 (선택사항)
echo -e "${YELLOW}🌐 네트워크 연결 대기 중...${NC}"
sleep 5

# Python 실행
echo -e "${BLUE}🚀 Motion Canvas 시작...${NC}"
echo ""

# PYTHONPATH 설정 및 실행
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
python -m raspberry.main

# 스크립트 종료 (보통 여기까지 도달하지 않음)
echo -e "${RED}⚠️ 프로그램이 종료되었습니다.${NC}"

