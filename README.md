# 🎨 Motion Canvas - AI가 바라본 나

> **피지컬 컴퓨팅 기반 AI 미디어 아트 프로젝트**
> 
> 라즈베리파이가 포착한 순간을 AI가 예술 작품으로 재해석합니다.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18+-blue?logo=react)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-5-red?logo=raspberrypi)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📌 프로젝트 개요

**"Motion Canvas"**는 라즈베리파이5와 AI를 결합한 인터랙티브 미디어 아트 시스템입니다.

### 작동 흐름

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Motion Canvas 시스템                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐               │
│   │  Raspberry   │     │   EC2 서버   │     │   웹 갤러리   │               │
│   │    Pi 5      │────▶│   (FastAPI)  │────▶│   (React)    │               │
│   └──────────────┘     └──────────────┘     └──────────────┘               │
│          │                    │                    │                        │
│    ┌─────┴─────┐        ┌────┴────┐         ┌────┴────┐                    │
│    │• 사람 감지 │        │• 분석    │         │• 갤러리  │                    │
│    │• LED 피드백│        │• 생성    │         │• 스트림  │                    │
│    │• 실시간    │        │• 저장    │         │• 상세정보│                    │
│    │  스트림    │        │  (S3)    │         │          │                    │
│    └───────────┘        └─────────┘         └─────────┘                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. **사람 감지**: PIR 센서 + MediaPipe/HOG로 정확한 인체 감지
2. **촬영**: RGB LED 카운트다운(🔴→🟡→🟢→⚪) 후 고화질 촬영
3. **AI 분석**: Gemini Vision으로 키워드, 분위기, 색상 추출
4. **예술 작품 생성**: Gemini 2.0으로 독창적인 AI 아트 생성
5. **갤러리 공개**: AWS S3 저장 및 웹 갤러리에서 감상

---

## 📁 프로젝트 구조

```
motion-canvas/
│
├── 📁 raspberry/                    # 🍓 라즈베리파이 (Edge Device)
│   ├── main.py                      # 메인 실행 파일
│   ├── config.py                    # 환경변수 기반 설정
│   │
│   ├── 📁 camera/                   # 카메라 모듈
│   │   └── picam_source.py          # Picamera2 래퍼 (싱글톤)
│   │
│   ├── 📁 vision/                   # 컴퓨터 비전
│   │   ├── mediapipe_detector.py    # MediaPipe Pose 기반 감지 (딥러닝)
│   │   ├── person_detector.py       # OpenCV HOG 기반 감지
│   │   └── segmentation.py          # 이미지 크롭/패딩
│   │
│   ├── 📁 utils/                    # 유틸리티
│   │   ├── pir_sensor.py            # PIR 인체감지 센서
│   │   ├── rgb_led_controller.py    # RGB LED PWM 제어
│   │   ├── led_controller.py        # 단색 LED 제어
│   │   ├── image_encode.py          # JPEG/PNG 인코딩
│   │   └── countdown.py             # 카운트다운 표시
│   │
│   ├── 📁 stream/                   # 실시간 스트림
│   │   ├── mjpeg_server.py          # MJPEG 스트림 서버 (로컬)
│   │   └── websocket_pusher.py      # WebSocket 스트림 푸시 (EC2)
│   │
│   ├── 📁 network/                  # 네트워크
│   │   └── api_client.py            # HTTP API 클라이언트
│   │
│   ├── 📁 scripts/                  # 자동 시작 스크립트
│   │   ├── start.sh                 # 시작 스크립트
│   │   ├── motion-canvas.service    # systemd 서비스
│   │   ├── motion-canvas.desktop    # GUI autostart
│   │   ├── install.sh               # 설치 스크립트
│   │   └── uninstall.sh             # 제거 스크립트
│   │
│   └── requirements.txt
│
├── 📁 server/                       # ☁️ FastAPI 서버 (Backend)
│   ├── app.py                       # FastAPI 엔트리포인트
│   ├── schemas.py                   # Pydantic 모델
│   │
│   ├── 📁 routers/                  # API 라우터
│   │   ├── upload.py                # 이미지 업로드
│   │   ├── analyze.py               # AI 분석
│   │   ├── generate.py              # AI 이미지 생성
│   │   ├── gallery.py               # 갤러리 API
│   │   ├── stream.py                # 스트림 중계
│   │   └── admin.py                 # 관리자 API
│   │
│   ├── 📁 services/                 # 비즈니스 로직
│   │   ├── storage.py               # AWS S3 저장소
│   │   ├── analyzer.py              # Gemini Vision 분석
│   │   ├── generator.py             # Gemini 이미지 생성
│   │   ├── stream_relay.py          # 스트림 중계
│   │   └── auth.py                  # JWT 인증
│   │
│   ├── Dockerfile
│   └── requirements.txt
│
├── 📁 web/                          # 🌐 React 프론트엔드
│   ├── 📁 src/
│   │   ├── App.tsx                  # 라우터 설정
│   │   ├── 📁 pages/
│   │   │   ├── Home.tsx             # 홈 (작동원리, 시스템구성)
│   │   │   ├── Gallery.tsx          # 갤러리
│   │   │   ├── Detail.tsx           # 상세 페이지
│   │   │   ├── Stream.tsx           # 실시간 스트림
│   │   │   ├── AdminLogin.tsx       # 관리자 로그인
│   │   │   └── AdminDashboard.tsx   # 관리자 대시보드
│   │   ├── 📁 components/           # 공통 컴포넌트
│   │   └── 📁 api/                  # API 모듈
│   │
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
├── docker-compose.yml               # 개발용
├── docker-compose.prod.yml          # 프로덕션용
└── README.md
```

