import React, { useEffect, useState } from 'react'
import { IconMoon, IconSun } from './icons'
import './ThemeToggle.css'

function getInitialTheme() {
  return document.documentElement.getAttribute('data-theme') || 'dark'
}

export default function ThemeToggle() {
  const [theme, setTheme] = useState(getInitialTheme)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('ataraxia_theme', theme)
    const meta = document.querySelector('meta[name="theme-color"]')
    if (meta) meta.setAttribute('content', theme === 'dark' ? '#12110e' : '#f7f4ee')
  }, [theme])

  const toggle = () => setTheme(t => (t === 'dark' ? 'light' : 'dark'))

  return (
    <button
      type="button"
      className="theme-toggle"
      onClick={toggle}
      aria-label={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
      title={theme === 'dark' ? 'Light theme' : 'Dark theme'}
    >
      <span className={`theme-icon ${theme === 'dark' ? 'is-active' : ''}`}>
        <IconMoon size={14} />
      </span>
      <span className={`theme-icon ${theme === 'light' ? 'is-active' : ''}`}>
        <IconSun size={14} />
      </span>
    </button>
  )
}