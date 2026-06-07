import { useState } from 'react'

const CATEGORIES = [
  'entertainment', 'food_dining', 'gas_transport', 'grocery_net',
  'grocery_pos', 'health_fitness', 'home', 'kids_pets',
  'misc_net', 'misc_pos', 'personal_care', 'shopping_net',
  'shopping_pos', 'travel'
]

const MODELS = [
  { value: 'lof', label: 'Local Outlier Factor (recomendado)' },
  { value: 'isolation_forest', label: 'Isolation Forest' },
  { value: 'autoencoder', label: 'Autoencoder' },
]

const DEFAULTS = {
  amt: '150.00',
  trans_date_trans_time: '2020-06-21 02:30:00',
  category: 'shopping_net',
  lat: '36.0788',
  long: '-81.1573',
  merch_lat: '36.011293',
  merch_long: '-82.048315',
  city_pop: '3495',
  dob: '1985-03-15',
  model: 'lof',
}

export default function TransactionForm({ onPredict, loading }) {
  const [form, setForm] = useState(DEFAULTS)

  const handle = (e) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const submit = () => {
    onPredict({
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
  }

  return (
    <div className='card' style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div className='card-title'>Nueva transacción</div>

      <div className='form-group'>
        <label>Modelo</label>
        <select name='model' value={form.model} onChange={handle}>
          {MODELS.map(m => (
            <option key={m.value} value={m.value}>{m.label}</option>
          ))}
        </select>
      </div>

      <div className='form-group'>
        <label>Monto (USD)</label>
        <input name='amt' value={form.amt} onChange={handle} type='number' step='0.01' />
      </div>

      <div className='form-group'>
        <label>Fecha y hora</label>
        <input name='trans_date_trans_time' value={form.trans_date_trans_time} onChange={handle} placeholder='2020-06-21 02:30:00' />
      </div>

      <div className='form-group'>
        <label>Categoría</label>
        <select name='category' value={form.category} onChange={handle}>
          {CATEGORIES.map(c => (
            <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>
          ))}
        </select>
      </div>

      <div className='form-group'>
        <label>Fecha de nacimiento del titular</label>
        <input name='dob' value={form.dob} onChange={handle} placeholder='1985-03-15' />
      </div>

      <div className='form-group'>
        <label>Población de la ciudad</label>
        <input name='city_pop' value={form.city_pop} onChange={handle} type='number' />
      </div>

      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
        Ubicación del titular
      </div>
      <div className='grid-2'>
        <div className='form-group'>
          <label>Latitud</label>
          <input name='lat' value={form.lat} onChange={handle} type='number' step='any' />
        </div>
        <div className='form-group'>
          <label>Longitud</label>
          <input name='long' value={form.long} onChange={handle} type='number' step='any' />
        </div>
      </div>

      <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
        Ubicación del comercio
      </div>
      <div className='grid-2'>
        <div className='form-group'>
          <label>Latitud</label>
          <input name='merch_lat' value={form.merch_lat} onChange={handle} type='number' step='any' />
        </div>
        <div className='form-group'>
          <label>Longitud</label>
          <input name='merch_long' value={form.merch_long} onChange={handle} type='number' step='any' />
        </div>
      </div>

      <button className='btn-primary' onClick={submit} disabled={loading}>
        {loading ? 'Analizando...' : 'Analizar transacción'}
      </button>
    </div>
  )
}