#!/bin/bash
# Motion Canvas 자동 시작 설치 스크립트
# 라즈베리파이에서 실행하세요.

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}=================================================${NC}"
echo -e "${GREEN}🎨 Motion Canvas 자동 시작 설치${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# 현재 사용자 확인
CURRENT_USER=$(whoami)
echo -e "${CYAN}현재 사용자: $CURRENT_USER${NC}"

# 프로젝트 경로
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
echo -e "${CYAN}프로젝트 경로: $PROJECT_DIR${NC}"
echo ""

# 실행 권한 부여
echo -e "${YELLOW}📝 스크립트 실행 권한 설정...${NC}"
chmod +x "$SCRIPT_DIR/start.sh"

# 방법 선택
echo -e "${BLUE}=================================================${NC}"
echo -e "${CYAN}자동 시작 방법을 선택하세요:${NC}"
echo ""
echo -e "  ${GREEN}1)${NC} systemd 서비스 (권장)"
echo -e "     - 백그라운드에서 실행"
echo -e "     - 자동 재시작 지원"
echo -e "     - 로그 관리 (journalctl)"
echo ""
echo -e "  ${GREEN}2)${NC} GUI 터미널 자동 실행"
echo -e "     - 데스크톱에서 터미널 창 열림"
echo -e "     - 로그를 직접 볼 수 있음"
echo ""
echo -e "  ${GREEN}3)${NC} 둘 다 설치하지 않음 (취소)"
echo ""
echo -e "${BLUE}=================================================${NC}"

read -p "선택 (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo -e "${YELLOW}📦 systemd 서비스 설치 중...${NC}"
        
        # 서비스 파일에서 사용자 이름 변경
        SERVICE_FILE="$SCRIPT_DIR/motion-canvas.service"
        TEMP_SERVICE="/tmp/motion-canvas.service"
        
        # 현재 사용자로 경로 변경
        sed "s|/home/pi|$HOME|g; s|User=pi|User=$CURRENT_USER|g; s|Group=pi|Group=$CURRENT_USER|g" \
            "$SERVICE_FILE" > "$TEMP_SERVICE"
        
        # 서비스 파일 복사
        sudo cp "$TEMP_SERVICE" /etc/systemd/system/motion-canvas.service
        rm "$TEMP_SERVICE"
        
        # systemd 리로드
        sudo systemctl daemon-reload
        
        # 서비스 활성화
        sudo systemctl enable motion-canvas
        
        echo ""
        echo -e "${GREEN}✅ systemd 서비스 설치 완료!${NC}"
        echo ""
        echo -e "${CYAN}유용한 명령어:${NC}"
        echo -e "  ${YELLOW}sudo systemctl start motion-canvas${NC}   # 시작"
        echo -e "  ${YELLOW}sudo systemctl stop motion-canvas${NC}    # 중지"
        echo -e "  ${YELLOW}sudo systemctl status motion-canvas${NC}  # 상태 확인"
        echo -e "  ${YELLOW}journalctl -u motion-canvas -f${NC}       # 실시간 로그"
        echo ""
        
        read -p "지금 서비스를 시작할까요? (y/n): " start_now
        if [ "$start_now" = "y" ] || [ "$start_now" = "Y" ]; then
            sudo systemctl start motion-canvas
            echo -e "${GREEN}✅ 서비스가 시작되었습니다.${NC}"
            sudo systemctl status motion-canvas --no-pager
        fi
        ;;
        
    2)
        echo ""
        echo -e "${YELLOW}📦 GUI 자동 시작 설치 중...${NC}"
        
        # autostart 디렉토리 생성
        mkdir -p "$HOME/.config/autostart"
        
        # desktop 파일에서 경로 변경
        DESKTOP_FILE="$SCRIPT_DIR/motion-canvas.desktop"
        DEST_FILE="$HOME/.config/autostart/motion-canvas.desktop"
        
        # 현재 사용자 경로로 변경
        sed "s|\$HOME|$HOME|g" "$DESKTOP_FILE" > "$DEST_FILE"
        
        echo ""
        echo -e "${GREEN}✅ GUI 자동 시작 설치 완료!${NC}"
        echo ""
        echo -e "${CYAN}다음 재부팅 시 터미널 창이 자동으로 열립니다.${NC}"
        echo ""
        echo -e "${YELLOW}제거하려면:${NC}"
        echo -e "  rm $DEST_FILE"
        ;;
        
    3)
        echo ""
        echo -e "${YELLOW}설치가 취소되었습니다.${NC}"
        exit 0
        ;;
        
    *)
        echo -e "${RED}잘못된 선택입니다.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}=================================================${NC}"
echo -e "${GREEN}🎉 설치 완료!${NC}"
echo -e "${BLUE}=================================================${NC}"

