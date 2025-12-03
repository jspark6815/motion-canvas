#!/bin/bash

# 라즈베리파이 한글 설정 스크립트

set -e

echo "=== 라즈베리파이 한글 설정 ==="
echo ""

# 1. 로케일 설치
echo "1. 로케일 설치 중..."
sudo apt-get update
sudo apt-get install -y locales

# 2. 한국어 로케일 생성
echo ""
echo "2. 한국어 로케일 생성 중..."
sudo locale-gen ko_KR.UTF-8

# 3. 한글 폰트 설치
echo ""
echo "3. 한글 폰트 설치 중..."
sudo apt-get install -y fonts-nanum fonts-nanum-coding fonts-nanum-extra

# 4. 폰트 캐시 업데이트
echo ""
echo "4. 폰트 캐시 업데이트 중..."
sudo fc-cache -fv

# 5. 로케일 설정 (사용자별)
echo ""
echo "5. 로케일 설정 중..."
if ! grep -q "LANG=ko_KR.UTF-8" ~/.bashrc; then
    echo 'export LANG=ko_KR.UTF-8' >> ~/.bashrc
    echo 'export LC_ALL=ko_KR.UTF-8' >> ~/.bashrc
    echo "   ✓ ~/.bashrc에 로케일 설정 추가됨"
else
    echo "   ✓ ~/.bashrc에 이미 로케일 설정이 있습니다"
fi

# 6. 현재 세션에 적용
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8

# 7. 시스템 전체 설정 (선택사항)
echo ""
read -p "시스템 전체에 적용하시겠습니까? (모든 사용자, y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if ! grep -q "LANG=ko_KR.UTF-8" /etc/default/locale 2>/dev/null; then
        echo "LANG=ko_KR.UTF-8" | sudo tee -a /etc/default/locale > /dev/null
        echo "LC_ALL=ko_KR.UTF-8" | sudo tee -a /etc/default/locale > /dev/null
        echo "   ✓ 시스템 전체 로케일 설정 완료"
    else
        echo "   ✓ 시스템 전체 로케일이 이미 설정되어 있습니다"
    fi
fi

# 8. 테스트
echo ""
echo "6. 한글 출력 테스트:"
echo "안녕하세요"
echo ""

# 9. 설정 확인
echo "현재 로케일 설정:"
locale | grep -E "LANG|LC_ALL"

echo ""
echo "=== 설정 완료 ==="
echo ""
echo "다음 중 하나를 선택하세요:"
echo "1. 새 터미널을 열기 (권장)"
echo "2. 재부팅: sudo reboot"
echo "3. 현재 세션에서 테스트: echo '안녕하세요'"
echo ""

