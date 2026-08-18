import React, { useState, useCallback, useEffect } from 'react'
import ChatWindow from './components/ChatWindow'
import Dashboard from './components/Dashboard'
import ThemeToggle from './components/ThemeToggle'
import {
  BrandMark, IconChat, IconAnalytics, IconMapPin, IconUtensils,
  IconList, IconReset, IconSearch, IconShield,
} from './components/icons'
import { getRestaurants } from './services/api'
import './App.css'

const LABELS = {
  location: 'Area',
  cuisine: 'Cuisine',
  budget_max: 'Budget ≤ Rs.',
  purpose: 'Purpose',
  dietary: 'Dietary',
  ambience: 'Vibe',
}

const SAVED_SEARCHES = [
  { label: 'Korean in Thamel', query: 'Korean in Thamel' },
  { label: 'Quiet cafe in Patan', query: 'Quiet cafe in Patan under Rs. 1000' },
  { label: 'Vegetarian in Baneshwor', query: 'Vegetarian food in Baneshwor' },
  { label: 'Date spot in Jhamsikhel', query: 'Cozy place for a date in Jhamsikhel' },
  { label: 'Budget Nepali near Boudha', query: 'Cheap Nepali food near Boudha' },
  { label: 'Best rated Italian', query: 'Best Italian restaurant in Kathmandu' },
]

const FILTER_TINTS = {
  location: 'tint-patina',
  cuisine: 'tint-gold',
  budget_max: 'tint-vermilion',
  purpose: 'tint-gold',
  dietary: 'tint-patina',
  ambience: 'tint-neutral',
}

export default function App() {
  const [view, setView] = useState('chat')
  const [activeFilters, setActiveFilters] = useState(null)
  const [datasetStats, setDatasetStats] = useState(null)
  const chatRef = React.useRef(null)

  useEffect(() => {
    getRestaurants().then(data => {
      const restaurants = Array.isArray(data) ? data : (data.restaurants || [])
      const areas = [...new Set(restaurants.map(r => r.area).filter(Boolean))]
      const cuisines = [...new Set(
        restaurants.flatMap(r => r.cuisine?.split(',').map(c => c.trim()) || [])
      )]
      setDatasetStats({
        total: restaurants.length,
        areas: areas.length,
        cuisines: cuisines.length,
      })
    }).catch(() => {})
  }, [])

  const handleFiltersUpdate = useCallback((filters, stats) => {
    setActiveFilters(filters)
    if (stats) setDatasetStats(stats)
  }, [])

  function sendQuick(text) {
    setView('chat')
    setTimeout(() => {
      if (chatRef.current) {
        chatRef.current.handleSend(text)
      }
    }, 50)
  }

  function handleReset() {
    setActiveFilters(null)
    if (chatRef.current) {
      chatRef.current.handleReset()
    }
  }

  const filterEntries = activeFilters
    ? Object.entries(activeFilters).filter(([, v]) => v && (Array.isArray(v) ? v.length > 0 : true))
    : []

  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="header-left">
          <span className="header-emblem"><BrandMark size={24} /></span>
          <div className="header-title-group">
            <h1>Ataraxia</h1>
            <span className="header-subtitle">Restaurant discovery · Kathmandu</span>
          </div>
        </div>
        <nav className="header-nav" aria-label="Primary">
          <button
            type="button"
            className={`nav-tab ${view === 'chat' ? 'active' : ''}`}
            onClick={() => setView('chat')}
          >
            <IconChat size={14} /><span>Chat</span>
          </button>
          <button
            type="button"
            className={`nav-tab ${view === 'dashboard' ? 'active' : ''}`}
            onClick={() => setView('dashboard')}
          >
            <IconAnalytics size={14} /><span>Analytics</span>
          </button>
        </nav>
        <div className="header-right">
          <div className="header-badges">
            <span className="header-badge">Dataset-grounded</span>
            <span className="header-badge">LLM-Assisted</span>
            <span className="header-badge is-muted">No personal data</span>
          </div>
          <ThemeToggle />
        </div>
      </header>

      <div className="app-body">
        <aside className="sidebar">
          <section className="panel-card">
            <h3 className="panel-label">Quick actions</h3>
            <button className="action-btn" onClick={() => sendQuick('areas')}>
              <IconMapPin size={14} /><span>Show areas</span>
            </button>
            <button className="action-btn" onClick={() => sendQuick('cuisines')}>
              <IconUtensils size={14} /><span>Show cuisines</span>
            </button>
            <button className="action-btn" onClick={() => sendQuick('show all')}>
              <IconList size={14} /><span>Show all</span>
            </button>
            <button className="action-btn is-danger" onClick={handleReset}>
              <IconReset size={14} /><span>Clear filters</span>
            </button>
          </section>

          {view === 'chat' && (
            <>
              <section className="panel-card">
                <h3 className="panel-label">Saved searches</h3>
                {SAVED_SEARCHES.map((s, i) => (
                  <button
                    key={i}
                    type="button"
                    className="saved-search-chip"
                    onClick={() => sendQuick(s.query)}
                    title={s.query}
                  >
                    <IconSearch size={12} />
                    <span>{s.label}</span>
                  </button>
                ))}
              </section>

              <section className="panel-card" id="filter-panel">
                <h3 className="panel-label">Current filters</h3>
                <div className="filter-list">
                  {filterEntries.length > 0 ? (
                    filterEntries.map(([key, value]) => (
                      <span
                        key={key}
                        className={`filter-tag ${FILTER_TINTS[key] || 'tint-neutral'}`}
                      >
                        <span className="filter-dot" />
                        <span className="filter-k">{LABELS[key] || key}:</span>
                        <span className="filter-v">{Array.isArray(value) ? value.join(', ') : String(value)}</span>
                      </span>
                    ))
                  ) : (
                    <span className="filter-empty">No filters set yet</span>
                  )}
                </div>
              </section>
            </>
          )}

          <section className="panel-card">
            <h3 className="panel-label">Dataset</h3>
            <div className="dataset-stat">
              <span className="stat-num">{datasetStats?.total || '—'}</span>
              <span className="stat-label">restaurants</span>
            </div>
            <div className="dataset-stat">
              <span className="stat-num">{datasetStats?.areas || '—'}</span>
              <span className="stat-label">areas covered</span>
            </div>
            <div className="dataset-stat">
              <span className="stat-num">{datasetStats?.cuisines || '—'}</span>
              <span className="stat-label">cuisine types</span>
            </div>
            <p className="dataset-note">Public data only. No personal data collected.</p>
          </section>

          <section className="panel-card">
            <h3 className="panel-label">System</h3>
            <div className="dataset-stat stat-line">
              <IconShield size={13} className="stat-check" />
              <span className="stat-label">Hallucination guard: Active</span>
            </div>
            <div className="dataset-stat stat-line">
              <IconShield size={13} className="stat-check" />
              <span className="stat-label">Grounded response check: Enabled</span>
            </div>
          </section>
        </aside>

        <main className="main-panel">
          {view === 'chat' ? (
            <ChatWindow
              ref={chatRef}
              onFiltersUpdate={handleFiltersUpdate}
              onReset={handleReset}
              datasetStats={datasetStats}
            />
          ) : (
            <Dashboard />
          )}
        </main>
      </div>
    </div>
  )
}