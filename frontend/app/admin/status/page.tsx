"use client"

import { useSWRJson } from "@/lib/useSWRJson"

export default function StatusPage() {
  const { data = {} } = useSWRJson<any>("/api/admin/status")

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">System Status</h1>
      <ul className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(data).map(([key, value]) => (
          <li key={key} className="bg-white border p-4 rounded shadow text-sm">
            <strong className="block mb-1">{key}</strong>
            <span className={value === "OK" ? "text-green-600" : "text-red-600"}>
              {String(value)}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
