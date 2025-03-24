import useSWR from "swr"

export function useProfile() {
  return useSWR("/api/admin/me", (url) => fetch(url).then(res => res.json()))
}
