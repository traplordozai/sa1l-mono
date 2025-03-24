"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

const entries = [
  { label: "Go to Student Dashboard", action: () => location.href = "/student/dashboard" },
  { label: "Go to Org Dashboard", action: () => location.href = "/org/dashboard" },
  { label: "View All Deliverables", action: () => location.href = "/admin/deliverables" }
]

export function CommandK() {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState("")
  const router = useRouter()

  useEffect(() => {
    const listener = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        setOpen((v) => !v)
      }
    }
    window.addEventListener("keydown", listener)
    return () => window.removeEventListener("keydown", listener)
  }, [])

  const filtered = entries.filter((e) =>
    e.label.toLowerCase().includes(query.toLowerCase())
  )

  if (!open) return null

  return (
    <div className="fixed inset-0 bg-black/30 z-50 flex items-start justify-center pt-40">
      <div className="bg-white rounded shadow-lg w-full max-w-md p-4">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          autoFocus
          className="w-full border px-3 py-2 rounded text-sm"
          placeholder="Type a command..."
        />
        <ul className="mt-3 space-y-1 text-sm">
          {filtered.map((e, i) => (
            <li key={i} onClick={e.action} className="cursor-pointer hover:bg-gray-100 px-3 py-2 rounded">
              {e.label}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
