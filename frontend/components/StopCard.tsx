import CongestionBadge from "./CongestionBadge"

interface StopData {
  stop_id: string
  stop_name?: string
  label: string
  ts: string
  buses_arriving_20min: number | null
  avg_interval_min: number | null
  temp: number | null
  is_raining: boolean
  pm10: number | null
  region?: string
}

export default function StopCard({ data }: { data: StopData }) {
  return (
    <div className="bg-white rounded-2xl shadow-md p-6 w-full max-w-md">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-800">
            {data.stop_name || data.stop_id}
          </h2>
          <p className="text-sm text-gray-400">
            {data.region && `${data.region} · `}노드ID {data.stop_id}
          </p>
        </div>
        <CongestionBadge label={data.label} />
      </div>

      <div className="grid grid-cols-2 gap-3 text-sm text-gray-600">
        <InfoItem label="20분 내 도착 버스" value={data.buses_arriving_20min != null ? `${data.buses_arriving_20min}대` : "-"} />
        <InfoItem label="평균 배차 간격" value={data.avg_interval_min != null ? `${data.avg_interval_min}분` : "-"} />
        <InfoItem label="현재 기온" value={data.temp != null ? `${data.temp}°C` : "-"} />
        <InfoItem label="날씨" value={data.is_raining ? "비 내림 🌧" : "맑음 ☀️"} />
        <InfoItem label="미세먼지(PM10)" value={data.pm10 != null ? `${data.pm10} μg/m³` : "-"} />
      </div>

      <p className="text-xs text-gray-300 mt-4 text-right">
        {new Date(data.ts).toLocaleTimeString("ko-KR")} 기준
      </p>
    </div>
  )
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-50 rounded-lg p-2">
      <p className="text-xs text-gray-400">{label}</p>
      <p className="font-semibold text-gray-700">{value}</p>
    </div>
  )
}
