import { useState } from "react"

export function useUndo<T>(initial: T) {
  const [state, setState] = useState<T>(initial)
  const [history, setHistory] = useState<T[]>([])

  const update = (next: T) => {
    setHistory([...history, state])
    setState(next)
  }

  const undo = () => {
    const last = history[history.length - 1]
    if (last !== undefined) {
      setState(last)
      setHistory(history.slice(0, -1))
    }
  }

  return { state, set: update, undo, history }
}
