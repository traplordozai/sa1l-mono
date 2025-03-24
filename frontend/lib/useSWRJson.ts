import useSWR from "swr"

export function useSWRJson<T>(url: string) {
  const fetcher = (url: string): Promise<T> =>
    fetch(url).then(res => res.json())

  return useSWR<T>(url, fetcher, {
    refreshInterval: 30000 // 30s polling
  })
}
