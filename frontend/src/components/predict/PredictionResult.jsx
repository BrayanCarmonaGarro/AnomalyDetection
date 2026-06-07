export default function PredictionResult({ result }) {
  if (!result) return null

  const isAnomaly = result.is_anomaly
  const score = result.score
  const pct = Math.round(score * 100)

  const modelLabels = {
    lof: 'Local Outlier Factor',
    isolation_forest: 'Isolation Forest',
    autoencoder: 'Autoencoder',
  }

  return (
    <div className='card' style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div className='card-title'>Resultado</div>

      {/* Badge principal */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <div style={{
          width: 44,
          height: 44,
          borderRadius: '10px',
          background: isAnomaly ? 'var(--danger-light)' : 'var(--success-light)',
          border: `1px solid ${isAnomaly ? 'rgba(184,92,74,0.25)' : 'rgba(122,158,126,0.25)'}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
            stroke={isAnomaly ? 'var(--danger)' : 'var(--success)'}
            strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            {isAnomaly ? (
              <>
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                <line x1="12" y1="9" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </>
            ) : (
              <>
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
              </>
            )}
          </svg>
        </div>

        <div>
          <span className={`badge ${isAnomaly ? 'badge-anomaly' : 'badge-normal'}`}
            style={{ fontSize: 13, padding: '5px 14px' }}>
            {isAnomaly ? 'Transacción anómala' : 'Transacción normal'}
          </span>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 6 }}>
            Modelo: {modelLabels[result.model] || result.model}
          </div>
        </div>
      </div>

      {/* Score */}
      <div>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginBottom: 8,
          fontSize: 13,
        }}>
          <span style={{ color: 'var(--text-secondary)' }}>Score de anomalía</span>
          <span style={{
            fontWeight: 700,
            color: isAnomaly ? 'var(--danger)' : 'var(--success)',
          }}>
            {pct}%
          </span>
        </div>
        <div style={{
          height: 6,
          background: 'var(--bg-secondary)',
          borderRadius: 999,
          overflow: 'hidden',
        }}>
          <div style={{
            height: '100%',
            width: `${pct}%`,
            background: isAnomaly ? 'var(--danger)' : 'var(--success)',
            borderRadius: 999,
            transition: 'width 0.5s ease',
          }} />
        </div>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginTop: 4,
          fontSize: 11,
          color: 'var(--text-muted)',
        }}>
          <span>Normal (0)</span>
          <span>Anómalo (1)</span>
        </div>
      </div>

      {/* Interpretación */}
      <div style={{
        background: 'var(--bg-secondary)',
        borderRadius: '6px',
        padding: '12px 16px',
        fontSize: 13,
        color: 'var(--text-secondary)',
        borderLeft: `2px solid ${isAnomaly ? 'var(--danger)' : 'var(--success)'}`,
        display: 'flex',
        gap: 10,
        alignItems: 'flex-start',
      }}>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
          stroke={isAnomaly ? 'var(--danger)' : 'var(--success)'}
          strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
          style={{ flexShrink: 0, marginTop: 1 }}>
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        {isAnomaly
          ? `El modelo detectó que esta transacción se desvía significativamente del comportamiento normal. Score: ${score.toFixed(4)}.`
          : `El modelo considera que esta transacción es consistente con el comportamiento normal. Score: ${score.toFixed(4)}.`
        }
      </div>
    </div>
  )
}