import React from 'react'
import './BarChart.css'

const BAR_COLORS = ['var(--chart-1)', 'var(--chart-2)', 'var(--chart-3)', 'var(--chart-4)', 'var(--chart-5)']

export default function BarChart({ data, title, horizontal = false, maxBars = 12 }) {
  if (!data || data.length === 0) return null

  const items = data.slice(0, maxBars)
  const maxValue = Math.max(...items.map(d => d.value), 1)

  return (
    <div className={`bar-chart ${horizontal ? 'bar-horizontal' : ''}`}>
      {title && <h4 className="chart-title">{title}</h4>}
      <div className="bar-chart-body">
        {items.map((item, i) => {
          const pct = (item.value / maxValue) * 100
          const color = item.color || BAR_COLORS[i % BAR_COLORS.length]
          return (
            <div key={i} className="bar-item" title={`${item.label}: ${item.value}`}>
              <span className="bar-label">{item.label}</span>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{
                    [horizontal ? 'width' : 'height']: `${pct}%`,
                    backgroundColor: color,
                  }}
                />
              </div>
              <span className="bar-value">{item.value}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}