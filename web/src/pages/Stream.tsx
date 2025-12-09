import { useMemo, useState } from 'react'

const DEFAULT_STREAM = 'http://raspberrypi:8080/stream.mjpg'

export default function Stream() {
  // 환경변수로 스트림 URL 주입 (예: http://<PI_IP>:8080/stream.mjpg)
  const streamUrl = useMemo(() => import.meta.env.VITE_STREAM_URL || DEFAULT_STREAM, [])
  const [refreshKey, setRefreshKey] = useState(0)
  const [currentUrl, setCurrentUrl] = useState(streamUrl)

  const handleRefresh = () => {
    // 이미지 캐시 무효화를 위해 쿼리 파라미터를 변경
    setRefreshKey((k) => k + 1)
    setCurrentUrl(`${streamUrl}?t=${Date.now()}`)
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-3xl sm:text-4xl font-bold text-gradient mb-2">실시간 스트림</h1>
          <p className="text-dark-400 text-sm">
            라즈베리파이에서 송출하는 MJPEG 스트림을 표시합니다. <br />
            환경변수 VITE_STREAM_URL로 스트림 주소를 설정할 수 있습니다.
          </p>
        </div>
        <button
          onClick={handleRefresh}
          className="px-4 py-2 rounded-lg bg-dark-800 border border-dark-700 hover:border-primary-500/50 text-dark-200 hover:text-white transition-all"
        >
          새로고침
        </button>
      </div>

      <div className="glass rounded-2xl overflow-hidden border border-dark-800">
        <div className="bg-black aspect-video flex items-center justify-center">
          <img
            key={refreshKey}
            src={currentUrl}
            alt="Live Stream"
            className="w-full h-full object-contain bg-black"
            onError={(e) => {
              const target = e.target as HTMLImageElement
              target.alt = '스트림을 불러올 수 없습니다. 스트림 URL과 네트워크를 확인하세요.'
            }}
          />
        </div>
        <div className="p-4 text-sm text-dark-400 border-t border-dark-800">
          현재 스트림: <code className="text-dark-200">{streamUrl}</code>
        </div>
      </div>
    </div>
  )
}


