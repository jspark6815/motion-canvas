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
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-center mb-16">
            <span className="text-gradient">어떻게 작동하나요?</span>
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* 단계 1 */}
            <div className="glass rounded-2xl p-8 text-center card-hover">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center mx-auto mb-6 shadow-lg shadow-blue-500/30">
                <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-3">1. 촬영</h3>
              <p className="text-dark-400">
                라즈베리파이5에 연결된 카메라가
                <br />
                사람을 자동으로 감지하고 촬영합니다
              </p>
            </div>
            
            {/* 단계 2 */}
            <div className="glass rounded-2xl p-8 text-center card-hover">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center mx-auto mb-6 shadow-lg shadow-purple-500/30">
                <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-3">2. AI 분석</h3>
              <p className="text-dark-400">
                Gemini Vision AI가 이미지를 분석하여
                <br />
                키워드와 분위기를 추출합니다
              </p>
            </div>
            
            {/* 단계 3 */}
            <div className="glass rounded-2xl p-8 text-center card-hover">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-pink-400 to-pink-600 flex items-center justify-center mx-auto mb-6 shadow-lg shadow-pink-500/30">
                <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-3">3. 예술 작품 생성</h3>
              <p className="text-dark-400">
                AI가 분석 결과를 바탕으로
                <br />
                독창적인 예술 이미지를 생성합니다
              </p>
            </div>
          </div>
        </div>
      </section>
      
      {/* 시스템 구성 섹션 */}
      <section className="relative py-24 px-4 bg-dark-900/50">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="font-display text-3xl sm:text-4xl font-bold mb-8">
            <span className="text-gradient">시스템 구성</span>
          </h2>
          
          <div className="glass rounded-2xl p-8 text-left">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              <div className="space-y-2">
                <div className="text-primary-400 font-semibold">🍇 Raspberry Pi 5</div>
                <ul className="text-sm text-dark-400 space-y-1">
                  <li>• 카메라 모듈 3</li>
                  <li>• MediaPipe 사람 감지</li>
                  <li>• 자동 촬영 & 업로드</li>
                </ul>
              </div>
              
              <div className="space-y-2">
                <div className="text-purple-400 font-semibold">⚡ FastAPI Server</div>
                <ul className="text-sm text-dark-400 space-y-1">
                  <li>• 이미지 업로드 처리</li>
                  <li>• Gemini API 연동</li>
                  <li>• 메타데이터 관리</li>
                </ul>
              </div>
              
              <div className="space-y-2">
                <div className="text-pink-400 font-semibold">🌐 React Web</div>
                <ul className="text-sm text-dark-400 space-y-1">
                  <li>• 갤러리 뷰어</li>
                  <li>• 상세 정보 표시</li>
                  <li>• 반응형 디자인</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

