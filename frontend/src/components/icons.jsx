import React from 'react'

export function BrandMark({ size = 24, className = '' }) {
  return (
    <svg viewBox="0 0 24 24" width={size} height={size} className={className} aria-hidden="true">
      <path d="M5 2.5 L13.5 2.5 L5.5 21.5 L5 21.5 Q2.5 21.5 2.5 19 L2.5 5 Q2.5 2.5 5 2.5 Z" />
      <path d="M16.5 2.5 L19 2.5 Q21.5 2.5 21.5 5 L21.5 19 Q21.5 21.5 19 21.5 L8.5 21.5 Z" />
    </svg>
  )
}

function Base({ children, size = 18, className = '' }) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      {children}
    </svg>
  )
}

export const IconChat = (p) => (
  <Base {...p}><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></Base>
)

export const IconAnalytics = (p) => (
  <Base {...p}><path d="M3 3v18h18" /><path d="M7 15l4-4 3 3 5-6" /></Base>
)

export const IconSearch = (p) => (
  <Base {...p}><circle cx="11" cy="11" r="7" /><path d="M21 21l-4.35-4.35" /></Base>
)

export const IconSend = (p) => (
  <Base {...p}><path d="M22 2L11 13" /><path d="M22 2l-7 20-4-9-9-4z" /></Base>
)

export const IconMapPin = (p) => (
  <Base {...p}><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" /><circle cx="12" cy="10" r="3" /></Base>
)

export const IconUtensils = (p) => (
  <Base {...p}><path d="M3 2v7a2 2 0 0 0 4 0V2" /><path d="M5 2v20" /><path d="M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3zm0 0v7" /></Base>
)

export const IconList = (p) => (
  <Base {...p}><path d="M8 6h13" /><path d="M8 12h13" /><path d="M8 18h13" /><path d="M3 6h.01" /><path d="M3 12h.01" /><path d="M3 18h.01" /></Base>
)

export const IconStar = (p) => (
  <Base {...p}><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z" /></Base>
)

export const IconReset = (p) => (
  <Base {...p}><path d="M3 12a9 9 0 1 0 3-6.7" /><path d="M3 4v5h5" /></Base>
)

export const IconSun = (p) => (
  <Base {...p}><circle cx="12" cy="12" r="4" /><path d="M12 2v2" /><path d="M12 20v2" /><path d="M4.93 4.93l1.41 1.41" /><path d="M17.66 17.66l1.41 1.41" /><path d="M2 12h2" /><path d="M20 12h2" /><path d="M6.34 17.66l-1.41 1.41" /><path d="M19.07 4.93l-1.41 1.41" /></Base>
)

export const IconMoon = (p) => (
  <Base {...p}><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" /></Base>
)

export const IconCheck = (p) => (
  <Base {...p}><path d="M20 6L9 17l-5-5" /></Base>
)

export const IconClock = (p) => (
  <Base {...p}><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 3" /></Base>
)

export const IconInfo = (p) => (
  <Base {...p}><circle cx="12" cy="12" r="9" /><path d="M12 16v-4" /><path d="M12 8h.01" /></Base>
)

export const IconRetry = (p) => (
  <Base {...p}><path d="M3 12a9 9 0 1 0 3-6.7" /><path d="M3 4v5h5" /><path d="M12 9l3-3-3-3" /></Base>
)

export const IconStop = (p) => (
  <Base {...p}><rect x="7" y="7" width="10" height="10" rx="1.5" /></Base>
)

export const IconSparkle = (p) => (
  <Base {...p}><path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z" /><path d="M19 15l1 2.5L22.5 18 20 19l-1 2.5L18 19l-2.5-1L18 17.5z" /></Base>
)

export const IconShield = (p) => (
  <Base {...p}><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /><path d="M9 12l2 2 4-4" /></Base>
)

export const IconUser = (p) => (
  <Base {...p}><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></Base>
)

export const IconTag = (p) => (
  <Base {...p}><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.83z" /><path d="M7 7h.01" /></Base>
)