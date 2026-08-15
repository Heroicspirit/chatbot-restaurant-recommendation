import React from 'react'
import RecommendationCard from './RecommendationCard'
import './Message.css'

const DIETARY_LABELS = {
  vegetarian: 'Vegetarian',
  vegetarian_only: 'Veg only',
  non_vegetarian: 'Non-veg',
  non_vegetarian_only: 'Non-veg only',
}

export default function Message({ message }) {
  const isUser = message.role === 'user'

  function buildCompactFilters(filters) {
    const parts = []
    if (filters.location) parts.push(`Area = ${filters.location}`)
    if (filters.cuisine) parts.push(`Cuisine = ${Array.isArray(filters.cuisine) ? filters.cuisine.join(', ') : filters.cuisine}`)
    if (filters.budget_max) parts.push(`Budget ≤ Rs. ${filters.budget_max}`)
    if (filters.dietary) parts.push(`Dietary = ${DIETARY_LABELS[filters.dietary] || filters.dietary}`)
    if (filters.ambience) parts.push(`Vibe = ${Array.isArray(filters.ambience) ? filters.ambience.join(', ') : filters.ambience}`)
    if (filters.purpose) parts.push(`Purpose = ${filters.purpose}`)
    return parts.join(' · ')
  }

  const hasFilters = message.activeFilters && Object.values(message.activeFilters).some(v => v)
  const isNoMatch = message.text && message.text.includes('No exact match found')
  const showFilters = hasFilters && (message.recommendations?.length > 0 || isNoMatch)

  return (
    <div className={`message-row ${isUser ? 'user' : 'bot'}`}>
      <div className={`avatar ${isUser ? 'user-avatar' : 'bot-avatar'}`}>
        {isUser ? 'U' : 'A'}
      </div>
      <div className="bubble-col">
        <div className={`bubble ${isUser ? 'user-bubble' : 'bot-bubble'}`}>
          {showFilters && (
            <div className="compact-filters">
              Using filters: {buildCompactFilters(message.activeFilters)}
            </div>
          )}
          {message.text}
        </div>
        {message.recommendations && message.recommendations.length > 0 && (
          <div className="cards-container">
            {message.recommendations.map((rec, i) => (
              <RecommendationCard key={rec.restaurant_id || i} rec={rec} index={i} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
