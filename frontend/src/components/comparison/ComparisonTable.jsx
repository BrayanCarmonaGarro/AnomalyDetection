const METRICS = [
  { key: 'f1', label: 'F1', highlight: true },
  { key: 'precision', label: 'Precision' },
  { key: 'recall', label: 'Recall' },
  { key: 'roc_auc', label: 'AUC-ROC' },
  { key: 'pr_auc', label: 'PR-AUC' },
]

const MODEL_LABELS = {
  'Isolation Forest': 'Isolation Forest',
  'LOF (k=20)': 'LOF (k=20)',
  'Autoencoder': 'Autoencoder',
}

const HARDCODED = [
  {
    model: 'Isolation Forest',
    f1: 0.2446, precision: 0.2100, recall: 0.2943,
    roc_auc: 0.8996, pr_auc: 0.1258,
  },
  {
    model: 'LOF (k=20)',
    f1: 0.4538, precision: 0.6998, recall: 0.3358,
    roc_auc: 0.8354, pr_auc: 0.3915,
  },
  {
    model: 'Autoencoder',
    f1: 0.0832, precision: 0.0551, recall: 0.1699,
    roc_auc: 0.7662, pr_auc: 0.0291,
  },
]

export default function ComparisonTable() {
  const data = HARDCODED
  const best = {}
  METRICS.forEach(m => {
    best[m.key] = Math.max(...data.map(d => d[m.key]))
  })

  return (
    <div className='card'>
      <div className='card-title'>Comparativa final de modelos</div>
      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
        Umbral calibrado en validación, métricas reportadas en test
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontSize: 13,
        }}>
          <thead>
            <tr>
              <th style={{
                textAlign: 'left', padding: '10px 14px',
                color: 'var(--text-muted)', fontWeight: 500,
                borderBottom: '1px solid var(--border)',
              }}>
                Modelo
              </th>
              {METRICS.map(m => (
                <th key={m.key} style={{
                  textAlign: 'right', padding: '10px 14px',
                  color: m.highlight ? 'var(--accent)' : 'var(--text-muted)',
                  fontWeight: m.highlight ? 700 : 500,
                  borderBottom: '1px solid var(--border)',
                }}>
                  {m.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i} style={{
                background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)',
              }}>
                <td style={{
                  padding: '12px 14px',
                  fontWeight: 600,
                  borderBottom: '1px solid var(--border)',
                  color: row.model === 'LOF (k=20)' ? 'var(--accent)' : 'var(--text-primary)',
                }}>
                  {MODEL_LABELS[row.model]}
                  {row.model === 'LOF (k=20)' && (
                    <span style={{
                      marginLeft: 8, fontSize: 10, padding: '2px 8px',
                      background: 'var(--accent-light)', color: 'var(--accent)',
                      borderRadius: 999, fontWeight: 600,
                    }}>
                      mejor
                    </span>
                  )}
                </td>
                {METRICS.map(m => {
                  const val = row[m.key]
                  const isBest = val === best[m.key]
                  return (
                    <td key={m.key} style={{
                      textAlign: 'right', padding: '12px 14px',
                      borderBottom: '1px solid var(--border)',
                      color: isBest
                        ? (m.highlight ? 'var(--accent)' : 'var(--success)')
                        : 'var(--text-primary)',
                      fontWeight: isBest ? 700 : 400,
                    }}>
                      {val.toFixed(4)}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}