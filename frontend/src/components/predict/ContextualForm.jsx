import { useState } from 'react'

const CATEGORIES = [
  'entertainment', 'food_dining', 'gas_transport', 'grocery_net',
  'grocery_pos', 'health_fitness', 'home', 'kids_pets',
  'misc_net', 'misc_pos', 'personal_care', 'shopping_net',
  'shopping_pos', 'travel'
]

const EMPTY = {
  amt: '',
  trans_date_trans_time: '',
  category: 'food_dining',
  lat: '',
  long: '',
  merch_lat: '',
  merch_long: '',
  city_pop: '',
  dob: '1985-03-15',
  model: 'lof',
}

const EXAMPLE_REFS = [
  { amt: 42.5, trans_date_trans_time: '2020-06-01 14:20:00', category: 'food_dining', lat: 36.0788, long: -81.1573, merch_lat: 36.0800, merch_long: -81.1580, city_pop: 50000, dob: '1985-03-15', model: 'lof' },
  { amt: 38.0, trans_date_trans_time: '2020-06-03 13:10:00', category: 'food_dining', lat: 36.0788, long: -81.1573, merch_lat: 36.0810, merch_long: -81.1560, city_pop: 50000, dob: '1985-03-15', model: 'lof' },
  { amt: 55.0, trans_date_trans_time: '2020-06-05 12:30:00', category: 'grocery_pos', lat: 36.0788, long: -81.1573, merch_lat: 36.0795, merch_long: -81.1570, city_pop: 50000, dob: '1985-03-15', model: 'lof' },
  { amt: 47.0, trans_date_trans_time: '2020-06-07 15:00:00', category: 'food_dining', lat: 36.0788, long: -81.1573, merch_lat: 36.0802, merch_long: -81.1575, city_pop: 50000, dob: '1985-03-15', model: 'lof' },
  { amt: 60.0, trans_date_trans_time: '2020-06-09 11:45:00', category: 'grocery_pos', lat: 36.0788, long: -81.1573, merch_lat: 36.0790, merch_long: -81.1568, city_pop: 50000, dob: '1985-03-15', model: 'lof' },
]

function TransactionRow({ t, index, onRemove }) {
  return (
    <div style={{
      background: 'var(--bg-secondary)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-sm)',
      padding: '10px 14px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      fontSize: 13,
    }}>
      <div>
        <span style={{ color: 'var(--text-muted)', marginRight: 8 }}>#{index + 1}</span>
        <span style={{ fontWeight: 500 }}>${t.amt}</span>
        <span style={{ color: 'var(--text-muted)', margin: '0 8px' }}>·</span>
        <span style={{ color: 'var(--text-secondary)' }}>{t.category.replace(/_/g, ' ')}</span>
        <span style={{ color: 'var(--text-muted)', margin: '0 8px' }}>·</span>
        <span style={{ color: 'var(--text-secondary)' }}>{t.trans_date_trans_time.slice(11, 16)}h</span>
      </div>
      <button
        onClick={() => onRemove(index)}
        style={{
          background: 'transparent',
          color: 'var(--text-muted)',
          fontSize: 16,
          padding: '2px 6px',
          borderRadius: 4,
        }}
      >
        ✕
      </button>
    </div>
  )
}

