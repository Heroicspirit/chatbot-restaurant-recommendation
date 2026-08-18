import React, { useState, useRef, useEffect } from 'react'
import { IconMapPin, IconUtensils, IconList, IconStar, IconReset, IconSend, IconStop } from './icons'
import './InputBar.css'

const QUICK_CHIPS = [
  { label: 'Areas', value: 'areas', Icon: IconMapPin },
  { label: 'Cuisines', value: 'cuisines', Icon: IconUtensils },
  { label: 'All', value: 'show all', Icon: IconList },
  { label: 'Best', value: 'the best', Icon: IconStar },
  { label: 'Reset', value: 'reset', Icon: IconReset },
]

export default function InputBar({ onSend, onStop, submitting }) {
  const [text, setText] = useState('')
  const inputRef = useRef(null)

  useEffect(() => {
    if (!submitting) inputRef.current?.focus()
  }, [submitting])

  function autoResize(e) {
    const el = e.target
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 140) + 'px'
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey && !submitting) {
      e.preventDefault()
      handleSubmit()
    }
  }

  function handleSubmit() {
    if (!text.trim() || submitting) return
    onSend(text.trim())
    setText('')
    if (inputRef.current) inputRef.current.style.height = 'auto'
  }

  function handleFormSubmit(e) {
    e.preventDefault()
    handleSubmit()
  }

  return (
    <footer className="chat-footer">
      <div className="quick-chips">
        {QUICK_CHIPS.map(({ label, value, Icon }, i) => (
          <button
            key={i}
            className="quick-chip"
            onClick={() => onSend(value)}
            disabled={submitting}
            type="button"
          >
            <Icon size={12} /> {label}
          </button>
        ))}
      </div>
      <form className="input-bar" onSubmit={handleFormSubmit}>
        <textarea
          ref={inputRef}
          className="input-field"
          value={text}
          onChange={e => setText(e.target.value)}
          onInput={autoResize}
          onKeyDown={handleKeyDown}
          placeholder="Try: quiet cafe in Patan under Rs. 1000"
          disabled={submitting}
          rows={1}
        />
        {submitting ? (
          <button
            type="button"
            className="send-btn is-stop"
            onClick={onStop}
            aria-label="Stop generating"
          >
            <IconStop size={15} />
          </button>
        ) : (
          <button
            type="submit"
            className="send-btn"
            disabled={!text.trim()}
            aria-label="Send"
          >
            <IconSend size={15} />
          </button>
        )}
      </form>
    </footer>
  )
}