const AlertIcon = ({ color }) => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
    stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
    <line x1="12" y1="9" x2="12" y2="13" />
    <line x1="12" y1="17" x2="12.01" y2="17" />
  </svg>
)

const CheckIcon = ({ color }) => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
    stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
    <polyline points="22 4 12 14.01 9 11.01" />
  </svg>
)

const InfoIcon = ({ color, size = 15 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
    style={{ flexShrink: 0, marginTop: 1 }}>
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="8" x2="12" y2="12" />
    <line x1="12" y1="16" x2="12.01" y2="16" />
  </svg>
)

const WarningSmall = ({ color }) => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
    stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
    style={{ flexShrink: 0 }}>
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
    <line x1="12" y1="9" x2="12" y2="13" />
    <line x1="12" y1="17" x2="12.01" y2="17" />
  </svg>
)

const ScoreCard = ({ title, subtitle, result, color }) => {
  if (!result) return null
  const pct = Math.round(result.score * 100)

  return (
    <div className='card' style={{ borderTop: `2px solid ${color}` }}>
      <div style={{ marginBottom: 12 }}>
        <div style={{ fontWeight: 600, fontSize: 13, color: 'var(--text-primary)' }}>{title}</div>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 3 }}>{subtitle}</div>
      </div>

      <div style={{ marginBottom: 14 }}>
        <span className={`badge ${result.is_anomaly ? 'badge-anomaly' : 'badge-normal'}`}
          style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          {result.is_anomaly
            ? <AlertIcon color='var(--danger)' />
            : <CheckIcon color='var(--success)' />
          }
          {result.is_anomaly ? 'Anómala' : 'Normal'}
        </span>
      </div>

      <div style={{ marginBottom: 6, fontSize: 12, display: 'flex', justifyContent: 'space-between' }}>
        <span style={{ color: 'var(--text-secondary)' }}>Score de anomalía</span>
        <span style={{ fontWeight: 700, color: result.is_anomaly ? 'var(--danger)' : 'var(--success)' }}>
          {pct}%
        </span>
      </div>
      <div style={{ height: 6, background: 'var(--bg-secondary)', borderRadius: 999, overflow: 'hidden', marginBottom: 14 }}>
        <div style={{
          height: '100%',
          width: `${pct}%`,
          background: result.is_anomaly ? 'var(--danger)' : 'var(--success)',
          borderRadius: 999,
          transition: 'width 0.5s ease',
        }} />
      </div>

      {result.top_deviations && (
        <div>
          <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Variables más desviadas
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
            {result.top_deviations.map((d, i) => (
              <div key={i} style={{
                display: 'flex', justifyContent: 'space-between',
                fontSize: 12, padding: '5px 10px',
                background: 'var(--bg-secondary)',
                borderRadius: '6px',
              }}>
                <span style={{ color: 'var(--text-secondary)' }}>
                  {d.feature.replace(/cat_/, '').replace(/_/g, ' ')}
                </span>
                <span style={{
                  color: d.z_score > 2 ? 'var(--danger)' : d.z_score > 1 ? 'var(--warning)' : 'var(--text-muted)',
                  fontWeight: 600,
                }}>
                  z = {d.z_score}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.n_neighbors_used && (
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 12 }}>
          {result.n_references} referencias · {result.n_neighbors_used} vecinos
        </div>
      )}

      {result.note && (
        <div style={{ fontSize: 11, color: 'var(--warning)', marginTop: 8, display: 'flex', alignItems: 'center', gap: 5 }}>
          <WarningSmall color='var(--warning)' />
          {result.note}
        </div>
      )}
    </div>
  )
}

const MODEL_LABELS = {
  lof: 'Local Outlier Factor',
  isolation_forest: 'Isolation Forest',
  autoencoder: 'Autoencoder',
}

