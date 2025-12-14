/**
 * 인증 API 모듈
 * 관리자 로그인 및 인증 토큰 관리를 담당합니다.
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// 토큰 저장 키
const TOKEN_KEY = 'admin_token';

// Axios 인스턴스
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터: 토큰 자동 추가
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터: 401 에러 시 토큰 제거
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeToken();
      // 로그인 페이지로 리다이렉트 (옵션)
      if (window.location.pathname.startsWith('/admin')) {
        window.location.href = '/admin/login';
      }
    }
    return Promise.reject(error);
  }
);

// 타입 정의
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface AdminInfo {
  username: string;
  is_admin: boolean;
}

export interface AdminStats {
  total_images: number;
  generated_images: number;
  pending_images: number;
}

// 토큰 관리
export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}

// API 함수들
export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>('/admin/login', credentials);
  setToken(response.data.access_token);
  return response.data;
}

export async function logout(): Promise<void> {
  removeToken();
}

export async function getCurrentAdmin(): Promise<AdminInfo> {
  const response = await api.get<AdminInfo>('/admin/me');
  return response.data;
}

export async function getAdminStats(): Promise<AdminStats> {
  const response = await api.get<AdminStats>('/admin/stats');
  return response.data;
}

export async function deleteImage(imageId: string): Promise<void> {
  await api.delete(`/admin/images/${imageId}`);
}

export default api;

