import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell
} from 'recharts'

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div style={{
      background: 'var(--bg-card)', border: '1px solid var(--border)',
      borderRadius: 8, padding: '10px 14px', fontSize: 12,
    }}>
      <div style={{ fontWeight: 600, marginBottom: 6 }}>{d.category}</div>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16 }}>
        <span style={{ color: 'var(--text-muted)' }}>Tasa de fraude</span>
        <span style={{ color: 'var(--danger)' }}>{d.fraud_rate}%</span>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16 }}>
        <span style={{ color: 'var(--text-muted)' }}>Fraudes</span>
        <span>{d.fraud_count.toLocaleString('es-CR')}</span>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16 }}>
        <span style={{ color: 'var(--text-muted)' }}>Total</span>
        <span>{d.total.toLocaleString('es-CR')}</span>
      </div>
    </div>
  )
}

export default function FraudByCategory({ data }) {
  if (!data) return <div className='card' style={{ color: 'var(--text-muted)' }}>Cargando...</div>

  const maxRate = Math.max(...data.map(d => d.fraud_rate))

  return (
    <div className='card'>
      <div className='card-title'>Tasa de fraude por categoría</div>
      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
        Ordenado de mayor a menor tasa de fraude
      </div>
      <ResponsiveContainer width='100%' height={280}>
        <BarChart
          data={data}
          margin={{ top: 10, right: 10, left: 0, bottom: 60 }}
        >
          <CartesianGrid strokeDasharray='3 3' stroke='var(--border)' vertical={false} />
          <XAxis
            dataKey='category'
            tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
            angle={-40}
            textAnchor='end'
            interval={0}
          />
          <YAxis
            tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
            tickFormatter={v => `${v}%`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey='fraud_rate' radius={[4, 4, 0, 0]} isAnimationActive={false}>
            {data.map((entry, i) => (
              <Cell
                key={i}
                fill={`rgba(239, 68, 68, ${0.3 + 0.7 * (entry.fraud_rate / maxRate)})`}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}