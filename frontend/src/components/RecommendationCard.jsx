import React from 'react'
import { IconStar, IconCheck, IconInfo } from './icons'
import './RecommendationCard.css'

const PRICE_LABELS = {
  low: 'Budget-friendly',
  medium: 'Moderate',
  high: 'Premium',
}

function formatPrice(amount, level) {
  if (!amount && !level) return ''
  const parts = []
  if (amount) parts.push(`Rs. ${Number(amount).toLocaleString()}/person`)
  if (level) parts.push(PRICE_LABELS[level.toLowerCase()] || level)
  return parts.join(' · ')
}

export default function RecommendationCard({ rec, index }) {
  const matchType = rec.match_type || (rec.match_status === 'exact' ? 'exact' : 'closest')
  const isExact = matchType === 'exact'
  const animDelay = `${0.08 + (index || 0) * 0.08}s`

  return (
    <div
      className={`rec-card ${isExact ? 'match-exact' : 'match-closest'}`}
      style={{ animationDelay: animDelay }}
    >
      <div className="rec-header">
        <div className="rec-title-col">
          <h3 className="rec-name">{rec.name}</h3>
          <p className="rec-sub">{rec.area} · {rec.cuisine}</p>
        </div>
        <div className="rec-header-right">
          {rec.rating && (
            <span className="rec-rating"><IconStar size={11} /> {rec.rating}</span>
          )}
        </div>
      </div>
      <div className="rec-meta">
        {rec.avg_price_per_person != null && (
          <span className="price-badge">{formatPrice(rec.avg_price_per_person, rec.price_level)}</span>
        )}
        {rec.veg_available && (
          <span className="veg-badge"><IconCheck size={11} /> Veg options</span>
        )}
      </div>
      {rec.ambience_tags && (
        <div className="rec-tags">
          {rec.ambience_tags.split(',').map((tag, i) => (
            <span key={i} className="tag">{tag.trim()}</span>
          ))}
        </div>
      )}
      <div className="rec-reason">
        <span className={`match-badge ${isExact ? 'badge-exact' : 'badge-closest'}`}>
          {isExact ? (
            <><IconCheck size={11} /> Exact match</>
          ) : (
            <><IconInfo size={11} /> Closest alternative</>
          )}
        </span>
        <p className="reason-text"><strong>Why:</strong> {rec.reason || 'Best available match.'}</p>
      </div>
    </div>
  )
}