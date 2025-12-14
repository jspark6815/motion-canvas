#!/bin/bash
# Motion Canvas 자동 시작 제거 스크립트

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=================================================${NC}"
echo -e "${YELLOW}🗑️ Motion Canvas 자동 시작 제거${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# systemd 서비스 제거
if [ -f /etc/systemd/system/motion-canvas.service ]; then
    echo -e "${YELLOW}systemd 서비스 제거 중...${NC}"
    sudo systemctl stop motion-canvas 2>/dev/null
    sudo systemctl disable motion-canvas 2>/dev/null
    sudo rm /etc/systemd/system/motion-canvas.service
    sudo systemctl daemon-reload
    echo -e "${GREEN}✅ systemd 서비스 제거 완료${NC}"
else
    echo -e "${CYAN}systemd 서비스가 설치되어 있지 않습니다.${NC}"
fi

# autostart 제거
AUTOSTART_FILE="$HOME/.config/autostart/motion-canvas.desktop"
if [ -f "$AUTOSTART_FILE" ]; then
    echo -e "${YELLOW}GUI 자동 시작 제거 중...${NC}"
    rm "$AUTOSTART_FILE"
    echo -e "${GREEN}✅ GUI 자동 시작 제거 완료${NC}"
else
    echo -e "${CYAN}GUI 자동 시작이 설치되어 있지 않습니다.${NC}"
fi

echo ""
echo -e "${GREEN}🎉 제거 완료!${NC}"

