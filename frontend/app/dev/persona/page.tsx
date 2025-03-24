"use client"

import { useRouter } from "next/navigation"

const personas = ["admin", "student", "org", "faculty"]

export default function PersonaSim() {
  const router = useRouter()

  const simulate = async (role: string) => {
    await fetch("/api/dev/persona", {
      method: "POST",
      body: JSON.stringify({ role }),
      headers: { "Content-Type": "application/json" }
    })
    router.push(`/${role}/dashboard`)
  }

  return (
    <div className="space-y-4 p-6">
      <h1 className="text-2xl font-bold">Simulate Persona</h1>
      <ul className="flex gap-4">
        {personas.map((p) => (
          <button
            key={p}
            onClick={() => simulate(p)}
            className="bg-indigo-600 text-white px-4 py-2 rounded"
          >
            {p}
          </button>
        ))}
      </ul>
    </div>
  )
}
