/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 커스텀 컬러 팔레트
        primary: {
          50: '#f0f5ff',
          100: '#e0ebff',
          200: '#c7d7fe',
          300: '#a4bcfc',
          400: '#7b97f8',
          500: '#5a71f2',
          600: '#4451e6',
          700: '#3840d3',
          800: '#3036ab',
          900: '#2c3386',
          950: '#1c1f52',
        },
        dark: {
          50: '#f7f7f8',
          100: '#efeef0',
          200: '#dcdadf',
          300: '#bdbac3',
          400: '#9894a2',
          500: '#7b7687',
          600: '#645f6e',
          700: '#524e5b',
          800: '#46434d',
          900: '#1a1a1f',
          950: '#0d0d10',
        }
      },
      fontFamily: {
        sans: ['Pretendard', 'system-ui', 'sans-serif'],
        display: ['Playfair Display', 'serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'pulse-slow': 'pulse 3s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}

