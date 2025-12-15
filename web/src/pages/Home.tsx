import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { checkHealth } from '../api/server';

export default function Home() {
  const [serverStatus, setServerStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  
  useEffect(() => {
    const checkServerStatus = async () => {
      try {
        await checkHealth();
        setServerStatus('online');
      } catch {
        setServerStatus('offline');
      }
    };
    
    checkServerStatus();
    const interval = setInterval(checkServerStatus, 30000);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="relative overflow-hidden">
      {/* 배경 그라데이션 */}
      <div className="absolute inset-0 bg-gradient-to-b from-primary-950/30 via-dark-950 to-dark-950" />
      
      {/* 배경 패턴 */}
      <div 
        className="absolute inset-0 opacity-5"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }}
      />
      
      {/* 히어로 섹션 */}
      <section className="relative min-h-[80vh] flex items-center justify-center px-4">
        <div className="max-w-4xl mx-auto text-center">
          {/* 서버 상태 */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-8 animate-fade-in">
            <span 
              className={`w-2 h-2 rounded-full ${
                serverStatus === 'online' 
                  ? 'bg-green-400 animate-pulse' 
                  : serverStatus === 'offline'
                  ? 'bg-red-400'
                  : 'bg-yellow-400 animate-pulse'
              }`}
            />
            <span className="text-sm text-dark-300">
              {serverStatus === 'online' 
                ? '서버 연결됨' 
                : serverStatus === 'offline'
                ? '서버 오프라인'
                : '연결 확인 중...'}
            </span>
          </div>
          
          {/* 타이틀 */}
          <h1 className="font-display text-5xl sm:text-7xl font-bold mb-6 animate-slide-up">
            <span className="text-gradient">AI가 바라본</span>
            <br />
            <span className="text-white">나의 모습</span>
          </h1>
          
          {/* 서브타이틀 */}
          <p className="text-lg sm:text-xl text-dark-300 max-w-2xl mx-auto mb-10 animate-slide-up animation-delay-100">
            라즈베리파이 카메라가 포착한 순간을
            <br className="hidden sm:block" />
            AI가 예술 작품으로 재해석합니다
          </p>
          
          {/* CTA 버튼 */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-slide-up animation-delay-200">
            <Link
              to="/gallery"
              className="group px-8 py-4 rounded-xl bg-gradient-to-r from-primary-500 to-primary-600 text-white font-semibold text-lg shadow-lg shadow-primary-500/30 hover:shadow-primary-500/50 hover:scale-105 transition-all"
            >
              갤러리 보기
              <span className="inline-block ml-2 group-hover:translate-x-1 transition-transform">
                →
              </span>
            </Link>
            
            <a
              href="#how-it-works"
              className="px-8 py-4 rounded-xl border border-dark-600 text-dark-200 font-medium hover:bg-dark-800 hover:border-dark-500 transition-all"
            >
              작동 원리 알아보기
            </a>
          </div>
        </div>
        
        {/* 스크롤 인디케이터 */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <svg className="w-6 h-6 text-dark-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>
      </section>
      
      {/* 작동 원리 섹션 */}
      <section id="how-it-works" className="relative py-24 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-center mb-6">
            <span className="text-gradient">어떻게 작동하나요?</span>
          </h2>
          <p className="text-center text-dark-400 mb-16 max-w-2xl mx-auto">
            라즈베리파이에서 촬영된 사진이 클라우드를 거쳐 AI 예술 작품으로 변환되는 과정입니다
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* 단계 1: 감지 */}
            <div className="glass rounded-2xl p-6 text-center card-hover relative">
              <div className="absolute -top-3 -left-3 w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-sm font-bold text-white shadow-lg">1</div>
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-blue-500/30">
                <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-2">사람 감지</h3>
              <p className="text-dark-400 text-sm mb-3">
                OpenCV HOG 알고리즘으로<br />
                사람을 자동 감지합니다
              </p>
              <div className="text-xs text-dark-500 space-y-1">
                <div>• 신뢰도 임계값 필터링</div>
                <div>• 쿨다운으로 연속 촬영 방지</div>
              </div>
            </div>
            
            {/* 단계 2: 촬영 */}
            <div className="glass rounded-2xl p-6 text-center card-hover relative">
              <div className="absolute -top-3 -left-3 w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-sm font-bold text-white shadow-lg">2</div>
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-green-500/30">
                <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-2">촬영 & 업로드</h3>
              <p className="text-dark-400 text-sm mb-3">
                RGB LED 카운트다운 후<br />
                고화질 사진을 촬영합니다
              </p>
              <div className="text-xs text-dark-500 space-y-1">
                <div>• 🔴→🟡→🟢→⚪ LED 신호</div>
                <div>• OpenCV JPEG 인코딩</div>
                <div>• EC2 서버로 HTTP 업로드</div>
              </div>
            </div>
            
            {/* 단계 3: 분석 */}
            <div className="glass rounded-2xl p-6 text-center card-hover relative">
              <div className="absolute -top-3 -left-3 w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center text-sm font-bold text-white shadow-lg">3</div>
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-purple-500/30">
                <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-2">AI 분석</h3>
              <p className="text-dark-400 text-sm mb-3">
                Gemini Vision AI가<br />
                이미지를 분석합니다
              </p>
              <div className="text-xs text-dark-500 space-y-1">
                <div>• 5개 키워드 추출</div>
                <div>• 분위기 & 색상 분석</div>
                <div>• 예술 스타일 추천</div>
              </div>
            </div>
            
            {/* 단계 4: 생성 */}
            <div className="glass rounded-2xl p-6 text-center card-hover relative">
              <div className="absolute -top-3 -left-3 w-8 h-8 rounded-full bg-pink-500 flex items-center justify-center text-sm font-bold text-white shadow-lg">4</div>
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-pink-400 to-pink-600 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-pink-500/30">
                <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-2">예술 작품 생성</h3>
              <p className="text-dark-400 text-sm mb-3">
                Gemini 2.0이 분석 결과로<br />
                독창적인 작품을 생성합니다
              </p>
              <div className="text-xs text-dark-500 space-y-1">
                <div>• 분위기별 스타일 적용</div>
                <div>• 추상/초현실/인상주의 등</div>
                <div>• S3에 저장 & 갤러리 공개</div>
              </div>
            </div>
          </div>
          
          {/* 연결선 (데스크톱만) */}
          <div className="hidden lg:flex justify-center items-center mt-8 text-dark-600">
            <div className="flex items-center gap-2 text-sm">
              <span className="text-blue-400">라즈베리파이</span>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
              <span className="text-purple-400">EC2 서버</span>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
              <span className="text-pink-400">S3 & 웹 갤러리</span>
            </div>
          </div>
        </div>
      </section>
      
      {/* 실시간 스트림 섹션 */}
      <section className="relative py-24 px-4 bg-dark-900/50">
        <div className="max-w-5xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-center mb-6">
            <span className="text-gradient">실시간 스트림</span>
          </h2>
          <p className="text-center text-dark-400 mb-12 max-w-2xl mx-auto">
            WebSocket을 통해 라즈베리파이의 카메라 영상을 실시간으로 확인할 수 있습니다
          </p>
          
          <div className="glass rounded-2xl p-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
              {/* 스트림 프리뷰 영역 */}
              <div className="bg-dark-900 rounded-xl aspect-video flex items-center justify-center border border-dark-700">
                <div className="text-center text-dark-500">
                  <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  <p className="text-sm">실시간 스트림 미리보기</p>
                </div>
              </div>
              
              {/* 스트림 설명 */}
              <div className="space-y-4">
                <h3 className="text-xl font-semibold text-white">스트림 중계 시스템</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <div className="w-2 h-2 rounded-full bg-green-400"></div>
                    </div>
                    <div>
                      <div className="text-dark-200 font-medium">WebSocket 푸시</div>
                      <div className="text-dark-400">라즈베리파이가 EC2 서버로 JPEG 프레임 전송</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <div className="w-2 h-2 rounded-full bg-blue-400"></div>
                    </div>
                    <div>
                      <div className="text-dark-200 font-medium">MJPEG 중계</div>
                      <div className="text-dark-400">서버가 브라우저에 실시간 영상 중계</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <div className="w-2 h-2 rounded-full bg-purple-400"></div>
                    </div>
                    <div>
                      <div className="text-dark-200 font-medium">스냅샷 캡처</div>
                      <div className="text-dark-400">현재 프레임을 정지 이미지로 저장 가능</div>
                    </div>
                  </div>
                </div>
                <a
                  href="/stream"
                  className="inline-flex items-center gap-2 mt-4 px-4 py-2 rounded-lg bg-primary-500/20 border border-primary-500/30 text-primary-400 hover:bg-primary-500/30 transition-colors text-sm"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  실시간 스트림 보기
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      {/* 시스템 구성 섹션 */}
      <section className="relative py-24 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-center mb-6">
            <span className="text-gradient">시스템 구성</span>
          </h2>
          <p className="text-center text-dark-400 mb-12 max-w-2xl mx-auto">
            엣지 디바이스부터 클라우드까지, 전체 시스템 아키텍처입니다
          </p>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 라즈베리파이 */}
            <div className="glass rounded-2xl p-6 border border-dark-800">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                  <span className="text-xl">🍓</span>
                </div>
                <div>
                  <h3 className="font-semibold text-white">Raspberry Pi 5</h3>
                  <p className="text-xs text-dark-400">Edge Device</p>
                </div>
              </div>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2 text-dark-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400"></span>
                  <span>Picamera2 카메라 모듈 3</span>
                </li>
                <li className="flex items-center gap-2 text-dark-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400"></span>
                  <span>1280×720 해상도 (RGB888)</span>
                </li>
                <li className="flex items-center gap-2 text-dark-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400"></span>
                  <span>OpenCV HOG 사람 감지</span>
                </li>
                <li className="flex items-center gap-2 text-dark-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400"></span>
                  <span>RGB LED 피드백 (PWM)</span>
                </li>
                <li className="flex items-center gap-2 text-dark-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400"></span>
                  <span>WebSocket 스트림 푸시</span>
                </li>
                <li className="flex items-center gap-2 text-dark-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400"></span>
                  <span>환경변수 기반 설정</span>
                </li>
                </ul>
              </div>
              
            {/* EC2 서버 */}
            <div className="glass rounded-2xl p-6 border border-dark-800">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-orange-500/20 flex items-center justify-center">
                  <span className="text-xl">☁️</span>
                </div>
                <div>
                  <h3 className="font-semibold text-white">EC2 + FastAPI</h3>
                  <p className="text-xs text-dark-400">Backend Server</p>
                </div>
              </div>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2 text-dark-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-orange-400"></span>
                  <span>이미지 업로드 수신</span>
                </li>
                <li className="flex items-center gap-2 text-dark-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-orange-400"></span>
                  <span>WebSocket 스트림 수신</span>
                </li>
                <li className="flex items-center gap-2 text-dark-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-orange-400"></span>
                  <span>MJPEG 스트림 중계</span>
                </li>
                <li className="flex items-center gap-2 text-dark-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-orange-400"></span>
                  <span>Gemini Vision 이미지 분석</span>
                </li>
                <li className="flex items-center gap-2 text-dark-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-orange-400"></span>
                  <span>Gemini 2.0 이미지 생성</span>
                </li>
                <li className="flex items-center gap-2 text-dark-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-orange-400"></span>
                  <span>백그라운드 작업 처리</span>
                </li>
              </ul>
            </div>
            
            {/* 저장소 & 웹 */}
            <div className="glass rounded-2xl p-6 border border-dark-800">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                  <span className="text-xl">🗄️</span>
                </div>
                <div>
                  <h3 className="font-semibold text-white">S3 + React</h3>
                  <p className="text-xs text-dark-400">Storage & Frontend</p>
                </div>
              </div>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2 text-dark-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                  <span>AWS S3 이미지 저장</span>
                </li>
                <li className="flex items-center gap-2 text-dark-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                  <span>JSON 메타데이터 관리</span>
                </li>
                <li className="flex items-center gap-2 text-dark-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                  <span>React + TypeScript 웹앱</span>
                </li>
                <li className="flex items-center gap-2 text-dark-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                  <span>Tailwind CSS 스타일링</span>
                </li>
                <li className="flex items-center gap-2 text-dark-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                  <span>갤러리 & 상세 뷰어</span>
                </li>
                <li className="flex items-center gap-2 text-dark-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                  <span>실시간 스트림 뷰어</span>
                </li>
                </ul>
            </div>
          </div>
        </div>
      </section>
      
      {/* 기술 스택 섹션 */}
      <section className="relative py-24 px-4 bg-dark-900/50">
        <div className="max-w-4xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-center mb-12">
            <span className="text-gradient">기술 스택</span>
          </h2>
          
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {/* 기술 스택 아이템들 */}
            {[
              { name: 'Python', category: 'Backend', color: 'from-blue-400 to-yellow-400' },
              { name: 'FastAPI', category: 'Backend', color: 'from-teal-400 to-green-400' },
              { name: 'Picamera2', category: 'Hardware', color: 'from-green-400 to-emerald-400' },
              { name: 'OpenCV', category: 'Vision', color: 'from-blue-400 to-blue-600' },
              { name: 'Gemini AI', category: 'AI', color: 'from-blue-400 to-purple-400' },
              { name: 'WebSocket', category: 'Network', color: 'from-orange-400 to-red-400' },
              { name: 'AWS S3', category: 'Storage', color: 'from-orange-400 to-orange-600' },
              { name: 'React', category: 'Frontend', color: 'from-cyan-400 to-blue-400' },
              { name: 'TypeScript', category: 'Frontend', color: 'from-blue-400 to-blue-600' },
              { name: 'Tailwind', category: 'Styling', color: 'from-cyan-400 to-teal-400' },
              { name: 'Docker', category: 'DevOps', color: 'from-blue-400 to-cyan-400' },
              { name: 'Nginx', category: 'Server', color: 'from-green-400 to-green-600' },
            ].map((tech) => (
              <div 
                key={tech.name}
                className="glass rounded-xl p-4 text-center card-hover border border-dark-800"
              >
                <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${tech.color} opacity-80 mx-auto mb-2`}></div>
                <div className="font-medium text-white text-sm">{tech.name}</div>
                <div className="text-xs text-dark-500">{tech.category}</div>
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {/* 이미지 처리 파이프라인 섹션 */}
      <section className="relative py-24 px-4">
        <div className="max-w-4xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-center mb-6">
            <span className="text-gradient">이미지 처리 파이프라인</span>
          </h2>
          <p className="text-center text-dark-400 mb-12 max-w-2xl mx-auto">
            색상 정확도를 위한 BGR 기반 이미지 처리 흐름
          </p>
          
          <div className="glass rounded-2xl p-8">
            <div className="space-y-6">
              {/* 파이프라인 단계들 */}
              <div className="flex flex-col md:flex-row items-center gap-4 md:gap-2">
                <div className="flex-1 bg-dark-800 rounded-lg p-4 text-center">
                  <div className="text-xs text-dark-400 mb-1">Picamera2</div>
                  <div className="font-mono text-sm text-green-400">RGB888</div>
                  <div className="text-xs text-dark-500 mt-1">(실제 BGR 순서)</div>
                </div>
                <svg className="w-6 h-6 text-dark-600 rotate-90 md:rotate-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
                <div className="flex-1 bg-dark-800 rounded-lg p-4 text-center">
                  <div className="text-xs text-dark-400 mb-1">cv2.imencode</div>
                  <div className="font-mono text-sm text-blue-400">JPEG</div>
                  <div className="text-xs text-dark-500 mt-1">BGR 입력 그대로</div>
                </div>
                <svg className="w-6 h-6 text-dark-600 rotate-90 md:rotate-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
                <div className="flex-1 bg-dark-800 rounded-lg p-4 text-center">
                  <div className="text-xs text-dark-400 mb-1">서버 업로드</div>
                  <div className="font-mono text-sm text-purple-400">S3 저장</div>
                  <div className="text-xs text-dark-500 mt-1">정확한 색상</div>
                </div>
              </div>
              
              <div className="text-center text-sm text-dark-400 bg-dark-800/50 rounded-lg p-4">
                <span className="text-primary-400">💡 핵심:</span> 스트림과 업로드 모두 동일한 OpenCV 인코딩 방식을 사용하여 색상 일관성 보장
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

