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
      <div style={{ fontWeight: 600, marginBottom: 6 }}>{d.gender}</div>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16 }}>
        <span style={{ color: 'var(--text-muted)' }}>Tasa de fraude</span>
        <span style={{ color: 'var(--danger)' }}>{d.fraud_rate}%</span>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16 }}>
        <span style={{ color: 'var(--text-muted)' }}>Total transacciones</span>
        <span>{d.total.toLocaleString('es-CR')}</span>
      </div>
    </div>
  )
}

export default function FraudByGender({ data }) {
  if (!data) return <div className='card' style={{ color: 'var(--text-muted)' }}>Cargando...</div>

  const COLORS = ['#a78bfa', '#60a5fa']

  return (
    <div className='card'>
      <div className='card-title'>Tasa de fraude por género</div>
      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
        La diferencia es mínima — género no se usa como variable en los modelos
      </div>

      <div style={{ display: 'flex', gap: 16 }}>
        {/* Total de transacciones */}
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8, textAlign: 'center' }}>
            Total de transacciones
          </div>
          <ResponsiveContainer width='100%' height={200}>
            <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray='3 3' stroke='var(--border)' />
              <XAxis dataKey='gender' tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} />
              <YAxis
                tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
                tickFormatter={v => `${(v / 1000).toFixed(0)}k`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey='total' radius={[4, 4, 0, 0]}>
                {data.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Tasa de fraude */}
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8, textAlign: 'center' }}>
            Tasa de fraude (%)
          </div>
          <ResponsiveContainer width='100%' height={200}>
            <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray='3 3' stroke='var(--border)' />
              <XAxis dataKey='gender' tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} />
              <YAxis
                tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
                tickFormatter={v => `${v}%`}
                domain={[0, 1]}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey='fraud_rate' radius={[4, 4, 0, 0]}>
                {data.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}