import React, { useState, useCallback, useEffect } from 'react'
import ChatWindow from './components/ChatWindow'
import Dashboard from './components/Dashboard'
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

const FILTER_COLORS = {
  location: '#8FA89A',
  cuisine: '#C4956A',
  budget_max: '#D4A574',
  purpose: '#A67C55',
  dietary: '#6F8A7C',
  ambience: '#B89A7A',
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
          <span className="header-emblem">⛲</span>
          <div className="header-title-group">
            <h1>Ataraxia</h1>
            <span className="header-subtitle">Restaurant discovery · Kathmandu</span>
          </div>
        </div>
        <nav className="header-nav">
          <button
            className={`nav-tab ${view === 'chat' ? 'active' : ''}`}
            onClick={() => setView('chat')}
          >
            💬 Chat
          </button>
          <button
            className={`nav-tab ${view === 'dashboard' ? 'active' : ''}`}
            onClick={() => setView('dashboard')}
          >
            📊 Analytics
          </button>
        </nav>
        <div className="header-badges">
          <span className="header-badge">Dataset-grounded</span>
          <span className="header-badge">LLM-Assisted</span>
          <span className="header-badge">No personal data</span>
        </div>
      </header>

      <div className="app-body">
        <aside className="sidebar">
          <section className="panel-card">
            <h3 className="panel-label">Quick actions</h3>
            <button className="action-btn" onClick={() => sendQuick('areas')}>📍 Show areas</button>
            <button className="action-btn" onClick={() => sendQuick('cuisines')}>🍽 Show cuisines</button>
            <button className="action-btn" onClick={() => sendQuick('show all')}>📋 Show all</button>
            <button className="action-btn" onClick={handleReset}>✕ Clear filters</button>
          </section>

          {view === 'chat' && (
            <>
              <section className="panel-card">
                <h3 className="panel-label">Saved searches</h3>
                {SAVED_SEARCHES.map((s, i) => (
                  <button
                    key={i}
                    className="saved-search-chip"
                    onClick={() => sendQuick(s.query)}
                    title={s.query}
                  >
                    <span className="saved-search-icon">🔍</span>
                    {s.label}
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
                        className="filter-tag"
                        style={{
                          borderColor: `${FILTER_COLORS[key] || '#14B8A6'}44`,
                          background: `${FILTER_COLORS[key] || '#14B8A6'}15`,
                        }}
                      >
                        <span
                          className="filter-dot"
                          style={{ background: FILTER_COLORS[key] || '#14B8A6' }}
                        />
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
            <div className="dataset-stat">
              <span className="stat-num">✓</span>
              <span className="stat-label">Hallucination guard: Active</span>
            </div>
            <div className="dataset-stat">
              <span className="stat-num">✓</span>
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
