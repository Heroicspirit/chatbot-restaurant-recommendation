import React from 'react'
import './TableView.css'

export default function TableView({ columns, data, title, maxRows = 10 }) {
  if (!data || data.length === 0) return null

  const rows = data.slice(0, maxRows)

  return (
    <div className="table-view">
      {title && <h4 className="chart-title">{title}</h4>}
      <div className="table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              {columns.map((col, i) => (
                <th key={i} style={col.width ? { width: col.width } : undefined}>
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, ri) => (
              <tr key={ri}>
                {columns.map((col, ci) => (
                  <td key={ci}>
                    {col.render ? col.render(row[col.key], row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
