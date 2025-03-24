export async function parseQueryToFilter(input: string): Promise<any[]> {
  const res = await fetch("/api/search/parse", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: input })
  })
  const json = await res.json()
  return json.filters || []
}
