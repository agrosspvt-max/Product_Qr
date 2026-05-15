import clsx from 'clsx';

export default function DataTable({ columns, rows, empty = 'No records found.' }) {
  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-slate-600">
            <tr>
              {columns.map((col, i) => (
                <th key={i} className={clsx('px-4 py-3 text-left font-medium whitespace-nowrap', col.className)}>
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {rows.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-10 text-center text-slate-400">
                  {empty}
                </td>
              </tr>
            ) : (
              rows.map((row, ri) => (
                <tr key={ri} className="hover:bg-slate-50">
                  {columns.map((col, ci) => (
                    <td key={ci} className={clsx('px-4 py-3 align-middle', col.cellClassName)}>
                      {col.render ? col.render(row) : row[col.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