---

## 🎯 주요 기능

### 1. 사람 감지 시스템

#### MediaPipe (딥러닝 기반) - 기본값
- **33개 신체 랜드마크** 감지
- 높은 정확도, 낮은 오탐률
- 포즈 추정 가능

#### OpenCV HOG (전통적 방식) - 폴백
- Histogram of Oriented Gradients
- 빠른 처리 속도
- MediaPipe 미설치 시 자동 전환

#### PIR 적외선 센서 (선택사항)
- 적외선 기반 움직임 감지
- MediaPipe/HOG와 조합하여 정확도 향상
- 두 가지 모드:
  - **보조 모드**: PIR 감지 시 카메라 감지 수행
  - **필수 모드**: PIR + 카메라 감지 둘 다 필요

### 2. LED 피드백 시스템

#### RGB LED (PWM 제어)
- 카운트다운: 🔴 빨강 → 🟡 노랑 → 🟢 초록 → ⚪ 흰색 플래시
- 무지개 테스트 모드
- Common Anode/Cathode 지원

#### 단색 LED
- 간단한 깜빡임 피드백

### 3. 실시간 스트림

#### 로컬 MJPEG 서버
- 같은 네트워크에서 직접 접속
- `http://라즈베리파이IP:8080/stream.mjpg`

#### EC2 WebSocket 푸시
- 외부 네트워크에서도 접속 가능
- 라즈베리파이 → EC2 → 브라우저 중계
- 시크릿 키 인증

### 4. AI 분석 (Gemini Vision)

```json
{
  "keywords": ["사람", "실루엣", "움직임", "에너지", "존재"],
  "description": "한 사람의 형상이 공간 속에 존재하고 있습니다.",
  "mood": "신비로운",
  "colors": ["파랑", "보라", "검정"],
  "pose": "서있는 자세",
  "suggested_art_style": "추상 표현주의"
}
```

### 5. AI 이미지 생성 (Gemini 2.0)

- 분석 결과 기반 프롬프트 자동 생성
- 분위기별 스타일 적용
- 추상/초현실/인상주의 등 다양한 스타일

### 6. 웹 갤러리

- **홈**: 작동 원리, 시스템 구성, 기술 스택 소개
- **갤러리**: 생성된 작품 목록 (페이지네이션)
- **상세**: 원본/생성 이미지 비교, 분석 정보
- **스트림**: 실시간 카메라 영상
- **관리자**: 이미지 삭제, 통계

### 7. 이미지 처리 파이프라인

```
Picamera2 (RGB888/BGR) → cv2.imencode (JPEG) → HTTP 업로드 → S3 저장
                                    ↓
스트림에서도 동일한 인코딩 방식 사용 → 색상 일관성 보장
```

### 8. 자동 시작 (부팅 시)

#### systemd 서비스 (권장)
- 백그라운드 실행
- 자동 재시작
- journalctl 로그 관리

#### GUI 자동 시작
- 데스크톱에서 터미널 창 열림
- 디버깅에 용이

---

## 🔧 하드웨어 구성

### 필수 구성품

