# ==============================================
# Motion Canvas - Frontend Dockerfile (Build Stage)
# ==============================================
FROM node:20-alpine AS builder

WORKDIR /app

# 의존성 파일 복사
COPY package*.json ./

# 의존성 설치
RUN npm ci

# 소스 코드 복사
COPY . .

# 환경변수 (빌드 시 사용)
ARG VITE_API_URL=
ENV VITE_API_URL=$VITE_API_URL

# 빌드
RUN npm run build

# ==============================================
# Production Stage (Nginx)
# ==============================================
FROM nginx:alpine

# Nginx 설정 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 빌드된 정적 파일 복사
COPY --from=builder /app/dist /usr/share/nginx/html

# 포트 노출
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

