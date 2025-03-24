"use client"
import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function RootRedirect() {
  const router = useRouter()

  useEffect(() => {
    fetch("/api/admin/me")
      .then(res => res.json())
      .then(data => {
        const role = data.role || "student"
        router.replace(`/${role}/dashboard`)
      })
  }, [])

  return <div className="p-6 text-gray-500">Redirecting...</div>
}
