import { useEffect, useState } from 'react'

export default function Sidebar({ active, onChange }) {
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark')

  const items = [
    { id: 'predict', icon: '', label: 'Predicción' },
    { id: 'eda', icon: '', label: 'Análisis exploratorio' },
    { id: 'models', icon: '', label: 'Resultados de modelos' },
    { id: 'contextual', icon: '', label: 'Análisis contextual' },
  ]

  return (
    <aside style={{
      width: 220,
      minHeight: '100vh',
      background: 'var(--bg-secondary)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      padding: '24px 12px',
      position: 'fixed',
      top: 0,
      left: 0,
    }}>
      {/* Logo */}
      <div style={{ padding: '0 12px 28px' }}>
        <div style={{
          fontSize: 14,
          fontWeight: 700,
          color: 'var(--text-primary)',
          letterSpacing: '-0.01em',
        }}>
          Fraud Detector
        </div>
        <div style={{
          fontSize: 11,
          color: 'var(--text-muted)',
          marginTop: 3,
          letterSpacing: '0.03em',
        }}>
          Detección de anomalías
        </div>
      </div>

      {/* Nav items */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 2, flex: 1 }}>
        {items.map(item => (
          <button
            key={item.id}
            onClick={() => onChange(item.id)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 9,
              padding: '9px 12px',
              borderRadius: '6px',
              background: active === item.id ? 'var(--accent-light)' : 'transparent',
              color: active === item.id ? 'var(--accent)' : 'var(--text-secondary)',
              fontWeight: active === item.id ? 600 : 400,
              fontSize: 13,
              transition: 'all 0.15s',
              textAlign: 'left',
              border: active === item.id
                ? '1px solid rgba(201,125,78,0.25)'
                : '1px solid transparent',
            }}
          >
            <span style={{ fontSize: 14 }}>{item.icon}</span>
            {item.label}
          </button>
        ))}
      </div>

      {/* Toggle tema */}
      <div style={{
        borderTop: '1px solid var(--border)',
        paddingTop: 16,
        marginTop: 8,
      }}>
        <button
          onClick={toggleTheme}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 9,
            padding: '9px 12px',
            borderRadius: '6px',
            background: 'transparent',
            color: 'var(--text-muted)',
            fontSize: 13,
            width: '100%',
            border: '1px solid transparent',
            transition: 'all 0.15s',
          }}
          onMouseEnter={e => {
            e.currentTarget.style.background = 'var(--bg-hover)'
            e.currentTarget.style.color = 'var(--text-secondary)'
          }}
          onMouseLeave={e => {
            e.currentTarget.style.background = 'transparent'
            e.currentTarget.style.color = 'var(--text-muted)'
          }}
        >
          <span style={{ fontSize: 15 }}>
            {theme === 'dark' ? '☀️' : '🌙'}
          </span>
          {theme === 'dark' ? 'Modo claro' : 'Modo oscuro'}
        </button>
      </div>
    </aside>
  )
}