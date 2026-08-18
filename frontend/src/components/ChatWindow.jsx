import React, { useState, useRef, useEffect, forwardRef, useImperativeHandle, useCallback } from 'react'
import Message from './Message'
import InputBar from './InputBar'
import { sendMessage, resetSession as resetApiSession } from '../services/api'
import { BrandMark, IconRetry } from './icons'
import './ChatWindow.css'

const WELCOME_SUGGESTIONS = [
  'Korean in Thamel',
  'Quiet cafe in Patan under Rs. 1000',
  'Vegetarian food near Boudha',
  'Cozy date spot in Jhamsikhel',
]

const ChatWindow = forwardRef(function ChatWindow({ onFiltersUpdate, onReset, datasetStats }, ref) {
  const [messages, setMessages] = useState([])
  const [status, setStatus] = useState('ready') // ready | submitting | error
  const [showWelcome, setShowWelcome] = useState(true)
  const bottomRef = useRef(null)
  const abortRef = useRef(null)
  const lastPromptRef = useRef('')

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, status])

  useImperativeHandle(ref, () => ({
    handleSend(text) {
      doSend(text)
    },
    handleReset() {
      doReset()
    },
  }))

  function doReset() {
    abortRef.current?.abort()
    resetApiSession()
    setMessages([])
    setShowWelcome(true)
    setStatus('ready')
    if (onReset) onReset()
  }

  async function requestReply(prompt) {
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller
    setStatus('submitting')
    try {
      const data = await sendMessage(prompt, 3, controller.signal)
      if (controller.signal.aborted) return
      setMessages(prev => [...prev, {
        role: 'bot',
        text: data.response,
        recommendations: data.recommendations,
        intent: data.intent,
        matchStatus: data.match_status,
        activeFilters: data.active_filters,
        resultCount: data.result_count,
      }])
      if (data.active_filters) {
        onFiltersUpdate(data.active_filters, null)
      }
      setStatus('ready')
    } catch (err) {
      if (err.name === 'AbortError') {
        setStatus('ready')
        return
      }
      setStatus('error')
    } finally {
      if (abortRef.current === controller) abortRef.current = null
    }
  }

  function doSend(text) {
    const trimmed = String(text || '').trim()
    if (!trimmed || status === 'submitting') return
    lastPromptRef.current = trimmed
    setShowWelcome(false)
    setMessages(prev => [...prev, { role: 'user', text: trimmed }])
    requestReply(trimmed)
  }

  function handleStop() {
    abortRef.current?.abort()
    setStatus('ready')
  }

  function handleRetry() {
    if (lastPromptRef.current) requestReply(lastPromptRef.current)
  }

  function handleRegenerate(index) {
    abortRef.current?.abort()
    setMessages(prev => prev.slice(0, index))
    if (lastPromptRef.current) requestReply(lastPromptRef.current)
  }

  return (
    <div className="chat-window">
      <div className="messages-area">
        {showWelcome && messages.length === 0 && (
          <div className="welcome-state">
            <div className="welcome-emblem"><BrandMark size={40} /></div>
            <h2>Find a restaurant in Kathmandu</h2>
            <p>Ask naturally by area, cuisine, budget, or vibe.</p>
            <p className="welcome-sub">Try one of these:</p>
            <div className="welcome-examples">
              {WELCOME_SUGGESTIONS.map((s, i) => (
                <button
                  key={i}
                  className="welcome-chip"
                  onClick={() => doSend(s)}
                  disabled={status === 'submitting'}
                >
                  {s}
                </button>
              ))}
            </div>
            <p className="welcome-note">Dataset: {datasetStats?.total || '28'} restaurants · {datasetStats?.areas || '12'} areas · {datasetStats?.cuisines || '13'} cuisines</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <Message
            key={i}
            message={msg}
            index={i}
            isLast={i === messages.length - 1}
            canRegenerate={status === 'ready'}
            onRegenerate={handleRegenerate}
          />
        ))}

        {status === 'submitting' && (
          <div className="message-row bot" id="typing-indicator">
            <div className="avatar bot-avatar"><BrandMark size={16} /></div>
            <div className="typing-bubble">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </div>
          </div>
        )}

        {status === 'error' && (
          <div className="error-banner" role="alert">
            <span className="error-title">Something went wrong</span>
            <span className="error-hint">The backend may be offline. Your question was not answered.</span>
            <button type="button" className="retry-btn" onClick={handleRetry}>
              <IconRetry size={12} /> Retry
            </button>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
      <InputBar onSend={doSend} onStop={handleStop} submitting={status === 'submitting'} />
    </div>
  )
})

export default ChatWindow