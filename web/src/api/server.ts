/**
 * 서버 API 모듈
 * FastAPI 서버와의 통신을 담당합니다.
 */
import axios, { AxiosInstance } from 'axios';

// API 기본 URL (개발 환경에서는 Vite 프록시 사용)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Axios 인스턴스 생성
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 타입 정의
export interface GalleryItem {
  id: string;
  original_url: string;
  generated_url: string | null;
  thumbnail_url: string | null;
  keywords: string[];
  description: string;
  created_at: string;
}

export interface GalleryResponse {
  total: number;
  items: GalleryItem[];
  page: number;
  page_size: number;
}

export interface DetailResponse {
  id: string;
  original_url: string;
  generated_url: string | null;
  keywords: string[];
  description: string;
  mood: string;
  colors: string[];
  prompt_used: string | null;
  created_at: string;
  analyzed_at: string | null;
  generated_at: string | null;
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
}

// API 함수들

/**
 * 갤러리 목록 조회
 */
export async function fetchGallery(
  page: number = 1,
  pageSize: number = 20,
  generatedOnly: boolean = false
): Promise<GalleryResponse> {
  const response = await api.get<GalleryResponse>('/gallery', {
    params: {
      page,
      page_size: pageSize,
      generated_only: generatedOnly,
    },
  });
  return response.data;
}

/**
 * 이미지 상세 정보 조회
 */
export async function fetchDetail(imageId: string): Promise<DetailResponse> {
  const response = await api.get<DetailResponse>(`/gallery/${imageId}`);
  return response.data;
}

/**
 * 서버 상태 확인
 */
export async function checkHealth(): Promise<HealthResponse> {
  const response = await api.get<HealthResponse>('/health');
  return response.data;
}

/**
 * 이미지 URL을 전체 URL로 변환
 */
export function getImageUrl(path: string | null | undefined): string {
  if (!path) return '/placeholder.png';
  
  // 이미 전체 URL인 경우
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  
  // 상대 경로인 경우 API 기본 URL과 합성
  return `${API_BASE_URL}${path}`;
}

/**
 * 날짜 포맷팅
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

/**
 * 상대 시간 표시
 */
export function getRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return '방금 전';
  if (diffMins < 60) return `${diffMins}분 전`;
  if (diffHours < 24) return `${diffHours}시간 전`;
  if (diffDays < 7) return `${diffDays}일 전`;
  
  return formatDate(dateString);
}

export default api;