function AddTransactionForm({ onAdd }) {
  const [form, setForm] = useState(EMPTY)
  const [open, setOpen] = useState(false)

  const handle = (e) => setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))

  const submit = () => {
    if (!form.amt || !form.trans_date_trans_time || !form.lat || !form.long || !form.merch_lat || !form.merch_long || !form.city_pop) {
      alert('Completá todos los campos')
      return
    }
    onAdd({
      amt: parseFloat(form.amt),
      trans_date_trans_time: form.trans_date_trans_time,
      category: form.category,
      lat: parseFloat(form.lat),
      long: parseFloat(form.long),
      merch_lat: parseFloat(form.merch_lat),
      merch_long: parseFloat(form.merch_long),
      city_pop: parseInt(form.city_pop),
      dob: form.dob,
      model: form.model,
    })
    setForm(EMPTY)
    setOpen(false)
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        style={{
          background: 'var(--accent-light)',
          color: 'var(--accent)',
          border: '1px dashed rgba(99,102,241,0.4)',
          borderRadius: 'var(--radius-sm)',
          padding: '10px',
          width: '100%',
          fontSize: 13,
          fontWeight: 500,
        }}
      >
        + Agregar transacción de referencia
      </button>
    )
  }

  return (
    <div style={{
      background: 'var(--bg-secondary)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-sm)',
      padding: 16,
      display: 'flex',
      flexDirection: 'column',
      gap: 12,
    }}>
      <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
        Nueva transacción de referencia
      </div>

      <div className='grid-2'>
        <div className='form-group'>
          <label>Monto (USD)</label>
          <input name='amt' value={form.amt} onChange={handle} type='number' step='0.01' />
        </div>
        <div className='form-group'>
          <label>Fecha y hora</label>
          <input name='trans_date_trans_time' value={form.trans_date_trans_time} onChange={handle} placeholder='2020-06-01 14:00:00' />
        </div>
      </div>

      <div className='grid-2'>
        <div className='form-group'>
          <label>Categoría</label>
          <select name='category' value={form.category} onChange={handle}>
            {CATEGORIES.map(c => <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>)}
          </select>
        </div>
        <div className='form-group'>
          <label>Población ciudad</label>
          <input name='city_pop' value={form.city_pop} onChange={handle} type='number' />
        </div>
      </div>

      <div className='grid-2'>
        <div className='form-group'>
          <label>Lat titular</label>
          <input name='lat' value={form.lat} onChange={handle} type='number' step='any' />
        </div>
        <div className='form-group'>
          <label>Long titular</label>
          <input name='long' value={form.long} onChange={handle} type='number' step='any' />
        </div>
      </div>

      <div className='grid-2'>
        <div className='form-group'>
          <label>Lat comercio</label>
          <input name='merch_lat' value={form.merch_lat} onChange={handle} type='number' step='any' />
        </div>
        <div className='form-group'>
          <label>Long comercio</label>
          <input name='merch_long' value={form.merch_long} onChange={handle} type='number' step='any' />
        </div>
      </div>

      <div className='grid-2'>
        <button className='btn-primary' onClick={submit}>Agregar</button>
        <button
          onClick={() => setOpen(false)}
          style={{
            background: 'transparent',
            color: 'var(--text-muted)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-sm)',
            padding: '10px',
            fontSize: 14,
          }}
        >
          Cancelar
        </button>
      </div>
    </div>
  )
}

