import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchGallery, GalleryItem, getImageUrl } from '../api/server';
import { getAdminStats, deleteImage, logout, isAuthenticated } from '../api/auth';
import LoadingSpinner from '../components/LoadingSpinner';

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [items, setItems] = useState<GalleryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const [deleting, setDeleting] = useState<Set<string>>(new Set());
  const [selected, setSelected] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/admin/login');
      return;
    }

    loadData();
  }, [navigate]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [galleryResponse, statsResponse] = await Promise.all([
        fetchGallery(1, 100, false),
        getAdminStats()
      ]);
      setItems(galleryResponse.items);
      setStats(statsResponse);
      setSelected(new Set());
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleSelect = (imageId: string) => {
    setSelected(prev => {
      const newSet = new Set(prev);
      if (newSet.has(imageId)) {
        newSet.delete(imageId);
      } else {
        newSet.add(imageId);
      }
      return newSet;
    });
  };

  const selectAll = () => {
    if (selected.size === items.length) {
      setSelected(new Set());
    } else {
      setSelected(new Set(items.map(item => item.id)));
    }
  };

  const handleDeleteSingle = async (imageId: string) => {
    if (!confirm('정말 이 이미지를 삭제하시겠습니까?')) {
      return;
    }

    try {
      setDeleting(prev => new Set(prev).add(imageId));
      await deleteImage(imageId);
      setItems(items.filter(item => item.id !== imageId));
      setSelected(prev => {
        const newSet = new Set(prev);
        newSet.delete(imageId);
        return newSet;
      });
      const newStats = await getAdminStats();
      setStats(newStats);
    } catch (err: any) {
      alert(err.response?.data?.detail || '삭제에 실패했습니다.');
    } finally {
      setDeleting(prev => {
        const newSet = new Set(prev);
        newSet.delete(imageId);
        return newSet;
      });
    }
  };

  const handleDeleteSelected = async () => {
    if (selected.size === 0) {
      alert('삭제할 이미지를 선택하세요.');
      return;
    }

    if (!confirm(`선택한 ${selected.size}개의 이미지를 삭제하시겠습니까?`)) {
      return;
    }

    const selectedIds = Array.from(selected);
    setDeleting(new Set(selectedIds));

    let successCount = 0;
    let failCount = 0;

    for (const imageId of selectedIds) {
      try {
        await deleteImage(imageId);
        successCount++;
      } catch (err) {
        failCount++;
        console.error(`Failed to delete ${imageId}:`, err);
      }
    }

    // 목록 새로고침
    await loadData();

    if (failCount > 0) {
      alert(`${successCount}개 삭제 완료, ${failCount}개 실패`);
    }

    setDeleting(new Set());
  };

  const handleLogout = () => {
    logout();
    navigate('/admin/login');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" text="로딩 중..." />
      </div>
    );
  }

  const isAllSelected = items.length > 0 && selected.size === items.length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* 헤더 */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="font-display text-3xl sm:text-4xl font-bold text-gradient mb-2">
            관리자 대시보드
          </h1>
          <p className="text-dark-400">
            이미지 관리 및 통계
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/gallery')}
            className="px-4 py-2 rounded-lg bg-dark-800 border border-dark-700 text-dark-300 hover:text-white hover:border-dark-600 transition-all"
          >
            갤러리 보기
          </button>
          <button
            onClick={handleLogout}
            className="px-4 py-2 rounded-lg bg-red-500/20 border border-red-500/30 text-red-400 hover:bg-red-500/30 transition-all"
          >
            로그아웃
          </button>
        </div>
      </div>

      {/* 통계 */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <div className="glass rounded-xl p-6">
            <div className="text-sm text-dark-400 mb-1">전체 이미지</div>
            <div className="text-3xl font-bold text-white">{stats.total_images}</div>
          </div>
          <div className="glass rounded-xl p-6">
            <div className="text-sm text-dark-400 mb-1">생성 완료</div>
            <div className="text-3xl font-bold text-primary-400">{stats.generated_images}</div>
          </div>
          <div className="glass rounded-xl p-6">
            <div className="text-sm text-dark-400 mb-1">대기 중</div>
            <div className="text-3xl font-bold text-yellow-400">{stats.pending_images}</div>
          </div>
        </div>
      )}

      {/* 이미지 목록 */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">이미지 목록</h2>
          
          {items.length > 0 && (
            <div className="flex items-center gap-3">
              <button
                onClick={selectAll}
                className="px-4 py-2 rounded-lg bg-dark-800 border border-dark-700 text-dark-300 hover:text-white hover:border-dark-600 transition-all text-sm"
              >
                {isAllSelected ? '전체 해제' : '전체 선택'}
              </button>
              
              {selected.size > 0 && (
                <button
                  onClick={handleDeleteSelected}
                  disabled={deleting.size > 0}
                  className="px-4 py-2 rounded-lg bg-red-500 text-white text-sm font-medium hover:bg-red-600 disabled:opacity-50 transition-all"
                >
                  {deleting.size > 0 ? `삭제 중... (${deleting.size})` : `선택 삭제 (${selected.size})`}
                </button>
              )}
            </div>
          )}
        </div>

        {items.length === 0 ? (
          <div className="glass rounded-xl p-12 text-center">
            <p className="text-dark-400">이미지가 없습니다.</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {items.map((item) => {
              const isSelected = selected.has(item.id);
              const isDeleting = deleting.has(item.id);
              
              return (
                <div
                  key={item.id}
                  className={`relative group rounded-xl overflow-hidden border-2 transition-all cursor-pointer ${
                    isSelected 
                      ? 'border-primary-500 ring-2 ring-primary-500/30' 
                      : 'border-transparent hover:border-dark-600'
                  } ${isDeleting ? 'opacity-50' : ''}`}
                  onClick={() => !isDeleting && toggleSelect(item.id)}
                >
                  {/* 체크박스 */}
                  <div className={`absolute top-2 left-2 z-10 w-6 h-6 rounded-md border-2 flex items-center justify-center transition-all ${
                    isSelected 
                      ? 'bg-primary-500 border-primary-500' 
                      : 'bg-dark-900/80 border-dark-500 group-hover:border-dark-400'
                  }`}>
                    {isSelected && (
                      <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                  </div>

                  {/* 삭제 버튼 (개별) */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteSingle(item.id);
                    }}
                    disabled={isDeleting}
                    className="absolute top-2 right-2 z-10 w-8 h-8 rounded-lg bg-red-500/90 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600 disabled:opacity-50"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>

                  {/* 이미지 */}
                  <div className="aspect-square bg-dark-800">
                    <img
                      src={getImageUrl(item.generated_url || item.original_url)}
                      alt={item.description || 'Image'}
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                  </div>

                  {/* 정보 */}
                  <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/80 to-transparent">
                    <p className="text-xs text-white truncate">{item.id}</p>
                    {item.keywords && item.keywords.length > 0 && (
                      <p className="text-xs text-dark-400 truncate">{item.keywords.slice(0, 2).join(', ')}</p>
                    )}
                  </div>

                  {/* 삭제 중 오버레이 */}
                  {isDeleting && (
                    <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                      <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
