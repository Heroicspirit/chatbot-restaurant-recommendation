import React from 'react'
import './MetricCard.css'

export default function MetricCard({ label, value, subtitle, color = 'var(--chart-1)', icon, trend }) {
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
          <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            {trend >= 0
              ? <path d="M7 17L17 7" />
              : <path d="M7 7l10 10" />}
            {trend >= 0
              ? <path d="M7 7h10v10" />
              : <path d="M17 7v10H7" />}
          </svg>
          {Math.abs(trend)}%
        </div>
      )}
    </div>
  )
}