export default function ContextualForm({ onAnalyze, loading }) {
  const [refs, setRefs] = useState([])
  const [target, setTarget] = useState({
    amt: '',
    trans_date_trans_time: '',
    category: 'shopping_net',
    lat: '',
    long: '',
    merch_lat: '',
    merch_long: '',
    city_pop: '',
    dob: '1985-03-15',
    model: 'lof',
  })
  const [model, setModel] = useState('lof')

  const MODELS = [
    { value: 'lof', label: 'LOF (recomendado)' },
    { value: 'isolation_forest', label: 'Isolation Forest' },
    { value: 'autoencoder', label: 'Autoencoder' },
  ]

  const addRef = (t) => setRefs(prev => [...prev, t])
  const removeRef = (i) => setRefs(prev => prev.filter((_, idx) => idx !== i))
  const loadExamples = () => setRefs(EXAMPLE_REFS)

  const handleTarget = (e) => setTarget(prev => ({ ...prev, [e.target.name]: e.target.value }))

  const submit = () => {
    if (refs.length < 2) { alert('Necesitás al menos 2 transacciones de referencia'); return }
    if (!target.amt || !target.trans_date_trans_time || !target.lat || !target.long || !target.merch_lat || !target.merch_long || !target.city_pop) {
      alert('Completá todos los campos de la transacción a evaluar')
      return
    }
    const t = {
      amt: parseFloat(target.amt),
      trans_date_trans_time: target.trans_date_trans_time,
      category: target.category,
      lat: parseFloat(target.lat),
      long: parseFloat(target.long),
      merch_lat: parseFloat(target.merch_lat),
      merch_long: parseFloat(target.merch_long),
      city_pop: parseInt(target.city_pop),
      dob: target.dob,
      model,
    }
    const refsWithModel = refs.map(r => ({ ...r, model }))
    onAnalyze({ reference_transactions: refsWithModel, target_transaction: t, model })
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

      {/* Transacciones de referencia */}
      <div className='card'>
<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div className='card-title' style={{ marginBottom: 0 }}>
              Transacciones de referencia
            </div>
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              fontSize: 11,
              padding: '2px 8px',
              background: refs.length >= 2 ? 'var(--success-light)' : 'var(--danger-light)',
              color: refs.length >= 2 ? 'var(--success)' : 'var(--danger)',
              border: `1px solid ${refs.length >= 2 ? 'rgba(122,158,126,0.25)' : 'rgba(184,92,74,0.25)'}`,
              borderRadius: 4,
              fontWeight: 600,
              width: 'fit-content',
            }}>
              {refs.length} / mín. 2
            </span>
          </div>
          {refs.length === 0 && (
            <button
              onClick={loadExamples}
              style={{
                background: 'transparent',
                color: 'var(--accent)',
                border: '1px solid rgba(99,102,241,0.3)',
                borderRadius: 'var(--radius-sm)',
                padding: '6px 12px',
                fontSize: 12,
              }}
            >
              Cargar ejemplos
            </button>
          )}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {refs.map((t, i) => (
            <TransactionRow key={i} t={t} index={i} onRemove={removeRef} />
          ))}
          <AddTransactionForm onAdd={addRef} />
        </div>
      </div>

      {/* Modelo */}
      <div className='card'>
        <div className='card-title'>Modelo global</div>
        <div className='form-group'>
          <label>Modelo para el análisis global</label>
          <select value={model} onChange={e => setModel(e.target.value)}>
            {MODELS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
          </select>
        </div>
      </div>

      {/* Transacción a evaluar */}
      <div className='card'>
        <div className='card-title'>Transacción a evaluar</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div className='grid-2'>
            <div className='form-group'>
              <label>Monto (USD)</label>
              <input name='amt' value={target.amt} onChange={handleTarget} type='number' step='0.01' />
            </div>
            <div className='form-group'>
              <label>Fecha y hora</label>
              <input name='trans_date_trans_time' value={target.trans_date_trans_time} onChange={handleTarget} placeholder='2020-06-21 02:30:00' />
            </div>
          </div>

          <div className='grid-2'>
            <div className='form-group'>
              <label>Categoría</label>
              <select name='category' value={target.category} onChange={handleTarget}>
                {CATEGORIES.map(c => <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>)}
              </select>
            </div>
            <div className='form-group'>
              <label>Población ciudad</label>
              <input name='city_pop' value={target.city_pop} onChange={handleTarget} type='number' />
            </div>
          </div>

          <div className='grid-2'>
            <div className='form-group'>
              <label>Lat titular</label>
              <input name='lat' value={target.lat} onChange={handleTarget} type='number' step='any' />
            </div>
            <div className='form-group'>
              <label>Long titular</label>
              <input name='long' value={target.long} onChange={handleTarget} type='number' step='any' />
            </div>
          </div>

          <div className='grid-2'>
            <div className='form-group'>
              <label>Lat comercio</label>
              <input name='merch_lat' value={target.merch_lat} onChange={handleTarget} type='number' step='any' />
            </div>
            <div className='form-group'>
              <label>Long comercio</label>
              <input name='merch_long' value={target.merch_long} onChange={handleTarget} type='number' step='any' />
            </div>
          </div>

          <button className='btn-primary' onClick={submit} disabled={loading}>
            {loading ? 'Analizando...' : 'Analizar con contexto'}
          </button>
        </div>
      </div>
    </div>
  )
}