import React from 'react'
import './DonutChart.css'

const COLORS = [
  '#C4956A', '#8FA89A', '#D4A574', '#A67C55',
  '#B89A7A', '#6F8A7C', '#C47D6A', '#9C8B7A',
  '#7A9B8A', '#BFA88A', '#8A7A6A', '#D4BFA0',
]

export default function DonutChart({ data, title, size = 160 }) {
  if (!data || data.length === 0) return null

  const total = data.reduce((s, d) => s + d.value, 0)
  const cx = size / 2
  const cy = size / 2
  const radius = size * 0.35
  const circumference = 2 * Math.PI * radius

  let offset = 0
  const segments = data.map((d, i) => {
    const fraction = d.value / total
    const length = fraction * circumference
    const seg = {
      dasharray: `${length} ${circumference - length}`,
      dashoffset: -offset,
      color: d.color || COLORS[i % COLORS.length],
      label: d.label,
      value: d.value,
      fraction,
    }
    offset += length
    return seg
  })

  return (
    <div className="donut-chart">
      {title && <h4 className="chart-title">{title}</h4>}
      <div className="donut-body">
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          <circle cx={cx} cy={cy} r={radius} fill="none" stroke="var(--border-soft)" strokeWidth={size * 0.1} />
          {segments.map((seg, i) => (
            <circle
              key={i}
              cx={cx}
              cy={cy}
              r={radius}
              fill="none"
              stroke={seg.color}
              strokeWidth={size * 0.1}
              strokeDasharray={seg.dasharray}
              strokeDashoffset={seg.dashoffset}
              transform={`rotate(-90 ${cx} ${cy})`}
              style={{ transition: 'stroke-dashoffset 0.6s ease' }}
            />
          ))}
          <text x={cx} y={cy - 4} textAnchor="middle" fontSize="22" fontWeight="800" fill="var(--text)">
            {total}
          </text>
          <text x={cx} y={cy + 14} textAnchor="middle" fontSize="11" fill="var(--text-light)">
            total
          </text>
        </svg>
        <div className="donut-legend">
          {segments.map((seg, i) => (
            <div key={i} className="legend-item">
              <span className="legend-dot" style={{ background: seg.color }} />
              <span className="legend-label">{seg.label}</span>
              <span className="legend-value">{seg.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
