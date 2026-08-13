import React from 'react'
import './MetricCard.css'

export default function MetricCard({ label, value, subtitle, color = '#14B8A6', icon, trend }) {
  const cardStyle = {
    borderTop: `3px solid ${color}`,
  }
  return (
    <div className="metric-card" style={cardStyle}>
      <div className="metric-top">
        {icon && <span className="metric-icon">{icon}</span>}
        <span className="metric-label">{label}</span>
      </div>
      <div className="metric-value">{value ?? '—'}</div>
      {subtitle && <div className="metric-subtitle">{subtitle}</div>}
      {trend != null && (
        <div className={`metric-trend ${trend >= 0 ? 'trend-up' : 'trend-down'}`}>
          {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%
        </div>
      )}
    </div>
  )
}