| 구성품 | 모델 | 용도 |
|--------|------|------|
| 싱글보드 컴퓨터 | Raspberry Pi 5 | 메인 컨트롤러 |
| 카메라 모듈 | Camera Module 3 | 이미지 촬영 |
| SD 카드 | 32GB+ | OS 및 프로그램 |
| 전원 어댑터 | 27W USB-C | 전원 공급 |

### 선택 구성품

| 구성품 | 모델 | 용도 |
|--------|------|------|
| PIR 센서 | HC-SR501 | 인체 감지 보조 |
| RGB LED | Common Cathode | 시각적 피드백 |
| 저항 | 220Ω × 3 | LED 전류 제한 |

### GPIO 핀 배치

```
Raspberry Pi 5 GPIO (BCM 번호)
┌─────────────────────────────────────┐
│  3.3V (1)  ●  ● (2) 5V             │  ← PIR VCC
│  GPIO2 (3) ●  ● (4) 5V             │
│  GPIO3 (5) ●  ● (6) GND            │  ← PIR GND, LED GND
│  GPIO4 (7) ●  ● (8) GPIO14         │  ← PIR OUT
│   GND (9)  ●  ● (10) GPIO15        │
│ GPIO17(11) ●  ● (12) GPIO18        │  ← RGB Red / 단색 LED
│ GPIO27(13) ●  ● (14) GND           │  ← RGB Green
│ GPIO22(15) ●  ● (16) GPIO23        │  ← RGB Blue
│            ...                      │
└─────────────────────────────────────┘
```

---

## 🚀 설치 및 실행

### 1. 서버 (EC2)

```bash
# 프로젝트 클론
git clone https://github.com/yourusername/motion-canvas.git
cd motion-canvas

# Docker Compose로 실행
docker-compose up -d

# 또는 수동 설치
cd server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 환경변수 설정
export GEMINI_API_KEY=your_api_key
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_S3_BUCKET=your_bucket_name

# 서버 실행
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

### 2. 웹 프론트엔드

```bash
cd web
npm install
npm run dev          # 개발 모드
npm run build        # 프로덕션 빌드
```

### 3. 라즈베리파이

```bash
# 1. 시스템 패키지 설치
sudo apt update
sudo apt install -y python3-opencv python3-picamera2 python3-gpiozero

# 2. 프로젝트 클론
cd ~
git clone https://github.com/yourusername/motion-canvas.git
cd motion-canvas/raspberry

# 3. 가상환경 생성 (시스템 패키지 포함)
python3 -m venv venv --system-site-packages
source venv/bin/activate

# 4. 패키지 설치
pip install -r requirements.txt

# 5. 환경변수 설정
nano .env
```

**.env 파일:**
```env
# 서버 설정
SERVER_HOST=https://your-server.com
SERVER_PORT=443

# 카메라 설정
CAMERA_WIDTH=1280
CAMERA_HEIGHT=720

# 감지 설정
DETECTION_ENABLED=true
USE_MEDIAPIPE=true
DETECTION_COOLDOWN_SECONDS=5.0
COUNTDOWN_SECONDS=3

# PIR 센서 (선택사항)
PIR_ENABLED=false
PIR_PIN=4
PIR_REQUIRE_FOR_CAPTURE=false

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

```bash
# 6. 실행
python -m raspberry.main

# 또는 자동 시작 설치
cd scripts
chmod +x install.sh
./install.sh
```

---

## 📡 API 엔드포인트

### 이미지 처리

| 엔드포인트 | 메서드 | 설명 |
|------------|--------|------|
| `/upload` | POST | Pi에서 이미지 업로드 |
| `/analyze/{id}` | GET | 분석 결과 조회 |
| `/generate/{id}` | GET | 생성 결과 조회 |

### 갤러리

| 엔드포인트 | 메서드 | 설명 |
|------------|--------|------|
| `/gallery` | GET | 갤러리 목록 (페이지네이션) |
| `/gallery/{id}` | GET | 상세 정보 |

### 스트림

| 엔드포인트 | 메서드 | 설명 |
|------------|--------|------|
| `/stream/push` | WebSocket | Pi → 서버 스트림 푸시 |
| `/stream/live.mjpg` | GET | MJPEG 스트림 |
| `/stream/snapshot.jpg` | GET | 현재 프레임 스냅샷 |
| `/stream/status` | GET | 스트림 상태 |

### 관리자

| 엔드포인트 | 메서드 | 설명 |
|------------|--------|------|
| `/admin/login` | POST | 로그인 (JWT 발급) |
| `/admin/me` | GET | 현재 사용자 정보 |
| `/admin/stats` | GET | 통계 |
| `/admin/images/{id}` | DELETE | 이미지 삭제 |

