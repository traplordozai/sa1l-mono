export function Table({ headers = [], rows = [] }) {
  return (
    <table className="w-full text-left border-separate border-spacing-y-2">
      <thead className="text-gray-700">
        <tr>{headers.map((h, i) => <th key={i} className="py-2 px-4 border-b border-gray-200">{h}</th>)}</tr>
      </thead>
      <tbody>
        {rows.map((row, i) => (
          <tr key={i} className="bg-white hover:bg-gray-50">
            {row.map((cell, j) => <td key={j} className="py-2 px-4">{cell}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  );
}