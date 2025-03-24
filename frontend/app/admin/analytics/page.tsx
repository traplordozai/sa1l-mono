"use client"

import { useEffect, useState } from "react"

type Stat = {
  label: string
  value: string
}

export default function AnalyticsPage() {
  const [stats, setStats] = useState<Stat[]>([])

  useEffect(() => {
    fetch("/api/admin/stats")
      .then(res => res.json())
      .then(setStats)
  }, [])

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Analytics</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {stats.map((s, i) => (
          <div
            key={i}
            className="bg-white border rounded-lg p-4 shadow text-center"
          >
            <div className="text-sm text-gray-500">{s.label}</div>
            <div className="text-xl font-semibold">{s.value}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
