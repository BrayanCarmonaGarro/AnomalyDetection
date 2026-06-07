import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'

export default function ClassDistribution({ data }) {
  if (!data) return <div className='card' style={{ color: 'var(--text-muted)' }}>Cargando...</div>

  const pieData = [
    { name: 'Normal', value: data.normal },
    { name: 'Fraude', value: data.fraud },
  ]

  const barData = [
    { name: 'Normal', value: data.normal },
    { name: 'Fraude', value: data.fraud },
  ]

  const COLORS = ['#6366f1', '#ef4444']

  const fmt = (n) => n.toLocaleString('es-CR')

  return (
    <div className='card'>
      <div className='card-title'>Distribución de clases</div>
      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
        Total: {fmt(data.total)} transacciones — Fraude: {data.fraud_pct}%
      </div>

      <div style={{ display: 'flex', gap: 16 }}>
        {/* Pie */}
        <div style={{ flex: 1 }}>
          <ResponsiveContainer width='100%' height={200}>
            <PieChart>
              <Pie
                data={pieData}
                cx='50%'
                cy='50%'
                innerRadius={50}
                outerRadius={80}
                dataKey='value'
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
                labelLine={false}
              >
                {pieData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i]} />
                ))}
              </Pie>
              <Tooltip formatter={(v) => fmt(v)} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Bar */}
        <div style={{ flex: 1 }}>
          <ResponsiveContainer width='100%' height={200}>
            <BarChart data={barData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray='3 3' stroke='var(--border)' />
              <XAxis dataKey='name' tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} />
              <YAxis tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} tickFormatter={v => v >= 1000 ? `${(v/1000).toFixed(0)}k` : v} />
              <Tooltip formatter={(v) => fmt(v)} />
              <Bar dataKey='value' radius={[4, 4, 0, 0]}>
                {barData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}