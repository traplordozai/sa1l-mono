import { ReactNode } from "react"
import { Sidebar } from "./Sidebar"
import { Topbar } from "./Topbar"

import { useEffect, useState } from "react"

function ImpersonationBanner() {
  const [user, setUser] = useState("")
  useEffect(() => {
    fetch("/api/admin/impersonated")
      .then(res => res.json())
      .then((d) => setUser(d?.name))
  }, [])

  if (!user) return null
  useEffect(() => startIdleTimer(15 * 60 * 1000), [])
  return (
    <div className="bg-yellow-100 text-yellow-900 p-2 text-sm text-center">
      Impersonating: {user} — <a href="/api/admin/impersonate/clear" className="underline">Revert</a>
    </div>
  )
}


function AssistantWidget() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<{ role: string, content: string }[]>([])
  const [input, setInput] = useState("")

  const submit = async () => {
    const next = [...messages, { role: "user", content: input }]
    setMessages(next)
    setInput("")
    const res = await fetch("/api/deepseek", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: next })
    })
    const json = await res.json()
    setMessages([...next, { role: "assistant", content: json.reply }])
  }

  if (!open) useEffect(() => startIdleTimer(15 * 60 * 1000), [])
  return (
    <button onClick={() => setOpen(true)} className="fixed bottom-4 right-4 z-50 p-3 rounded-full shadow bg-indigo-600 text-white">🤖</button>
  )

  useEffect(() => startIdleTimer(15 * 60 * 1000), [])
  return (
    <div className="fixed bottom-4 right-4 z-50 bg-white w-96 border shadow-xl rounded-lg p-4">
      <div className="flex justify-between items-center mb-2">
        <strong>AI Assistant</strong>
        <button onClick={() => setOpen(false)}>✖</button>
      </div>
      <div className="h-64 overflow-y-auto mb-2">
        {messages.map((m, i) => (
          <div key={i} className={`text-sm my-1 ${m.role === "user" ? "text-right text-blue-700" : "text-left text-gray-800"}`}>
            <span className="inline-block px-2 py-1 rounded bg-gray-100">{m.content}</span>
          </div>
        ))}
      </div>
      <input
        className="w-full border px-3 py-1 text-sm rounded"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && submit()}
        placeholder="Ask something..."
      />
    </div>
  )
}


import { startIdleTimer } from "@/lib/idleLogout"

export function Shell({ children }: { children: ReactNode }) {
  useEffect(() => startIdleTimer(15 * 60 * 1000), [])
  return (
    <div className="flex h-screen w-full bg-gray-50 text-gray-900">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <Topbar />
        <ImpersonationBanner />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
<AssistantWidget />
      </div>
    </div>
  )
}
