import { useState, useEffect } from "react"

export function useWalkthrough(id: string, steps: string[]) {
  const [current, setCurrent] = useState(0)

  useEffect(() => {
    const saved = localStorage.getItem("walkthrough:" + id)
    if (saved) setCurrent(parseInt(saved))
  }, [id])

  const advance = () => {
    const next = current + 1
    setCurrent(next)
    localStorage.setItem("walkthrough:" + id, String(next))
  }

  const reset = () => {
    setCurrent(0)
    localStorage.removeItem("walkthrough:" + id)
  }

  return {
    step: steps[current],
    stepIndex: current,
    done: current >= steps.length,
    advance,
    reset
  }
}
