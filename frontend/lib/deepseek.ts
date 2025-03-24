export const OPENROUTER_API_KEY = process.env.NEXT_PUBLIC_OPENROUTER_API_KEY || ""
export const OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
export const DEEPSEEK_MODEL = "deepseek-coder"

export async function fetchDeepseekResponse(messages: { role: "user" | "assistant", content: string }[]) {
  const response = await fetch(OPENROUTER_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
      "HTTP-Referer": "https://yourdomain.com",
      "X-Title": "Admin Assistant"
    },
    body: JSON.stringify({
      model: DEEPSEEK_MODEL,
      messages,
      temperature: 0.5
    })
  })

  if (!response.ok) throw new Error("Failed to fetch Deepseek response")

  const data = await response.json()
  return data.choices?.[0]?.message?.content || ""
}
