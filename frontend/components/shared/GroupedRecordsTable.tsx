export function GroupedRecordsTable({ groups }: { groups: { group: string, records: any[] }[] }) {
  return (
    <div className="space-y-4 text-sm">
      {groups.map((g, i) => (
        <details key={i} className="border rounded">
          <summary className="bg-gray-100 px-4 py-2 font-semibold cursor-pointer">{g.group}</summary>
          <ul className="divide-y px-4">
            {g.records.map((r, j) => (
              <li key={j} className="py-2">{JSON.stringify(r)}</li>
            ))}
          </ul>
        </details>
      ))}
    </div>
  )
}
