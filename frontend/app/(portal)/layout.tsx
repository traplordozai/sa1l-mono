import { ReactNode } from "react"
import { SidebarRouter } from "@/components/layout/SidebarRouter"
import { Topbar } from "@/components/layout/Topbar"
import "@/styles/tailwind.css"

export default function PortalLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-screen w-full bg-gray-50 text-gray-900">
      <SidebarRouter />
      <div className="flex flex-col flex-1">
        <Topbar />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  )
}
