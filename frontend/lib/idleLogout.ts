let timeout: NodeJS.Timeout

export function startIdleTimer(timeoutMs: number = 900000) {
  const resetTimer = () => {
    clearTimeout(timeout)
    timeout = setTimeout(() => {
      alert("Session expired due to inactivity")
      window.location.href = "/login"
    }, timeoutMs)
  }

  ["mousemove", "keydown", "click"].forEach(event => {
    window.addEventListener(event, resetTimer)
  })

  resetTimer()
}
