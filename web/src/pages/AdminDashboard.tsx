import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchGallery, GalleryItem } from '../api/server';
import { getAdminStats, deleteImage, logout, isAuthenticated } from '../api/auth';
import ImageCard from '../components/ImageCard';
import LoadingSpinner from '../components/LoadingSpinner';

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [items, setItems] = useState<GalleryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const [deleting, setDeleting] = useState<string | null>(null);

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
        fetchGallery(1, 50, false),
        getAdminStats()
      ]);
      setItems(galleryResponse.items);
      setStats(statsResponse);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (imageId: string) => {
    if (!confirm('정말 이 이미지를 삭제하시겠습니까?')) {
      return;
    }

    try {
      setDeleting(imageId);
      await deleteImage(imageId);
      // 목록에서 제거
      setItems(items.filter(item => item.id !== imageId));
      // 통계 업데이트
      const newStats = await getAdminStats();
      setStats(newStats);
    } catch (err: any) {
      alert(err.response?.data?.detail || '삭제에 실패했습니다.');
    } finally {
      setDeleting(null);
    }
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
        <h2 className="text-xl font-semibold text-white mb-4">이미지 목록</h2>
        {items.length === 0 ? (
          <div className="glass rounded-xl p-12 text-center">
            <p className="text-dark-400">이미지가 없습니다.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {items.map((item) => (
              <div key={item.id} className="relative group">
                <ImageCard item={item} index={0} />
                <button
                  onClick={() => handleDelete(item.id)}
                  disabled={deleting === item.id}
                  className="absolute top-2 left-2 px-3 py-1 rounded-lg bg-red-500/90 text-white text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600 disabled:opacity-50"
                >
                  {deleting === item.id ? '삭제 중...' : '삭제'}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