export default function ContextualResult({ result }) {
  if (!result) return null

  const anyAnomaly = result.global.is_anomaly || result.statistical.is_anomaly || result.lof_local.is_anomaly

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

      {/* Header */}
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: '10px',
        padding: '16px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <div>
          <div style={{ fontWeight: 700, fontSize: 15 }}>Análisis contextual completado</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
            {result.n_references} transacciones de referencia · Modelo: {MODEL_LABELS[result.global.model] || result.global.model}
          </div>
        </div>
        <div style={{
          width: 40, height: 40, borderRadius: '10px',
          background: anyAnomaly ? 'var(--danger-light)' : 'var(--success-light)',
          border: `1px solid ${anyAnomaly ? 'rgba(184,92,74,0.25)' : 'rgba(122,158,126,0.25)'}`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          {anyAnomaly
            ? <AlertIcon color='var(--danger)' />
            : <CheckIcon color='var(--success)' />
          }
        </div>
      </div>

      {/* Tarjetas */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16 }}>
        <ScoreCard
          title='Análisis global'
          subtitle={`vs ${(1470000).toLocaleString('es-CR')} transacciones del dataset`}
          result={result.global}
          color='var(--accent)'
        />
        <ScoreCard
          title='Análisis estadístico'
          subtitle='Desviación Z-score vs perfil de referencia'
          result={result.statistical}
          color='var(--warning)'
        />
        <ScoreCard
          title='LOF local'
          subtitle='LOF entrenado solo con las referencias'
          result={result.lof_local}
          color='var(--success)'
        />
      </div>

      {/* Consenso */}
      <div className='card'>
        <div className='card-title'>Consenso de los tres análisis</div>
        <div style={{ display: 'flex', gap: 10 }}>
          {[
            { label: 'Global', val: result.global.is_anomaly, color: 'var(--accent)' },
            { label: 'Estadístico', val: result.statistical.is_anomaly, color: 'var(--warning)' },
            { label: 'LOF local', val: result.lof_local.is_anomaly, color: 'var(--success)' },
          ].map(({ label, val, color }) => (
            <div key={label} style={{
              flex: 1, textAlign: 'center', padding: '14px 12px',
              background: 'var(--bg-secondary)',
              borderRadius: '6px',
              borderTop: `2px solid ${color}`,
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6,
            }}>
              <div style={{
                width: 32, height: 32, borderRadius: '8px',
                background: val ? 'var(--danger-light)' : 'var(--success-light)',
                border: `1px solid ${val ? 'rgba(184,92,74,0.2)' : 'rgba(122,158,126,0.2)'}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                {val ? <AlertIcon color='var(--danger)' /> : <CheckIcon color='var(--success)' />}
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{label}</div>
              <div style={{ fontSize: 11, fontWeight: 600, color: val ? 'var(--danger)' : 'var(--success)' }}>
                {val ? 'Anómala' : 'Normal'}
              </div>
            </div>
          ))}
        </div>

        {/* Veredicto */}
        {(() => {
          const votes = [result.global.is_anomaly, result.statistical.is_anomaly, result.lof_local.is_anomaly]
          const anomalyCount = votes.filter(Boolean).length
          let msg, color
          if (anomalyCount === 3) { msg = 'Los tres análisis coinciden: transacción muy sospechosa.'; color = 'var(--danger)' }
          else if (anomalyCount === 2) { msg = 'Dos de tres análisis detectan anomalía. Se recomienda revisión.'; color = 'var(--warning)' }
          else if (anomalyCount === 1) { msg = 'Solo un análisis detecta anomalía. Riesgo bajo.'; color = 'var(--text-secondary)' }
          else { msg = 'Los tres análisis coinciden: transacción normal.'; color = 'var(--success)' }
          return (
            <div style={{
              marginTop: 14, padding: '11px 14px',
              background: 'var(--bg-secondary)',
              borderRadius: '6px',
              borderLeft: `2px solid ${color}`,
              fontSize: 13, color,
              display: 'flex', alignItems: 'flex-start', gap: 8,
            }}>
              <InfoIcon color={color} />
              {msg}
            </div>
          )
        })()}
      </div>
    </div>
  )
}