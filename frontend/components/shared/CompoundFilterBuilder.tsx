export function CompoundFilterBuilder({ filters, onChange }: {
  filters: any[],
  onChange: (filters: any[]) => void
}) {
  const ops = ["=", "!=", "contains", "in", "gt", "lt"]

  const update = (i: number, key: string, value: string) => {
    const next = [...filters]
    next[i] = { ...next[i], [key]: value }
    onChange(next)
  }

  const add = () => onChange([...filters, { field: "", op: "=", value: "" }])
  const remove = (i: number) => onChange(filters.filter((_, j) => j !== i))

  return (
    <div className="space-y-2 text-sm">
      {filters.map((f, i) => (
        <div key={i} className="flex items-center gap-2">
          <input placeholder="field" value={f.field} onChange={e => update(i, "field", e.target.value)} className="border px-2 py-1 rounded w-32" />
          <select value={f.op} onChange={e => update(i, "op", e.target.value)} className="border px-2 py-1 rounded">
            {ops.map(o => <option key={o} value={o}>{o}</option>)}
          </select>
          <input placeholder="value" value={f.value} onChange={e => update(i, "value", e.target.value)} className="border px-2 py-1 rounded w-40" />
          <button onClick={() => remove(i)} className="text-red-600 text-xs">Remove</button>
        </div>
      ))}
      <button onClick={add} className="text-blue-600 text-xs">Add Filter</button>
    </div>
  )
}
