// Auto-generated SDK from OpenAPI spec
export async function deepseekChat(messages: { role: string; content: string }[]) {
  const res = await fetch("/api/v1/ai/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages })
  })
  const json = await res.json()
  return json.reply
}

export async function parseSemanticQuery(query: string) {
  const res = await fetch("/api/v1/search/parse", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query })
  })
  const json = await res.json()
  return json.filters
}
