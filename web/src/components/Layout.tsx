import { Outlet, Link, useLocation } from 'react-router-dom';

export default function Layout() {
  const location = useLocation();
  
  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };
  
  return (
    <div className="min-h-screen flex flex-col">
      {/* 헤더 */}
      <header className="glass sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* 로고 */}
            <Link 
              to="/" 
              className="flex items-center gap-3 group"
            >
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center shadow-lg shadow-primary-500/30 group-hover:shadow-primary-500/50 transition-shadow">
                <svg 
                  className="w-6 h-6 text-white" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" 
                  />
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" 
                  />
                </svg>
              </div>
              <div>
                <h1 className="font-display text-xl font-semibold text-gradient">
                  AI가 바라본 나
                </h1>
                <p className="text-xs text-dark-400 hidden sm:block">
                  AI Art Gallery
                </p>
              </div>
            </Link>
            
            {/* 네비게이션 */}
            <nav className="flex items-center gap-1">
              <Link
                to="/"
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive('/') && !isActive('/gallery')
                    ? 'bg-primary-500/10 text-primary-400'
                    : 'text-dark-300 hover:text-white hover:bg-dark-800'
                }`}
              >
                홈
              </Link>
              <Link
                to="/gallery"
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive('/gallery')
                    ? 'bg-primary-500/10 text-primary-400'
                    : 'text-dark-300 hover:text-white hover:bg-dark-800'
                }`}
              >
                갤러리
              </Link>
            </nav>
          </div>
        </div>
      </header>
      
      {/* 메인 콘텐츠 */}
      <main className="flex-1">
        <Outlet />
      </main>
      
      {/* 푸터 */}
      <footer className="border-t border-dark-800 py-8 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="text-sm text-dark-400">
              © 2024 AI가 바라본 나. 피지컬 컴퓨팅 기반 AI 미디어 아트 프로젝트
            </div>
            <div className="flex items-center gap-4 text-sm text-dark-400">
              <span>Raspberry Pi + Gemini AI + React</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

