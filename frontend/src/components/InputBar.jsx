import React, { useState, useRef, useEffect } from 'react'
import './InputBar.css'

const QUICK_CHIPS = [
  { label: '📍 Areas', value: 'areas' },
  { label: '🍽 Cuisines', value: 'cuisines' },
  { label: '📋 All', value: 'show all' },
  { label: '★ Best', value: 'the best' },
  { label: '✕ Reset', value: 'reset' },
]

export default function InputBar({ onSend, disabled }) {
  const [text, setText] = useState('')
  const inputRef = useRef(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  useEffect(() => {
    if (!disabled) {
      inputRef.current?.focus()
    }
  }, [disabled])

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  function handleSubmit() {
    if (!text.trim() || disabled) return
    onSend(text.trim())
    setText('')
  }

  function handleFormSubmit(e) {
    e.preventDefault()
    handleSubmit()
  }

  function handleQuickClick(value) {
    onSend(value)
  }

  return (
    <footer className="chat-footer">
      <div className="quick-chips">
        {QUICK_CHIPS.map((chip, i) => (
          <button
            key={i}
            className="quick-chip"
            onClick={() => handleQuickClick(chip.value)}
            disabled={disabled}
            type="button"
          >
            {chip.label}
          </button>
        ))}
      </div>
      <form className="input-bar" onSubmit={handleFormSubmit}>
        <textarea
          ref={inputRef}
          className="input-field"
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Try: quiet cafe in Patan under Rs. 1000"
          disabled={disabled}
          rows={1}
        />
        <button
          type="submit"
          className="send-btn"
          disabled={!text.trim() || disabled}
        >
          {disabled ? '...' : 'Send'}
        </button>
      </form>
    </footer>
  )
}