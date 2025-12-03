# Interactive AI Digital Canvas

인터랙티브 AI 디지털 액자 프로젝트

라즈베리파이에 연결된 카메라로 사용자의 모습을 감지하고, AI가 해석하여 새로운 이미지를 생성하여 디스플레이에 보여주는 시스템입니다.

## 프로젝트 구조

```
project/
├── raspberry/          # 라즈베리파이 실행 코드
│   ├── main.py        # 메인 실행 파일
│   ├── camera/        # 카메라 관련 모듈
│   │   ├── capture.py # 카메라 캡처
│   │   └── detect.py  # 사람 감지 (OpenCV, MediaPipe)
│   ├── ui/            # 디스플레이 UI
│   │   └── display.py # 터치 디스플레이 제어
│   └── network/       # 네트워크 통신
│       └── client.py  # 서버 클라이언트
├── server/            # 서버 코드 (노트북/서버에서 실행)
│   ├── api/
│   │   ├── analyze.py # CLIP 기반 키워드 추출
│   │   ├── generate.py# 이미지 생성 API
│   │   └── app.py     # FastAPI 서버
│   └── model/
│       └── clip-model/# CLIP 모델 저장소
└── tests/             # 테스트 코드
```

## 시스템 아키텍처

### 1. 입력 (Input) - 카메라
- 라즈베리파이 카메라 모듈로 실시간 사람 감지
- OpenCV와 MediaPipe를 사용하여:
  - 사람 존재 여부 감지
  - 포즈 키포인트 추출
  - Bounding box 계산
  - 실루엣(mask) 추출

### 2. AI 해석 단계 - 서버
- **CLIP 모델**: 이미지 분석 및 키워드 추출
- **디퓨전 모델**: 키워드 기반 이미지 생성 (SDXL/FLUX 등)
- FastAPI 서버로 API 제공

### 3. 출력 (Output) - 디스플레이
- 생성된 이미지 표시
- 실시간 실루엣 표시
- 터치 UI로 모드 전환
- 다양한 디스플레이 모드 지원

## 설치 및 설정

### 라즈베리파이 측 (raspberry/)

```bash
# 필요한 패키지 설치
pip install opencv-python mediapipe numpy requests

# 실행
cd raspberry
python main.py
```

### 서버 측 (server/)

```bash
# 필요한 패키지 설치
pip install fastapi uvicorn torch torchvision pillow clip-by-openai diffusers

# CLIP 모델 다운로드 (자동)
# 이미지 생성 모델 설정 필요

# 서버 실행
cd server/api
python app.py
```

## 사용 방법

1. **서버 실행** (노트북/서버)
   ```bash
   cd server/api
   python app.py
   ```

2. **라즈베리파이 실행**
   ```bash
   cd raspberry
   # main.py에서 SERVER_URL을 서버 IP로 변경
   python main.py
   ```

3. **조작**
   - `q`: 종료
   - `m`: 디스플레이 모드 전환
   - 터치 디스플레이 모서리 터치: 모드 전환

## 디스플레이 모드

- `LIVE_CAMERA`: 실시간 카메라 화면
- `GENERATED_IMAGE`: 생성된 이미지 표시
- `SILHOUETTE`: 실루엣만 표시
- `MIXED`: 생성 이미지와 실루엣 블렌딩

## 개발 워크플로우

1. 노트북에서 개발 및 테스트
2. Git에 커밋 및 푸시
3. 라즈베리파이에서 Git pull
4. 라즈베리파이에서 실행

## 주의사항

- 서버의 CLIP 모델과 이미지 생성 모델 설정이 필요합니다
- 라즈베리파이와 서버가 같은 네트워크에 있어야 합니다
- 서버 URL은 `raspberry/main.py`에서 설정합니다

## 라이선스

MIT License
