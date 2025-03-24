import useSWR from "swr"

export function useFeature(name: string): boolean {
  const { data } = useSWR("/api/user/flags", (url) =>
    fetch(url).then((res) => res.json())
  )
  return !!data?.[name]
}
