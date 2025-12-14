import { useEffect, useMemo, useState } from 'react'

// 기본 스트림 URL: EC2 서버의 스트림 중계 엔드포인트
const DEFAULT_STREAM = '/stream/live.mjpg'

interface StreamStatus {
  source_connected: boolean
  source_id: string | null
  client_count: number
  frame_age_seconds: number | null
  has_frame: boolean
}

export default function Stream() {
  // 환경변수로 스트림 URL 주입 (기본: EC2 서버 중계)
  const streamUrl = useMemo(() => import.meta.env.VITE_STREAM_URL || DEFAULT_STREAM, [])
  const [refreshKey, setRefreshKey] = useState(0)
  const [currentUrl, setCurrentUrl] = useState(streamUrl)
  const [status, setStatus] = useState<StreamStatus | null>(null)
  const [statusError, setStatusError] = useState<string | null>(null)

  // 스트림 상태 주기적 확인
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('/stream/status')
        if (response.ok) {
          const data = await response.json()
          setStatus(data)
          setStatusError(null)
        } else {
          setStatusError('상태 확인 실패')
        }
      } catch {
        setStatusError('서버 연결 실패')
      }
    }

    fetchStatus()
    const interval = setInterval(fetchStatus, 3000)
    return () => clearInterval(interval)
  }, [])

  const handleRefresh = () => {
    // 이미지 캐시 무효화를 위해 쿼리 파라미터를 변경
    setRefreshKey((k) => k + 1)
    setCurrentUrl(`${streamUrl}?t=${Date.now()}`)
  }

  const isConnected = status?.source_connected ?? false

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-3xl sm:text-4xl font-bold text-gradient mb-2">실시간 스트림</h1>
          <p className="text-dark-400 text-sm">
            라즈베리파이에서 EC2를 통해 중계되는 실시간 스트림입니다.
          </p>
        </div>
        <button
          onClick={handleRefresh}
          className="px-4 py-2 rounded-lg bg-dark-800 border border-dark-700 hover:border-primary-500/50 text-dark-200 hover:text-white transition-all"
        >
          새로고침
        </button>
      </div>

      {/* 연결 상태 표시 */}
      <div className="glass rounded-xl p-4 border border-dark-800">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            <span className="text-sm text-dark-200">
              {statusError ? statusError : isConnected ? '라즈베리파이 연결됨' : '라즈베리파이 연결 대기 중...'}
            </span>
          </div>
          {status && (
            <>
              <div className="text-sm text-dark-400">
                시청자: <span className="text-dark-200">{status.client_count}명</span>
              </div>
              {status.frame_age_seconds !== null && (
                <div className="text-sm text-dark-400">
                  프레임: <span className="text-dark-200">{status.frame_age_seconds.toFixed(1)}초 전</span>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* 스트림 영역 */}
      <div className="glass rounded-2xl overflow-hidden border border-dark-800">
        <div className="bg-black aspect-video flex items-center justify-center relative">
          {isConnected ? (
            <img
              key={refreshKey}
              src={currentUrl}
              alt="Live Stream"
              className="w-full h-full object-contain bg-black"
              onError={(e) => {
                const target = e.target as HTMLImageElement
                target.style.display = 'none'
              }}
            />
          ) : (
            <div className="text-center text-dark-400 p-8">
              <div className="text-6xl mb-4">📷</div>
              <p className="text-lg mb-2">라즈베리파이 연결 대기 중</p>
              <p className="text-sm">
                라즈베리파이에서 <code className="text-primary-400">STREAM_PUSH_ENABLED=true</code>로 설정하고<br />
                프로그램을 실행해주세요.
              </p>
            </div>
          )}
        </div>
        <div className="p-4 text-sm text-dark-400 border-t border-dark-800 flex justify-between items-center">
          <div>
            스트림 URL: <code className="text-dark-200">{streamUrl}</code>
          </div>
          <a
            href="/stream/snapshot.jpg"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary-400 hover:text-primary-300 transition-colors"
          >
            스냅샷 보기 →
          </a>
        </div>
      </div>

      {/* 설정 안내 */}
      <div className="glass rounded-xl p-4 border border-dark-800">
        <h3 className="text-lg font-semibold text-dark-100 mb-3">📋 라즈베리파이 설정</h3>
        <div className="text-sm text-dark-300 space-y-2">
          <p><code className="bg-dark-800 px-2 py-1 rounded">raspberry/.env</code> 파일에서:</p>
          <pre className="bg-dark-900 p-3 rounded-lg overflow-x-auto text-xs">
{`# EC2로 스트림 푸시 활성화
STREAM_PUSH_ENABLED=true
STREAM_PUSH_URL=ws://[EC2-IP]:8000/stream/push
STREAM_PUSH_SECRET=raspberry-pi-secret`}
          </pre>
        </div>
      </div>
    </div>
  )
}
