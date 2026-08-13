import React, { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react'
import Message from './Message'
import InputBar from './InputBar'
import { sendMessage, resetSession as resetApiSession } from '../services/api'
import './ChatWindow.css'

const WELCOME_SUGGESTIONS = [
  'Korean in Thamel',
  'Quiet cafe in Patan under Rs. 1000',
  'Vegetarian food near Boudha',
  'Cozy date spot in Jhamsikhel',
]

const ChatWindow = forwardRef(function ChatWindow({ onFiltersUpdate, onReset, datasetStats }, ref) {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [showWelcome, setShowWelcome] = useState(true)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useImperativeHandle(ref, () => ({
    handleSend(text) {
      doSend(text)
    },
    handleReset() {
      doReset()
    },
  }))

  function doReset() {
    resetApiSession()
    setMessages([])
    setShowWelcome(true)
    if (onReset) onReset()
  }

  async function doSend(text) {
    setShowWelcome(false)
    setMessages(prev => [...prev, { role: 'user', text }])
    setLoading(true)

    try {
      const data = await sendMessage(text)
      const botMsg = {
        role: 'bot',
        text: data.response,
        recommendations: data.recommendations,
        intent: data.intent,
        matchStatus: data.match_status,
        activeFilters: data.active_filters,
        resultCount: data.result_count,
      }
      setMessages(prev => [...prev, botMsg])

      if (data.active_filters) {
        onFiltersUpdate(data.active_filters, null)
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'bot',
        text: 'Sorry, something went wrong. Please check that the backend server is running.',
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-window">
      <div className="messages-area">
        {showWelcome && messages.length === 0 && (
          <div className="welcome-state">
            <div className="welcome-icon">⛲</div>
            <h2>Find a restaurant in Kathmandu</h2>
            <p>Ask naturally by area, cuisine, budget, or vibe.</p>
            <p className="welcome-sub">Try one of these:</p>
            <div className="welcome-examples">
              {WELCOME_SUGGESTIONS.map((s, i) => (
                <button
                  key={i}
                  className="welcome-chip"
                  onClick={() => doSend(s)}
                  disabled={loading}
                >
                  {s}
                </button>
              ))}
            </div>
            <p className="welcome-note">Dataset: {datasetStats?.total || '28'} restaurants · {datasetStats?.areas || '12'} areas · {datasetStats?.cuisines || '13'} cuisines</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <Message key={i} message={msg} />
        ))}
        {loading && (
          <div className="message-row bot" id="typing-indicator">
            <div className="message-avatar bot-avatar">A</div>
            <div className="typing-bubble">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <InputBar onSend={doSend} disabled={loading} />
    </div>
  )
})

export default ChatWindow