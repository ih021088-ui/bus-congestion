import { BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ResponsiveContainer } from "recharts"

interface ForecastItem {
  minutes_ahead: number
  forecast_ts: string
  label: string
  proba: Record<string, number>
}

const LABEL_COLOR: Record<string, string> = {
  혼잡: "#ef4444",
  보통: "#f59e0b",
  여유: "#22c55e",
}

export default function PredictionChart({ current, forecast }: { current: any; forecast: ForecastItem[] }) {
  const data = [
    { name: "지금", label: current.label, ...current.proba },
    ...forecast.map((f) => ({ name: `+${f.minutes_ahead}분\n${f.forecast_ts}`, label: f.label, ...f.proba })),
  ]

  return (
    <div className="bg-white rounded-2xl shadow-md p-6 w-full">
      <h3 className="font-bold text-gray-700 mb-4">혼잡도 예측</h3>
      <div className="flex gap-4 mb-3 text-sm">
        {data.map((d) => (
          <div key={d.name} className="flex items-center gap-1">
            <span className="font-medium text-gray-500">{d.name}</span>
            <span
              className="px-2 py-0.5 rounded-full text-white text-xs font-bold"
              style={{ backgroundColor: LABEL_COLOR[d.label] ?? "#9ca3af" }}
            >
              {d.label}
            </span>
          </div>
        ))}
      </div>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={data} barCategoryGap="30%">
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 1]} tickFormatter={(v) => `${Math.round(v * 100)}%`} tick={{ fontSize: 11 }} />
          <Tooltip formatter={(v: number) => `${Math.round(v * 100)}%`} />
          <Bar dataKey="혼잡" stackId="a" fill="#ef4444" radius={[0, 0, 0, 0]} />
          <Bar dataKey="보통" stackId="a" fill="#f59e0b" />
          <Bar dataKey="여유" stackId="a" fill="#22c55e" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
