type Label = "혼잡" | "보통" | "여유" | "알 수 없음"

const COLOR: Record<string, string> = {
  혼잡: "bg-red-500",
  보통: "bg-amber-400",
  여유: "bg-green-500",
  "알 수 없음": "bg-gray-400",
}

const EMOJI: Record<string, string> = {
  혼잡: "🔴",
  보통: "🟡",
  여유: "🟢",
  "알 수 없음": "⚪",
}

export default function CongestionBadge({ label }: { label: string }) {
  return (
    <span className={`inline-flex items-center gap-1 px-4 py-2 rounded-full text-white font-bold text-lg ${COLOR[label] ?? "bg-gray-400"}`}>
      {EMOJI[label] ?? "⚪"} {label}
    </span>
  )
}
