import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, ReferenceLine
} from 'recharts'

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div style={{
      background: 'var(--bg-card)', border: '1px solid var(--border)',
      borderRadius: 8, padding: '10px 14px', fontSize: 12,
    }}>
      <div style={{ fontWeight: 600, marginBottom: 6 }}>{d.label}</div>
      <div style={{ color: 'var(--text-secondary)' }}>{d.description}</div>
      <div style={{ fontWeight: 700, marginTop: 4, color: d.fill }}>
        ${d.value.toFixed(2)}
      </div>
    </div>
  )
}

export default function AmountBoxplot({ data }) {
  if (!data) return <div className='card' style={{ color: 'var(--text-muted)' }}>Cargando...</div>

  const normalColor = '#6b8f71'
  const fraudColor = '#b85c4a'

  const normalData = [
    { label: 'Normal — Mínimo', description: 'Valor mínimo', value: data.normal.min, fill: normalColor },
    { label: 'Normal — Q1', description: '25% de transacciones por debajo', value: data.normal.q1, fill: normalColor },
    { label: 'Normal — Mediana', description: '50% de transacciones por debajo', value: data.normal.median, fill: normalColor },
    { label: 'Normal — Q3', description: '75% de transacciones por debajo', value: data.normal.q3, fill: normalColor },
  ]

  const fraudData = [
    { label: 'Fraude — Mínimo', description: 'Valor mínimo', value: data.fraud.min, fill: fraudColor },
    { label: 'Fraude — Q1', description: '25% de transacciones por debajo', value: data.fraud.q1, fill: fraudColor },
    { label: 'Fraude — Mediana', description: '50% de transacciones por debajo', value: data.fraud.median, fill: fraudColor },
    { label: 'Fraude — Q3', description: '75% de transacciones por debajo', value: data.fraud.q3, fill: fraudColor },
  ]

  const ticks = ['Mín', 'Q1', 'Mediana', 'Q3']

  const renderChart = (chartData, title, color, medianRef) => (
    <div className='card'>
      <div className='card-title'>{title}</div>
      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
        Mediana: <strong style={{ color }}>${medianRef.toFixed(2)}</strong>
      </div>
      <ResponsiveContainer width='100%' height={200}>
        <BarChart
          data={chartData.map((d, i) => ({ ...d, name: ticks[i] }))}
          margin={{ top: 10, right: 10, left: 10, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray='3 3' stroke='var(--border)' vertical={false} />
          <XAxis dataKey='name' tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} />
          <YAxis
            tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
            tickFormatter={v => `$${v}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine
            y={medianRef}
            stroke={color}
            strokeDasharray='4 2'
            strokeWidth={1.5}
          />
          <Bar dataKey='value' radius={[4, 4, 0, 0]}>
            {chartData.map((entry, i) => (
              <Cell key={i} fill={entry.fill} fillOpacity={0.5 + i * 0.15} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div className='charts-grid'>
        {renderChart(normalData, 'Distribución de montos — Normal', normalColor, data.normal.median)}
        {renderChart(fraudData, 'Distribución de montos — Fraude', fraudColor, data.fraud.median)}
      </div>
      <div className='card'>
        <div className='card-title'>Comparativa de medianas</div>
        <div style={{ display: 'flex', gap: 24 }}>
          {[
            { label: 'Mediana normal', value: data.normal.median, color: normalColor },
            { label: 'Mediana fraude', value: data.fraud.median, color: fraudColor },
            { label: 'Q3 normal', value: data.normal.q3, color: normalColor },
            { label: 'Q3 fraude', value: data.fraud.q3, color: fraudColor },
          ].map(({ label, value, color }) => (
            <div key={label} style={{
              flex: 1,
              background: 'var(--bg-secondary)',
              borderRadius: '6px',
              padding: '12px 16px',
              borderTop: `2px solid ${color}`,
            }}>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>{label}</div>
              <div style={{ fontSize: 18, fontWeight: 700, color }}>${value.toFixed(2)}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}