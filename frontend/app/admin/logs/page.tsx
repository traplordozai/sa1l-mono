"use client"

import { useSWRJson } from "@/lib/useSWRJson"

type LogEntry = {
  id: string
  type: string
  message: string
  createdAt: string
}

export default function LogsPage() {
  const { data: logs = [] } = useSWRJson<LogEntry[]>("/api/admin/logs")

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">System Logs</h1>
      <div className="border rounded-lg overflow-auto">
        <table className="min-w-full table-auto text-sm text-left">
          <thead className="bg-gray-100 text-xs text-gray-700">
            <tr>
              <th className="px-4 py-2">Type</th>
              <th className="px-4 py-2">Message</th>
              <th className="px-4 py-2">Date</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {logs.map((log) => (
              <tr key={log.id}>
                <td className="px-4 py-2 text-gray-700">{log.type}</td>
                <td className="px-4 py-2 text-gray-900">{log.message}</td>
                <td className="px-4 py-2 text-gray-500">{new Date(log.createdAt).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
