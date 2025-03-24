"use client"

import { useEffect, useState } from "react"

export default function FeatureFlagsPage() {
  const [flags, setFlags] = useState<Record<string, boolean>>({})

  useEffect(() => {
    fetch("/api/user/flags").then(res => res.json()).then(setFlags)
  }, [])

  const toggle = async (key: string) => {
    const next = { ...flags, [key]: !flags[key] }
    setFlags(next)
    await fetch("/api/user/flags", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(next)
    })
  }

  return (
    <div className="space-y-4 max-w-xl p-6">
      <h1 className="text-xl font-bold">Feature Flags</h1>
      <ul className="space-y-2 text-sm">
        {Object.entries(flags).map(([k, v]) => (
          <li key={k} className="flex justify-between items-center border rounded px-3 py-2">
            <span>{k}</span>
            <button onClick={() => toggle(k)} className={`px-2 py-1 rounded ${v ? 'bg-green-500' : 'bg-gray-300'}`}>
              {v ? "ON" : "OFF"}
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
