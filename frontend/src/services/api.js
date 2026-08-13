const API_BASE = import.meta.env.VITE_API_BASE || '/api'

function generateSessionId() {
  return 'session_' + Math.random().toString(36).substring(2, 10)
}

let currentSessionId = localStorage.getItem('ataraxia_session') || generateSessionId()
localStorage.setItem('ataraxia_session', currentSessionId)

export async function sendMessage(message, topK = 3) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: currentSessionId,
      message,
      top_k: topK,
    }),
  })
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }
  return response.json()
}

export async function getRestaurants() {
  const response = await fetch(`${API_BASE}/restaurants`)
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }
  return response.json()
}

export async function getDatasetStats() {
  const response = await fetch(`${API_BASE}/dataset/stats`)
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }
  return response.json()
}

export function resetSession() {
  currentSessionId = generateSessionId()
  localStorage.setItem('ataraxia_session', currentSessionId)
}
