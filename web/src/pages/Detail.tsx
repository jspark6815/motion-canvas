import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { fetchDetail, DetailResponse, getImageUrl, formatDate } from '../api/server';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Detail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [detail, setDetail] = useState<DetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeImage, setActiveImage] = useState<'original' | 'generated'>('generated');
  
  useEffect(() => {
    const loadDetail = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        setError(null);
        const response = await fetchDetail(id);
        setDetail(response);
        
        // 생성된 이미지가 있으면 기본으로 표시
        if (response.generated_url) {
          setActiveImage('generated');
        } else {
          setActiveImage('original');
        }
      } catch (err) {
        console.error('Failed to load detail:', err);
        setError('이미지 정보를 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };
    
    loadDetail();
  }, [id]);
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" text="작품 정보를 불러오는 중..." />
      </div>
    );
  }
  
  if (error || !detail) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <div className="w-20 h-20 rounded-full bg-dark-800 flex items-center justify-center mx-auto mb-6">
          <svg className="w-10 h-10 text-dark-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold mb-2">{error || '작품을 찾을 수 없습니다'}</h2>
        <button
          onClick={() => navigate('/gallery')}
          className="mt-4 px-6 py-2 rounded-lg bg-primary-500 hover:bg-primary-600 text-white transition-colors"
        >
          갤러리로 돌아가기
        </button>
      </div>
    );
  }
  
  const displayUrl = activeImage === 'generated' && detail.generated_url 
    ? getImageUrl(detail.generated_url)
    : getImageUrl(detail.original_url);
  
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* 뒤로가기 */}
      <Link
        to="/gallery"
        className="inline-flex items-center gap-2 text-dark-400 hover:text-white transition-colors mb-8"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        갤러리로 돌아가기
      </Link>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">
        {/* 이미지 섹션 */}
        <div className="space-y-4">
          {/* 메인 이미지 */}
          <div className="relative aspect-square rounded-2xl overflow-hidden glass">
            <img
              src={displayUrl}
              alt={detail.description || 'AI 생성 이미지'}
              className="w-full h-full object-cover"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.src = 'data:image/svg+xml,' + encodeURIComponent(`
                  <svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
                    <rect fill="#1a1a1f" width="512" height="512"/>
                    <text fill="#4a4a55" font-family="system-ui" font-size="16" text-anchor="middle" x="256" y="256">
                      이미지를 불러올 수 없습니다
                    </text>
                  </svg>
                `);
              }}
            />
            
            {/* 이미지 타입 뱃지 */}
            <div className="absolute top-4 right-4">
              <span className={`px-3 py-1 rounded-full text-sm font-medium backdrop-blur-sm ${
                activeImage === 'generated' 
                  ? 'bg-primary-500/90 text-white'
                  : 'bg-dark-800/90 text-dark-200'
              }`}>
                {activeImage === 'generated' ? '✨ AI 생성' : '📷 원본'}
              </span>
            </div>
          </div>
          
          {/* 이미지 전환 버튼 */}
          {detail.generated_url && (
            <div className="flex gap-2">
              <button
                onClick={() => setActiveImage('original')}
                className={`flex-1 py-3 rounded-xl text-sm font-medium transition-all ${
                  activeImage === 'original'
                    ? 'bg-dark-700 text-white'
                    : 'bg-dark-800/50 text-dark-400 hover:bg-dark-800'
                }`}
              >
                📷 원본 이미지
              </button>
              <button
                onClick={() => setActiveImage('generated')}
                className={`flex-1 py-3 rounded-xl text-sm font-medium transition-all ${
                  activeImage === 'generated'
                    ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                    : 'bg-dark-800/50 text-dark-400 hover:bg-dark-800'
                }`}
              >
                ✨ AI 생성 이미지
              </button>
            </div>
          )}
        </div>
        
        {/* 정보 섹션 */}
        <div className="space-y-6">
          {/* 제목 & 설명 */}
          <div>
            <h1 className="font-display text-2xl sm:text-3xl font-bold mb-4">
              AI가 바라본 순간
            </h1>
            <p className="text-dark-300 text-lg leading-relaxed">
              {detail.description || '설명이 없습니다'}
            </p>
          </div>
          
          {/* 키워드 */}
          {detail.keywords.length > 0 && (
            <div>
              <h2 className="text-sm font-semibold text-dark-400 uppercase tracking-wider mb-3">
                키워드
              </h2>
              <div className="flex flex-wrap gap-2">
                {detail.keywords.map((keyword, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 rounded-full text-sm bg-dark-800 text-dark-200 border border-dark-700"
                  >
                    #{keyword}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {/* 분위기 & 색상 */}
          <div className="grid grid-cols-2 gap-4">
            {detail.mood && (
              <div className="glass rounded-xl p-4">
                <h3 className="text-sm font-semibold text-dark-400 mb-2">분위기</h3>
                <p className="text-lg font-medium text-primary-400">{detail.mood}</p>
              </div>
            )}
            
            {detail.colors.length > 0 && (
              <div className="glass rounded-xl p-4">
                <h3 className="text-sm font-semibold text-dark-400 mb-2">주요 색상</h3>
                <div className="flex flex-wrap gap-1">
                  {detail.colors.map((color, index) => (
                    <span key={index} className="text-sm text-dark-300">
                      {color}{index < detail.colors.length - 1 && ', '}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          {/* 프롬프트 (있는 경우) */}
          {detail.prompt_used && (
            <div className="glass rounded-xl p-4">
              <h3 className="text-sm font-semibold text-dark-400 mb-2">사용된 프롬프트</h3>
              <p className="text-sm text-dark-300 whitespace-pre-wrap">
                {detail.prompt_used}
              </p>
            </div>
          )}
          
          {/* 타임라인 */}
          <div className="glass rounded-xl p-4">
            <h3 className="text-sm font-semibold text-dark-400 mb-4">타임라인</h3>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-blue-400" />
                <span className="text-sm text-dark-400">촬영</span>
                <span className="text-sm text-dark-200 ml-auto">
                  {formatDate(detail.created_at)}
                </span>
              </div>
              
              {detail.analyzed_at && (
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-purple-400" />
                  <span className="text-sm text-dark-400">분석 완료</span>
                  <span className="text-sm text-dark-200 ml-auto">
                    {formatDate(detail.analyzed_at)}
                  </span>
                </div>
              )}
              
              {detail.generated_at && (
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-primary-400" />
                  <span className="text-sm text-dark-400">이미지 생성</span>
                  <span className="text-sm text-dark-200 ml-auto">
                    {formatDate(detail.generated_at)}
                  </span>
                </div>
              )}
            </div>
          </div>
          
          {/* 다운로드 버튼 */}
          <div className="flex gap-3">
            <a
              href={displayUrl}
              download={`ai-art-${detail.id}.png`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 py-3 rounded-xl bg-primary-500 hover:bg-primary-600 text-white font-medium text-center transition-colors flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              다운로드
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

