import { useEffect } from "react"

export function useFormDraft<T>(
  key: string,
  values: T,
  setValues: (v: T) => void,
  delay = 1000
) {
  useEffect(() => {
    const raw = localStorage.getItem(key)
    if (raw) {
      try {
        const parsed = JSON.parse(raw)
        setValues(parsed)
      } catch {}
    }
  }, [key])

  useEffect(() => {
    const timeout = setTimeout(() => {
      localStorage.setItem(key, JSON.stringify(values))
    }, delay)

    return () => clearTimeout(timeout)
  }, [key, values, delay])
}
