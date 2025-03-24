import { useState } from "react"

export function useBulkSelect<T>(rows: T[]) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())

  const toggle = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const isSelected = (id: string) => selectedIds.has(id)

  const selectAll = () =>
    setSelectedIds(new Set(rows.map((r: any) => r.id)))

  const clearAll = () => setSelectedIds(new Set())

  return {
    selectedIds,
    toggle,
    isSelected,
    selectAll,
    clearAll
  }
}
