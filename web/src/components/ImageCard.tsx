import { Link } from 'react-router-dom';
import { GalleryItem, getImageUrl, getRelativeTime } from '../api/server';

interface ImageCardProps {
  item: GalleryItem;
  index?: number;
}

export default function ImageCard({ item, index = 0 }: ImageCardProps) {
  // 표시할 이미지 (생성된 이미지 우선, 없으면 원본)
  const displayImage = item.generated_url || item.original_url;
  const imageUrl = getImageUrl(displayImage);
  
  // 애니메이션 지연
  const animationDelay = `${index * 100}ms`;
  
  return (
    <Link
      to={`/detail/${item.id}`}
      className="group block card-hover rounded-2xl overflow-hidden glass animate-fade-in"
      style={{ animationDelay }}
    >
      {/* 이미지 컨테이너 */}
      <div className="relative aspect-square overflow-hidden bg-dark-800">
        <img
          src={imageUrl}
          alt={item.description || 'AI 생성 이미지'}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
          loading="lazy"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = 'data:image/svg+xml,' + encodeURIComponent(`
              <svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">
                <rect fill="#1a1a1f" width="400" height="400"/>
                <text fill="#4a4a55" font-family="system-ui" font-size="14" text-anchor="middle" x="200" y="200">
                  이미지를 불러올 수 없습니다
                </text>
              </svg>
            `);
          }}
        />
        
        {/* 오버레이 그라데이션 */}
        <div className="absolute inset-0 bg-gradient-to-t from-dark-950/90 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        
        {/* 생성 상태 뱃지 */}
        {item.generated_url && (
          <div className="absolute top-3 right-3">
            <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-primary-500/90 text-white backdrop-blur-sm">
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
              AI 생성
            </span>
          </div>
        )}
        
        {/* 호버 시 정보 표시 */}
        <div className="absolute bottom-0 left-0 right-0 p-4 translate-y-4 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300">
          {/* 키워드 */}
          {item.keywords.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-2">
              {item.keywords.slice(0, 3).map((keyword, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 rounded-full text-xs bg-dark-800/80 text-dark-200 backdrop-blur-sm"
                >
                  #{keyword}
                </span>
              ))}
              {item.keywords.length > 3 && (
                <span className="px-2 py-0.5 rounded-full text-xs bg-dark-800/80 text-dark-400 backdrop-blur-sm">
                  +{item.keywords.length - 3}
                </span>
              )}
            </div>
          )}
          
          {/* 시간 */}
          <p className="text-xs text-dark-300">
            {getRelativeTime(item.created_at)}
          </p>
        </div>
      </div>
      
      {/* 카드 하단 정보 (항상 표시) */}
      <div className="p-4">
        <p className="text-sm text-dark-200 line-clamp-2 mb-2">
          {item.description || '설명이 없습니다'}
        </p>
        <div className="flex items-center justify-between">
          <span className="text-xs text-dark-400">
            {getRelativeTime(item.created_at)}
          </span>
          <span className="text-xs text-primary-400 group-hover:text-primary-300 transition-colors flex items-center gap-1">
            자세히 보기
            <svg className="w-3 h-3 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </span>
        </div>
      </div>
    </Link>
  );
}

