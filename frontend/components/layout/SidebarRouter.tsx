"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import { usePathname } from "next/navigation"

const sidebars = {
  org: [
    { href: "/org/dashboard", label: "Dashboard" },
    { href: "/org/matches", label: "Matched Students" },
    { href: "/org/interviews", label: "Schedule Interviews" },
    { href: "/org/deliverables", label: "Deliverables" },
    { href: "/org/profile", label: "Org Profile" }
  ],
  student: [
    { href: "/student/dashboard", label: "Dashboard" },
    { href: "/student/status", label: "Status Tracker" },
    { href: "/student/documents", label: "My Documents" },
    { href: "/student/deliverables", label: "Deliverables" },
    { href: "/student/profile", label: "My Profile" }
  ],
  faculty: [
    { href: "/faculty/dashboard", label: "Dashboard" },
    { href: "/faculty/students", label: "Students" },
    { href: "/faculty/reviews", label: "Reviews" },
    { href: "/faculty/projects", label: "Projects" },
    { href: "/faculty/supervision", label: "Supervision" }
  ]
}

export function SidebarRouter() {
  const pathname = usePathname()
  const [role, setRole] = useState("")

  useEffect(() => {
    fetch("/api/admin/me")
      .then(res => res.json())
      .then(data => setRole(data.role || ""))
  }, [])

  const links = sidebars[role] || []

  return (
    <aside className="w-64 bg-white border-r h-full hidden lg:block">
      <div className="px-4 py-6">
        <h2 className="text-xl font-bold tracking-tight mb-6 capitalize">{role} Portal</h2>
        <nav className="space-y-2">
          {links.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className={`block rounded-md px-3 py-2 text-sm font-medium ${
                pathname?.startsWith(href)
                  ? "bg-gray-200 text-gray-900 font-semibold"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
            >
              {label}
            </Link>
          ))}
        </nav>
      </div>
    </aside>
  )
}
