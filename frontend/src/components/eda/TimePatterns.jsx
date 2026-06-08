import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: 'var(--bg-card)', border: '1px solid var(--border)',
      borderRadius: 8, padding: '10px 14px', fontSize: 12,
    }}>
      <div style={{ fontWeight: 600, marginBottom: 4 }}>{label}</div>
      <div style={{ color: 'var(--danger)' }}>
        Tasa de fraude: {payload[0].value}%
      </div>
    </div>
  )
}

export default function TimePatterns({ data }) {
  if (!data) return <div className='card' style={{ color: 'var(--text-muted)' }}>Cargando...</div>

  const hourData = data.by_hour.map(d => ({
    ...d,
    label: `${String(d.hour).padStart(2, '0')}:00`,
  }))

  return (
    <div className='card'>
      <div className='card-title'>Patrones temporales de fraude</div>

      {/* Por hora */}
      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>
        Tasa de fraude por hora del día
      </div>
      <ResponsiveContainer width='100%' height={180}>
        <LineChart data={hourData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray='3 3' stroke='var(--border)' />
          <XAxis
            dataKey='label'
            tick={{ fill: 'var(--text-secondary)', fontSize: 10 }}
            interval={2}
          />
          <YAxis
            tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
            tickFormatter={v => `${v}%`}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine y={0.52} stroke='var(--text-muted)' strokeDasharray='4 2'
            label={{ value: 'promedio', fill: 'var(--text-muted)', fontSize: 10 }} />
          <Line
            type='monotone'
            dataKey='fraud_rate'
            stroke='var(--danger)'
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Por día */}
      <div style={{ fontSize: 12, color: 'var(--text-muted)', margin: '20px 0 8px' }}>
        Tasa de fraude por día de la semana
      </div>
      <ResponsiveContainer width='100%' height={160}>
        <LineChart data={data.by_dow} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray='3 3' stroke='var(--border)' />
          <XAxis
            dataKey='day'
            tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
          />
          <YAxis
            tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
            tickFormatter={v => `${v}%`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type='monotone'
            dataKey='fraud_rate'
            stroke='var(--accent)'
            strokeWidth={2}
            dot={{ fill: 'var(--accent)', r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}