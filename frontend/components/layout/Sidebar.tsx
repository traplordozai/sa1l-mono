import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
  HomeIcon,
  UsersIcon,
  LockClosedIcon,
  Cog6ToothIcon,
  ChartBarIcon,
  ClipboardDocumentListIcon,
  DocumentDuplicateIcon
} from "@heroicons/react/24/outline"

const navItems = [
  { href: "/admin", label: "Dashboard", icon: HomeIcon },
  { href: "/admin/users", label: "Users", icon: UsersIcon },
  { href: "/admin/roles", label: "Roles", icon: LockClosedIcon },
  { href: "/admin/content", label: "Content", icon: DocumentDuplicateIcon },
  { href: "/admin/analytics", label: "Analytics", icon: ChartBarIcon },
  { href: "/admin/logs", label: "Logs", icon: ClipboardDocumentListIcon },
  { href: "/admin/settings", label: "Settings", icon: Cog6ToothIcon }
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 bg-white border-r h-full hidden lg:block">
      <div className="px-4 py-6">
        <h2 className="text-xl font-bold tracking-tight mb-6">Admin Panel</h2>
        <nav className="space-y-2">
          {navItems.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-gray-100",
                pathname === href ? "bg-gray-200 text-gray-900 font-semibold" : "text-gray-600"
              )}
            >
              <Icon className="h-5 w-5" />
              {label}
            </Link>
          ))}
        </nav>
      </div>
    </aside>
  )
}
