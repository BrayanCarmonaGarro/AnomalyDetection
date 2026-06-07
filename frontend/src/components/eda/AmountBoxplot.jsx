import {
  ComposedChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell
} from 'recharts'

const BoxShape = (props) => {
  const { x, y, width, height, payload } = props
  if (!payload) return null

  const { q1, q3, min, max, median } = payload
  const yScale = props.yAxis?.scale
  if (!yScale) return null

  const yQ1 = yScale(q1)
  const yQ3 = yScale(q3)
  const yMin = yScale(min)
  const yMax = yScale(max)
  const yMedian = yScale(median)
  const cx = x + width / 2
  const hw = width * 0.3

  return (
    <g>
      {/* caja */}
      <rect x={x + width * 0.1} y={yQ3} width={width * 0.8}
        height={yQ1 - yQ3} fill={payload.fill} fillOpacity={0.7}
        stroke={payload.fill} strokeWidth={1.5} />
      {/* mediana */}
      <line x1={x + width * 0.1} x2={x + width * 0.9}
        y1={yMedian} y2={yMedian} stroke='white' strokeWidth={2} />
      {/* whisker inferior */}
      <line x1={cx} x2={cx} y1={yQ1} y2={yMin} stroke={payload.fill} strokeWidth={1.5} strokeDasharray='3 2' />
      <line x1={cx - hw} x2={cx + hw} y1={yMin} y2={yMin} stroke={payload.fill} strokeWidth={1.5} />
      {/* whisker superior */}
      <line x1={cx} x2={cx} y1={yQ3} y2={yMax} stroke={payload.fill} strokeWidth={1.5} strokeDasharray='3 2' />
      <line x1={cx - hw} x2={cx + hw} y1={yMax} y2={yMax} stroke={payload.fill} strokeWidth={1.5} />
    </g>
  )
}

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div style={{
      background: 'var(--bg-card)', border: '1px solid var(--border)',
      borderRadius: 8, padding: '10px 14px', fontSize: 12,
    }}>
      <div style={{ fontWeight: 600, marginBottom: 6 }}>{d.name}</div>
      {[['Máximo', d.max], ['Q3', d.q3], ['Mediana', d.median],
        ['Q1', d.q1], ['Mínimo', d.min]].map(([l, v]) => (
        <div key={l} style={{ display: 'flex', justifyContent: 'space-between', gap: 16 }}>
          <span style={{ color: 'var(--text-muted)' }}>{l}</span>
          <span>${v?.toFixed(2)}</span>
        </div>
      ))}
    </div>
  )
}

export default function AmountBoxplot({ data }) {
  if (!data) return <div className='card' style={{ color: 'var(--text-muted)' }}>Cargando...</div>

  const normal = data.normal
  const fraud = data.fraud

  const chartData = [
    { name: 'Normal', ...normal, fill: '#6366f1' },
    { name: 'Fraude', ...fraud, fill: '#ef4444' },
  ]

  const chartDataLog = [
    { name: 'Normal', ...data.normal_log, fill: '#6366f1' },
    { name: 'Fraude', ...data.fraud_log, fill: '#ef4444' },
  ]

  const renderChart = (cData, title, prefix = '$') => (
    <div style={{ flex: 1 }}>
      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8, textAlign: 'center' }}>
        {title}
      </div>
      <ResponsiveContainer width='100%' height={220}>
        <ComposedChart data={cData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray='3 3' stroke='var(--border)' />
          <XAxis dataKey='name' tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} />
          <YAxis tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
            tickFormatter={v => `${prefix}${v.toFixed(1)}`} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey='max' shape={<BoxShape />} isAnimationActive={false}>
            {cData.map((_, i) => <Cell key={i} fill={cData[i].fill} />)}
          </Bar>
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )

  return (
    <div className='card'>
      <div className='card-title'>Monto por clase</div>
      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
        Mediana normal: ${normal.median} — Mediana fraude: ${fraud.median}
      </div>
      <div style={{ display: 'flex', gap: 16 }}>
        {renderChart(chartData, 'Escala original')}
        {renderChart(chartDataLog, 'Escala log', '')}
      </div>
    </div>
  )
}