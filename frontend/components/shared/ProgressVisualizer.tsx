export function ProgressVisualizer({ label, percent }: { label: string, percent: number }) {
  const getColor = () => percent >= 100 ? "bg-green-500" : percent >= 50 ? "bg-yellow-400" : "bg-red-500"
  return (
    <div className="w-full">
      <div className="flex justify-between text-sm mb-1">
        <span>{label}</span>
        <span>{percent}%</span>
      </div>
      <div className="h-2 rounded bg-gray-200 overflow-hidden">
        <div className={`h-full ${getColor()}`} style={{ width: `${percent}%` }} />
      </div>
    </div>
  )
}
