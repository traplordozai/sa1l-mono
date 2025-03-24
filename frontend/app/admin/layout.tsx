import { ReactNode } from "react"
import { Shell } from "@/components/layout/Shell"
import "@/styles/tailwind.css"

export default function AdminLayout({ children }: { children: ReactNode }) {
  return <Shell>{children}</Shell>
}
