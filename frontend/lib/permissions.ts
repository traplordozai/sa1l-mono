import { useEffect, useState } from "react"

export function useHasPermission(permission: string): boolean {
  const [allowed, setAllowed] = useState(false)

  useEffect(() => {
    fetch("/api/admin/me")
      .then(res => res.json())
      .then(data => {
        const perms = data?.permissions || []
        setAllowed(perms.includes(permission))
      })
  }, [permission])

  return allowed
}
