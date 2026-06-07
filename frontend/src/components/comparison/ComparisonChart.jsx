import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, ResponsiveContainer, Legend, Tooltip
} from 'recharts'

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

const COLORS = ['#6366f1', '#22c55e', '#f59e0b']

export default function ComparisonChart() {
  const metrics = ['f1', 'precision', 'recall', 'roc_auc', 'pr_auc']
  const labels = { f1: 'F1', precision: 'Precision', recall: 'Recall', roc_auc: 'AUC-ROC', pr_auc: 'PR-AUC' }

  const radarData = metrics.map(m => {
    const entry = { metric: labels[m] }
    HARDCODED.forEach(model => {
      entry[model.model] = parseFloat((model[m] * 100).toFixed(1))
    })
    return entry
  })

  return (
    <div className='card'>
      <div className='card-title'>Comparativa visual de métricas</div>
      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
        Valores escalados a 0–100 para comparación relativa
      </div>
      <ResponsiveContainer width='100%' height={320}>
        <RadarChart data={radarData}>
          <PolarGrid stroke='var(--border)' />
          <PolarAngleAxis
            dataKey='metric'
            tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: 'var(--text-muted)', fontSize: 10 }}
          />
          {HARDCODED.map((model, i) => (
            <Radar
              key={model.model}
              name={model.model}
              dataKey={model.model}
              stroke={COLORS[i]}
              fill={COLORS[i]}
              fillOpacity={0.15}
              strokeWidth={2}
            />
          ))}
          <Legend
            wrapperStyle={{ fontSize: 12, color: 'var(--text-secondary)' }}
          />
          <Tooltip
            formatter={(v) => `${v.toFixed(1)}%`}
            contentStyle={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              fontSize: 12,
            }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}