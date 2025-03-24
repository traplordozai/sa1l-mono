let queue: (() => Promise<void>)[] = []
let online = typeof window !== "undefined" ? navigator.onLine : true

if (typeof window !== "undefined") {
  window.addEventListener("online", () => {
    online = true
    flushQueue()
  })
  window.addEventListener("offline", () => {
    online = false
  })
}

async function flushQueue() {
  while (queue.length) {
    const job = queue.shift()
    try {
      await job?.()
    } catch (e) {
      console.error("Failed queued job", e)
      queue.unshift(job!)
      break
    }
  }
}

export function useOfflineMutation<T>(fn: () => Promise<T>) {
  return async () => {
    if (online) {
      return await fn()
    } else {
      queue.push(fn)
      alert("You are offline. Action will sync when back online.")
    }
  }
}