### 기타

| 엔드포인트 | 메서드 | 설명 |
|------------|--------|------|
| `/health` | GET | 서버 상태 확인 |

---

## 🛠 기술 스택

### 라즈베리파이 (Edge)

| 기술 | 버전 | 용도 |
|------|------|------|
| Python | 3.11+ | 메인 언어 |
| Picamera2 | 최신 | 카메라 제어 |
| OpenCV | 4.x | 이미지 처리, HOG 감지 |
| MediaPipe | 0.10+ | 딥러닝 사람 감지 |
| RPi.GPIO | 최신 | GPIO/PWM 제어 |
| aiohttp | 3.9+ | MJPEG 스트림 서버 |
| websockets | 12.0+ | WebSocket 클라이언트 |

### 서버 (Backend)

| 기술 | 버전 | 용도 |
|------|------|------|
| Python | 3.11+ | 메인 언어 |
| FastAPI | 0.100+ | 웹 프레임워크 |
| Pydantic | 2.x | 데이터 검증 |
| boto3 | 최신 | AWS S3 연동 |
| google-genai | 최신 | Gemini AI API |
| python-jose | 최신 | JWT 인증 |
| Pillow | 10.0+ | 이미지 처리 |

### 프론트엔드 (Web)

| 기술 | 버전 | 용도 |
|------|------|------|
| React | 18+ | UI 프레임워크 |
| TypeScript | 5.x | 타입 안전성 |
| Vite | 5.x | 빌드 도구 |
| Tailwind CSS | 3.x | 스타일링 |
| React Router | 6.x | 라우팅 |

### 인프라

| 기술 | 용도 |
|------|------|
| Docker | 컨테이너화 |
| Docker Compose | 멀티 컨테이너 관리 |
| Nginx | 리버스 프록시 |
| AWS EC2 | 서버 호스팅 |
| AWS S3 | 이미지 저장 |

---

## ⚙️ 환경변수 레퍼런스

### 라즈베리파이

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `SERVER_HOST` | `http://localhost` | 서버 호스트 |
| `SERVER_PORT` | `8000` | 서버 포트 |
| `CAMERA_WIDTH` | `1280` | 카메라 해상도 너비 |
| `CAMERA_HEIGHT` | `720` | 카메라 해상도 높이 |
| `CAMERA_FORMAT` | `RGB888` | 카메라 포맷 |
| `CAMERA_CAPTURE_INTERVAL` | `2.0` | 촬영 간격 (초) |
| `DETECTION_ENABLED` | `true` | 감지 활성화 |
| `USE_MEDIAPIPE` | `true` | MediaPipe 사용 |
| `DETECTION_MIN_CONFIDENCE` | `0.5` | 최소 감지 신뢰도 |
| `DETECTION_COOLDOWN_SECONDS` | `5.0` | 연속 촬영 방지 (초) |
| `COUNTDOWN_SECONDS` | `3` | 카운트다운 (초) |
| `PIR_ENABLED` | `false` | PIR 센서 활성화 |
| `PIR_PIN` | `4` | PIR GPIO 핀 |
| `PIR_REQUIRE_FOR_CAPTURE` | `false` | PIR+카메라 필수 |
| `RGB_LED_ENABLED` | `false` | RGB LED 활성화 |
| `RGB_LED_RED_PIN` | `17` | 빨강 GPIO 핀 |
| `RGB_LED_GREEN_PIN` | `27` | 초록 GPIO 핀 |
| `RGB_LED_BLUE_PIN` | `22` | 파랑 GPIO 핀 |
| `LED_ENABLED` | `true` | 단색 LED 활성화 |
| `LED_PIN` | `18` | 단색 LED GPIO 핀 |
| `STREAM_ENABLED` | `true` | 스트림 활성화 |
| `STREAM_PUSH_ENABLED` | `false` | EC2 푸시 활성화 |
| `STREAM_PUSH_URL` | - | WebSocket URL |
| `STREAM_PUSH_SECRET` | - | 인증 키 |

