"use client"

import { useState, useEffect } from "react"
import { fetchDeepseekResponse } from "@/lib/deepseek"

type Message = { role: "user" | "assistant"; content: string }

export default function ToolsPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [tool, setTool] = useState("general")

  useEffect(() => {
    const saved = localStorage.getItem("deepseek_history")
    if (saved) setMessages(JSON.parse(saved))
  }, [])

  useEffect(() => {
    localStorage.setItem("deepseek_history", JSON.stringify(messages))
  }, [messages])

  const handleSubmit = async () => {
    if (!input.trim()) return
    const promptPrefix = tool === "code" ? "Write clean, working code for: " :
                        tool === "doc" ? "Summarize this documentation: " :
                        tool === "plan" ? "Create a step-by-step dev plan for: " :
                        ""
    const newMessages = [...messages, { role: "user", content: promptPrefix + input }]
    setMessages(newMessages)
    setLoading(true)
    setInput("")

    try {
      const reply = await fetchDeepseekResponse(newMessages)
      setMessages([...newMessages, { role: "assistant", content: reply }])
    } catch (err) {
      alert("Error: " + err.message)
    } finally {
      setLoading(false)
    }
  }

  const tools = [
    { key: "general", label: "💬 General Chat" },
    { key: "code", label: "💻 Code Generator" },
    { key: "doc", label: "📄 Doc Summarizer" },
    { key: "plan", label: "📋 Project Planner" }
  ]

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-semibold mb-4">DeepSeek Assistant</h1>

      <div className="flex gap-2 mb-4">
        {tools.map(t => (
          <button
            key={t.key}
            className={`px-3 py-1 rounded ${
              tool === t.key ? "bg-blue-600 text-white" : "bg-gray-200"
            }`}
            onClick={() => setTool(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="border rounded-lg p-4 h-[500px] overflow-y-auto bg-white shadow-sm">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`mb-3 whitespace-pre-wrap ${
              msg.role === "user" ? "text-right" : "text-left text-gray-700"
            }`}
          >
            <div
              className={`inline-block px-4 py-2 rounded-lg ${
                msg.role === "user"
                  ? "bg-blue-100 text-blue-900"
                  : "bg-gray-100 text-gray-800"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="italic text-gray-500 mt-4">Thinking...</div>
        )}
      </div>
      <div className="mt-4 flex gap-2">
        <input
          type="text"
          className="flex-1 border rounded px-3 py-2"
          placeholder="Type your question or prompt..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
        />
        <button
          onClick={handleSubmit}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
          disabled={loading}
        >
          Send
        </button>
      </div>
    </div>
  )
}
