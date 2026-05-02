import { useEffect, useState } from "react"
import dynamic from "next/dynamic"
import useSWR from "swr"
import StopCard from "../components/StopCard"
import PredictionChart from "../components/PredictionChart"

const API = process.env.NEXT_PUBLIC_API_URL

// Leaflet은 SSR 불가 → 동적 import
const BusStopMap = dynamic(() => import("../components/BusStopMap"), { ssr: false })

const fetcher = (url: string) => fetch(url).then((r) => r.json())

export default function Home() {
  const { data: current, error } = useSWR(`${API}/current`, fetcher, { refreshInterval: 60000 })
  const { data: prediction } = useSWR(`${API}/predict`, fetcher, { refreshInterval: 60000 })

  return (
    <main className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-2xl mx-auto space-y-4">
        <header className="text-center py-4">
          <h1 className="text-2xl font-bold text-gray-800">수원대 7790 버스정류장</h1>
          <p className="text-sm text-gray-500">혼잡도 실시간 예측 서비스</p>
        </header>

        {error && (
          <div className="bg-red-100 text-red-600 rounded-xl p-4 text-sm">
            서버 연결 실패 - 백엔드를 먼저 실행해주세요
          </div>
        )}

        {current && <StopCard data={current} />}

        <BusStopMap />

        {prediction && (
          <PredictionChart current={prediction.current} forecast={prediction.forecast} />
        )}

        <p className="text-center text-xs text-gray-400 pb-4">
          매 1분마다 자동 갱신
        </p>
      </div>
    </main>
  )
}
