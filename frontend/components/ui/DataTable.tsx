import { ReactNode } from "react"

export function DataTable({
  headers,
  data,
  actions
}: {
  headers: string[]
  data: any[]
  actions?: (row: any) => ReactNode
}) {
  return (
    <div className="overflow-x-auto border rounded">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {headers.map((h, i) => (
              <th key={i} className="px-4 py-2 text-left text-sm font-semibold text-gray-700">
                {h}
              </th>
            ))}
            {actions && <th className="px-4 py-2"></th>}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-100">
          {data.map((row, i) => (
            <tr key={i}>
              {headers.map((h) => (
                <td key={h} className="px-4 py-2 text-sm text-gray-800">{row[h]}</td>
              ))}
              {actions && <td className="px-4 py-2">{actions(row)}</td>}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
