export function CalendarView({ events }: { events: { date: string, label: string, status: "confirmed" | "pending" | "overdue" }[] }) {
  const getColor = (status: string) => ({
    confirmed: "bg-green-400",
    pending: "bg-orange-400",
    overdue: "bg-red-500"
  }[status] || "bg-gray-300")

  return (
    <div className="grid grid-cols-7 gap-2 text-sm">
      {events.map((e, i) => (
        <div key={i} className="p-2 rounded shadow-sm text-white text-center font-medium truncate " + getColor(e.status)}>
          <div>{new Date(e.date).toLocaleDateString()}</div>
          <div className="text-xs">{e.label}</div>
        </div>
      ))}
    </div>
  )
}
