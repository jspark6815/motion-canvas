# Motion Canvas 자동 시작 스크립트

라즈베리파이 부팅 시 Motion Canvas를 자동으로 실행하는 스크립트입니다.

## 📁 파일 구성

```
scripts/
├── start.sh                 # 메인 시작 스크립트
├── motion-canvas.service    # systemd 서비스 파일
├── motion-canvas.desktop    # GUI autostart 파일
├── install.sh               # 설치 스크립트
├── uninstall.sh             # 제거 스크립트
└── README.md                # 이 파일
```

## 🚀 빠른 설치

라즈베리파이에서 다음 명령어를 실행하세요:

```bash
cd ~/motion-canvas/raspberry/scripts
chmod +x install.sh
./install.sh
```

설치 스크립트가 두 가지 방법 중 선택하도록 안내합니다.

---

## 📋 설치 방법 상세

### 방법 1: systemd 서비스 (권장) ⭐

백그라운드에서 안정적으로 실행됩니다. 서버/헤드리스 환경에 적합합니다.

**장점:**
- 부팅 시 자동 시작
- 오류 시 자동 재시작
- `journalctl`로 로그 관리
- 서비스 상태 모니터링 가능

**수동 설치:**
```bash
# 서비스 파일 복사
sudo cp motion-canvas.service /etc/systemd/system/

# 서비스 활성화 (부팅 시 자동 시작)
sudo systemctl daemon-reload
sudo systemctl enable motion-canvas

# 서비스 시작
sudo systemctl start motion-canvas
```

**유용한 명령어:**
```bash
# 상태 확인
sudo systemctl status motion-canvas

# 서비스 중지
sudo systemctl stop motion-canvas

# 서비스 재시작
sudo systemctl restart motion-canvas

# 실시간 로그 보기
journalctl -u motion-canvas -f

# 최근 로그 100줄 보기
journalctl -u motion-canvas -n 100
```

---

### 방법 2: GUI 터미널 자동 실행

데스크톱 환경에서 터미널 창을 열어 실행합니다.

**장점:**
- 터미널에서 로그를 직접 볼 수 있음
- 디버깅에 용이

**수동 설치:**
```bash
# autostart 디렉토리 생성
mkdir -p ~/.config/autostart

# desktop 파일 복사
cp motion-canvas.desktop ~/.config/autostart/

# 라즈베리파이 재부팅
sudo reboot
```

---

## ⚙️ 사전 요구사항

### 1. 프로젝트 클론
```bash
cd ~
git clone <repository-url> motion-canvas
```

### 2. 가상환경 설정
```bash
cd ~/motion-canvas/raspberry
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 환경변수 설정
```bash
# .env 파일 생성
cp .env.example .env  # 또는 직접 생성

# 필요한 값 설정
nano .env
```

**.env 예시:**
```env
# 서버 설정
SERVER_HOST=https://your-server.com
SERVER_PORT=443

# 카메라 설정
CAMERA_WIDTH=1280
CAMERA_HEIGHT=720

# 감지 설정
DETECTION_ENABLED=true
COUNTDOWN_SECONDS=3

# PIR 인체감지 센서 설정 (선택사항)
# HC-SR501 연결: VCC→5V, GND→GND, OUT→GPIO4
PIR_ENABLED=false
PIR_PIN=4
PIR_REQUIRE_FOR_CAPTURE=false  # true: PIR+HOG 둘 다 필요

# LED 설정
RGB_LED_ENABLED=true
RGB_LED_RED_PIN=17
RGB_LED_GREEN_PIN=27
RGB_LED_BLUE_PIN=22

# 스트림 설정
STREAM_PUSH_ENABLED=true
STREAM_PUSH_URL=ws://your-server.com:8000/stream/push
STREAM_PUSH_SECRET=your-secret-key
```

---

## 🔧 문제 해결

### 서비스가 시작되지 않을 때
```bash
# 상태 확인
sudo systemctl status motion-canvas

# 자세한 로그 확인
journalctl -u motion-canvas -n 50 --no-pager
```

### 카메라 권한 오류
```bash
# 사용자를 video 그룹에 추가
sudo usermod -a -G video $USER

# 재로그인 또는 재부팅 필요
```

### GPIO 권한 오류
```bash
# 사용자를 gpio 그룹에 추가
sudo usermod -a -G gpio $USER

# 재로그인 또는 재부팅 필요
```

### 가상환경을 찾을 수 없을 때
```bash
# 가상환경 다시 생성
cd ~/motion-canvas/raspberry
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🗑️ 제거

```bash
cd ~/motion-canvas/raspberry/scripts
chmod +x uninstall.sh
./uninstall.sh
```

또는 수동으로:

```bash
# systemd 서비스 제거
sudo systemctl stop motion-canvas
sudo systemctl disable motion-canvas
sudo rm /etc/systemd/system/motion-canvas.service
sudo systemctl daemon-reload

# GUI autostart 제거
rm ~/.config/autostart/motion-canvas.desktop
```

---

## 📝 수동 실행

자동 시작 없이 수동으로 실행하려면:

```bash
cd ~/motion-canvas/raspberry
source venv/bin/activate
python -m raspberry.main
```

또는 시작 스크립트 사용:

```bash
./scripts/start.sh
```

