# 🎨 AI가 바라본 나 (AI Art Gallery)

라즈베리파이 + AI Backend + React Web Viewer로 구성된 피지컬 컴퓨팅 기반 AI 미디어 아트 프로젝트입니다.

## 📌 프로젝트 개요

"AI가 바라본 나"는 다음과 같은 흐름으로 동작합니다:

1. **라즈베리파이5 + 카메라 모듈3**가 사람을 인식
2. 사람의 실루엣/영역 이미지를 서버로 업로드
3. **서버**에서 Gemini Vision으로 키워드/설명 추출
4. **Gemini Image Generation**으로 AI 예술 작품 생성
5. **React 웹**에서 갤러리 형태로 결과 확인

```
사용자 → Pi 카메라 → Pi가 사람 감지 → 이미지 서버 업로드 →
→ 서버: 키워드 분석 + 이미지 생성 → DB/폴더 저장 →
→ React 웹: 갤러리/상세 페이지에서 생성 이미지 확인
```

## 📁 프로젝트 구조

```
project-root/
│
├── raspberry/           # 라즈베리파이용 코드
│   ├── main.py         # 메인 실행 파일
│   ├── camera/         # 카메라 모듈
│   ├── vision/         # 사람 감지/세그멘테이션
│   ├── network/        # API 클라이언트
│   ├── utils/          # 유틸리티
│   ├── config.py       # 설정
│   └── requirements.txt
│
├── server/             # FastAPI 기반 AI 서버
│   ├── app.py          # FastAPI 엔트리포인트
│   ├── routers/        # API 라우터
│   ├── services/       # 비즈니스 로직
│   ├── schemas.py      # Pydantic 모델
│   └── requirements.txt
│
└── web/                # React 웹 프론트엔드
    ├── src/
    │   ├── pages/      # 페이지 컴포넌트
    │   ├── components/ # 공통 컴포넌트
    │   └── api/        # API 모듈
    └── package.json
```

## 🚀 빠른 시작

### 1. 서버 실행

```bash
cd server

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에서 GEMINI_API_KEY 설정

# 서버 실행
python -m uvicorn server.app:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면 http://localhost:8000/docs 에서 API 문서를 확인할 수 있습니다.

### 2. 웹 프론트엔드 실행

```bash
cd web

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

웹이 실행되면 http://localhost:5173 에서 확인할 수 있습니다.

### 3. 라즈베리파이 설정 (Pi에서 실행)

```bash
cd raspberry

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# config.py에서 서버 주소 수정
# server_config의 host를 실제 서버 IP로 변경

# 실행
python -m raspberry.main
```

## 🔧 상세 설정

### 서버 환경 변수 (.env)

```env
HOST=0.0.0.0
PORT=8000
GEMINI_API_KEY=your_api_key_here
```

### 라즈베리파이 설정 (config.py)

```python
@dataclass
class ServerConfig:
    host: str = "http://YOUR_SERVER_IP"  # 서버 IP 주소
    port: int = 8000
```

### 웹 환경 변수

```env
VITE_API_URL=http://localhost:8000
```

## 📡 API 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|------------|--------|------|
| `/upload` | POST | Pi에서 이미지 업로드 |
| `/analyze` | POST | 이미지 분석 (키워드 추출) |
| `/analyze/{id}` | GET | 분석 결과 조회 |
| `/generate` | POST | AI 이미지 생성 |
| `/generate/{id}` | GET | 생성 결과 조회 |
| `/gallery` | GET | 갤러리 목록 |
| `/gallery/{id}` | GET | 상세 정보 |
| `/health` | GET | 서버 상태 확인 |

## 🛠 기술 스택

### 라즈베리파이
- Python 3.11+
- Picamera2
- MediaPipe (사람 감지)
- Requests

### 서버
- Python 3.11+
- FastAPI
- Pydantic
- Pillow
- Google Generative AI (Gemini)

### 웹
- React 18
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Axios

## 📝 개발 단계

- [x] **1단계**: 기본 구조 생성
- [x] **2단계**: 라즈베리파이 코드 구현
- [x] **3단계**: FastAPI 서버 구현
- [x] **4단계**: React 웹 구현
- [ ] **5단계**: Gemini API 연동

## 🔮 5단계: Gemini API 연동 방법

### analyzer.py에서 Gemini Vision 연동

```python
import google.generativeai as genai

# 초기화
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# 이미지 분석
response = model.generate_content([
    "이미지를 분석해주세요...",
    {"mime_type": "image/jpeg", "data": base64_image}
])
```

### generator.py에서 이미지 생성 연동

```python
# Imagen 3 모델 사용
imagen_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
result = imagen_model.generate_images(
    prompt="예술적인 이미지 생성...",
    number_of_images=1
)
```

## 📄 라이선스

MIT License

## 👤 작성자

피지컬 컴퓨팅 AI 미디어 아트 프로젝트
