"use client"

import { useSWRJson } from "@/lib/useSWRJson"

export default function ActivityPage() {
  const { data: activity = [] } = useSWRJson<any[]>("/api/admin/activity")

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Admin Activity</h1>
      <ul className="space-y-3 text-sm">
        {activity.map((entry) => (
          <li key={entry.id} className="border p-3 rounded bg-white shadow-sm">
            <div>{entry.message}</div>
            <div className="text-gray-500 text-xs">{new Date(entry.timestamp).toLocaleString()}</div>
          </li>
        ))}
      </ul>
    </div>
  )
}
