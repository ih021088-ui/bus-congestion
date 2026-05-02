import { useState } from "react"
import dynamic from "next/dynamic"
import useSWR from "swr"
import StopCard from "../components/StopCard"
import PredictionChart from "../components/PredictionChart"

const API = process.env.NEXT_PUBLIC_API_URL
const BusStopMap = dynamic(() => import("../components/BusStopMap"), { ssr: false })

const fetcher = (url: string) => fetch(url).then((r) => r.json())

const CITIES = ["서울", "경기", "인천"]

const CITY_CODE_MAP: Record<string, number> = {
  서울: 11, 부산: 21, 대구: 22, 인천: 12, 광주: 24,
  대전: 25, 울산: 26, 경기: 31, 강원: 32, 충북: 33,
  충남: 34, 전북: 35, 전남: 36, 경북: 37, 경남: 38, 제주: 39,
}

interface StopSearch { node_id: string; name: string; no: string }
interface SelectedStop { stop_id: string; city_code: number; region: string; stop_name: string; lat: number; lng: number }

// 기본값: 수원대학교 7790 (검증용)
const DEFAULT_STOP: SelectedStop = {
  stop_id: "GGB234000743",
  city_code: 31,
  region: "화성",
  stop_name: "수원대학교",
  lat: 37.2378,
  lng: 126.9301,
}

export default function Home() {
  const [city, setCity] = useState("경기")
  const [searchName, setSearchName] = useState("")
  const [selected, setSelected] = useState<SelectedStop>(DEFAULT_STOP)
  const [searching, setSearching] = useState(false)
  const [searchResults, setSearchResults] = useState<StopSearch[]>([])

  const currentUrl = `${API}/current?stop_id=${selected.stop_id}&city_code=${selected.city_code}&region=${selected.region}`
  const predictUrl = `${API}/predict?stop_id=${selected.stop_id}&city_code=${selected.city_code}&region=${selected.region}`

  const { data: current, error } = useSWR(currentUrl, fetcher, { refreshInterval: 60000 })
  const { data: prediction } = useSWR(predictUrl, fetcher, { refreshInterval: 60000 })

  async function handleSearch() {
    if (!searchName.trim()) return
    setSearching(true)
    try {
      const res = await fetch(`${API}/stops/search?name=${encodeURIComponent(searchName)}&city=${city}`)
      const data = await res.json()
      setSearchResults(data.results || [])
    } finally {
      setSearching(false)
    }
  }

  function selectStop(stop: StopSearch) {
    setSelected({
      stop_id: stop.node_id,
      city_code: CITY_CODE_MAP[city] ?? 11,
      region: city,
      stop_name: stop.name,
      lat: 37.5665,
      lng: 126.9780,
    })
    setSearchResults([])
    setSearchName("")
  }

  return (
    <main className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-2xl mx-auto space-y-4">
        <header className="text-center py-4">
          <h1 className="text-2xl font-bold text-gray-800">버스정류장 혼잡도 예측</h1>
          <p className="text-sm text-gray-500">정류장을 검색해서 혼잡도를 확인하세요</p>
        </header>

        <div className="bg-white rounded-2xl shadow-md p-4 space-y-3">
          <div className="flex gap-2">
            <select
              className="border rounded-lg px-3 py-2 text-sm text-gray-700"
              value={city}
              onChange={(e) => setCity(e.target.value)}
            >
              {CITIES.map((c) => <option key={c}>{c}</option>)}
            </select>
            <input
              className="flex-1 border rounded-lg px-3 py-2 text-sm"
              placeholder="정류장 이름 검색 (예: 수원대학교)"
              value={searchName}
              onChange={(e) => setSearchName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
            <button
              className="bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-600"
              onClick={handleSearch}
              disabled={searching}
            >
              {searching ? "..." : "검색"}
            </button>
          </div>

          {searchResults.length > 0 && (
            <ul className="border rounded-lg divide-y text-sm">
              {searchResults.map((s) => (
                <li
                  key={s.node_id}
                  className="px-3 py-2 hover:bg-gray-50 cursor-pointer flex justify-between"
                  onClick={() => selectStop(s)}
                >
                  <span className="font-medium text-gray-700">{s.name}</span>
                  <span className="text-gray-400">{s.no}</span>
                </li>
              ))}
            </ul>
          )}

          <p className="text-xs text-gray-400">
            현재 선택: <span className="font-medium text-gray-600">{selected.stop_name || selected.stop_id}</span>
          </p>
        </div>

        {error && (
          <div className="bg-red-100 text-red-600 rounded-xl p-4 text-sm">
            서버 연결 실패 - 백엔드를 먼저 실행해주세요
          </div>
        )}

        {current && <StopCard data={{ ...current, stop_name: selected.stop_name }} />}

        <BusStopMap lat={selected.lat} lng={selected.lng} stopName={selected.stop_name || selected.stop_id} />

        {prediction && (
          <PredictionChart current={prediction.current} forecast={prediction.forecast} />
        )}

        <p className="text-center text-xs text-gray-400 pb-4">매 1분마다 자동 갱신</p>
      </div>
    </main>
  )
}