### 서버

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `GEMINI_API_KEY` | - | Gemini API 키 |
| `GEMINI_VISION_MODEL` | `gemini-1.5-flash-latest` | Vision 모델 |
| `GEMINI_IMAGE_MODEL` | `gemini-2.0-flash-exp` | 이미지 생성 모델 |
| `AWS_ACCESS_KEY_ID` | - | AWS 액세스 키 |
| `AWS_SECRET_ACCESS_KEY` | - | AWS 시크릿 키 |
| `AWS_S3_BUCKET` | - | S3 버킷 이름 |
| `AWS_REGION` | `ap-northeast-2` | AWS 리전 |
| `JWT_SECRET_KEY` | - | JWT 시크릿 |
| `ADMIN_USERNAME` | `admin` | 관리자 ID |
| `ADMIN_PASSWORD` | - | 관리자 비밀번호 |
| `STREAM_SECRET` | - | 스트림 인증 키 |

---

## 📊 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Motion Canvas Architecture                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌───────────────────────────────────────────────────────────────────┐    │
│   │                    🍓 Raspberry Pi 5 (Edge)                       │    │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐             │    │
│   │  │Picamera2│  │MediaPipe│  │   PIR   │  │ RGB LED │             │    │
│   │  │ Module3 │  │  /HOG   │  │ Sensor  │  │  PWM    │             │    │
│   │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘             │    │
│   │       │            │            │            │                    │    │
│   │       └────────────┴────────────┴────────────┘                    │    │
│   │                         │                                         │    │
│   │              ┌──────────┴──────────┐                             │    │
│   │              │     main.py         │                             │    │
│   │              │  (AIArtCapture)     │                             │    │
│   │              └──────────┬──────────┘                             │    │
│   │                         │                                         │    │
│   │         ┌───────────────┼───────────────┐                        │    │
│   │         ▼               ▼               ▼                        │    │
│   │   ┌──────────┐   ┌──────────┐   ┌──────────┐                    │    │
│   │   │  HTTP    │   │WebSocket │   │  MJPEG   │                    │    │
│   │   │ Upload   │   │  Push    │   │ Server   │                    │    │
│   │   └────┬─────┘   └────┬─────┘   └────┬─────┘                    │    │
│   └────────│──────────────│──────────────│───────────────────────────┘    │
│            │              │              │                                 │
│            ▼              ▼              │                                 │
│   ┌───────────────────────────────────────────────────────────────────┐   │
│   │                    ☁️ EC2 Server (FastAPI)                        │   │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐             │   │
│   │  │ Upload  │  │ Stream  │  │Analyzer │  │Generator│             │   │
│   │  │ Router  │  │ Relay   │  │(Gemini) │  │(Gemini) │             │   │
│   │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘             │   │
│   │       │            │            │            │                    │   │
│   │       └────────────┴────────────┴────────────┘                    │   │
│   │                         │                                         │   │
│   │              ┌──────────┴──────────┐                             │   │
│   │              │    AWS S3 Storage   │                             │   │
│   │              │  (uploads/generated │                             │   │
│   │              │     /metadata)      │                             │   │
│   │              └──────────┬──────────┘                             │   │
│   └─────────────────────────│─────────────────────────────────────────┘   │
│                             │                                              │
│                             ▼                                              │
│   ┌───────────────────────────────────────────────────────────────────┐   │
│   │                    🌐 React Web (Frontend)                        │   │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐             │   │
│   │  │  Home   │  │ Gallery │  │ Stream  │  │  Admin  │             │   │
│   │  │ (Info)  │  │ (List)  │  │ (Live)  │  │(Manage) │             │   │
│   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘             │   │
│   └───────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📝 개발 로그

- [x] **1단계**: 기본 프로젝트 구조 설계
- [x] **2단계**: 라즈베리파이 카메라/감지 모듈 구현
- [x] **3단계**: FastAPI 서버 구현
- [x] **4단계**: React 웹 프론트엔드 구현
- [x] **5단계**: Gemini Vision API 연동 (분석)
- [x] **6단계**: Gemini 2.0 이미지 생성 연동
- [x] **7단계**: AWS S3 스토리지 연동
- [x] **8단계**: 실시간 스트림 (WebSocket/MJPEG)
- [x] **9단계**: RGB LED 피드백 시스템
- [x] **10단계**: PIR 인체감지 센서 통합
- [x] **11단계**: MediaPipe 딥러닝 감지
- [x] **12단계**: 자동 시작 스크립트
- [x] **13단계**: Docker 컨테이너화

---

## 📄 라이선스

MIT License

---

## 👤 작성자

**피지컬 컴퓨팅 기반 AI 미디어 아트 프로젝트**

---

## 🙏 감사의 말

- Google Gemini AI
- Raspberry Pi Foundation
- MediaPipe Team
- FastAPI & React Communities
