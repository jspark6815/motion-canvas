import { useState, useEffect, useCallback } from 'react';
import { fetchGallery, GalleryItem } from '../api/server';
import ImageCard from '../components/ImageCard';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';

export default function Gallery() {
  const [items, setItems] = useState<GalleryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [total, setTotal] = useState(0);
  const [generatedOnly, setGeneratedOnly] = useState(false);
  
  const PAGE_SIZE = 12;
  
  const loadImages = useCallback(async (pageNum: number, reset: boolean = false) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetchGallery(pageNum, PAGE_SIZE, generatedOnly);
      
      if (reset) {
        setItems(response.items);
      } else {
        setItems(prev => [...prev, ...response.items]);
      }
      
      setTotal(response.total);
      setHasMore(response.items.length === PAGE_SIZE && pageNum * PAGE_SIZE < response.total);
      
    } catch (err) {
      console.error('Failed to load gallery:', err);
      setError('갤러리를 불러오는데 실패했습니다. 서버 연결을 확인해주세요.');
    } finally {
      setLoading(false);
    }
  }, [generatedOnly]);
  
  // 초기 로드
  useEffect(() => {
    setPage(1);
    loadImages(1, true);
  }, [generatedOnly, loadImages]);
  
  // 더 보기
  const loadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    loadImages(nextPage);
  };
  
  // 새로고침
  const refresh = () => {
    setPage(1);
    loadImages(1, true);
  };
  
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* 헤더 */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="font-display text-3xl sm:text-4xl font-bold text-gradient mb-2">
            갤러리
          </h1>
          <p className="text-dark-400">
            {total > 0 ? `총 ${total}개의 작품` : 'AI가 생성한 예술 작품들'}
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          {/* 필터 토글 */}
          <button
            onClick={() => setGeneratedOnly(!generatedOnly)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              generatedOnly
                ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                : 'bg-dark-800 text-dark-300 border border-dark-700 hover:border-dark-600'
            }`}
          >
            {generatedOnly ? '✨ AI 생성만' : '📷 전체 보기'}
          </button>
          
          {/* 새로고침 버튼 */}
          <button
            onClick={refresh}
            disabled={loading}
            className="p-2 rounded-lg bg-dark-800 border border-dark-700 hover:border-dark-600 text-dark-300 hover:text-white transition-all disabled:opacity-50"
            title="새로고침"
          >
            <svg 
              className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`}
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" 
              />
            </svg>
          </button>
        </div>
      </div>
      
      {/* 에러 상태 */}
      {error && (
        <div className="glass rounded-xl p-4 mb-8 border border-red-500/30 bg-red-500/10">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}
      
      {/* 로딩 상태 (초기 로드) */}
      {loading && items.length === 0 && (
        <div className="flex items-center justify-center min-h-[400px]">
          <LoadingSpinner size="lg" text="갤러리를 불러오는 중..." />
        </div>
      )}
      
      {/* 빈 상태 */}
      {!loading && items.length === 0 && !error && (
        <EmptyState
          title="아직 작품이 없습니다"
          description="라즈베리파이가 사람을 감지하면 자동으로 이미지가 생성됩니다. 카메라 앞에 서보세요!"
          action={{
            label: '새로고침',
            onClick: refresh,
          }}
        />
      )}
      
      {/* 이미지 그리드 */}
      {items.length > 0 && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {items.map((item, index) => (
              <ImageCard key={item.id} item={item} index={index} />
            ))}
          </div>
          
          {/* 더 보기 버튼 */}
          {hasMore && (
            <div className="flex justify-center mt-12">
              <button
                onClick={loadMore}
                disabled={loading}
                className="px-8 py-3 rounded-xl bg-dark-800 border border-dark-700 hover:border-primary-500/50 text-dark-200 hover:text-white font-medium transition-all disabled:opacity-50 flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <LoadingSpinner size="sm" />
                    로딩 중...
                  </>
                ) : (
                  <>
                    더 보기
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </>
                )}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

