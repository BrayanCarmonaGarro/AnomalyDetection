import { useState, useEffect } from 'react'
import Sidebar from './components/layout/Sidebar'
import TransactionForm from './components/predict/TransactionForm'
import PredictionResult from './components/predict/PredictionResult'
import ClassDistribution from './components/eda/ClassDistribution'
import AmountBoxplot from './components/eda/AmountBoxplot'
import FraudByCategory from './components/eda/FraudByCategory'
import TimePatterns from './components/eda/TimePatterns'
import FraudByGender from './components/eda/FraudByGender'
import ComparisonTable from './components/comparison/ComparisonTable'
import ComparisonChart from './components/comparison/ComparisonChart'
import ContextualForm from './components/predict/ContextualForm'
import ContextualResult from './components/predict/ContextualResult'
import { analyzeContextual, getClassDistribution, getAmountByClass, getFraudByCategory, getTimePatterns, getFraudByGender, predict } from './api/client'

const BoltIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none"
    stroke="var(--text-muted)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
  </svg>
)

const BrainIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none"
    stroke="var(--text-muted)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.46 2.5 2.5 0 0 1-1.04-4.79A2.5 2.5 0 0 1 7 5.5a2.5 2.5 0 0 1 2.5-3.5z" />
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.46 2.5 2.5 0 0 0 1.04-4.79A2.5 2.5 0 0 0 17 5.5a2.5 2.5 0 0 0-2.5-3.5z" />
  </svg>
)

export default function App() {
  const [section, setSection] = useState('predict')
  const [predResult, setPredResult] = useState(null)
  const [predLoading, setPredLoading] = useState(false)
  const [edaClass, setEdaClass] = useState(null)
  const [edaAmount, setEdaAmount] = useState(null)
  const [edaCategory, setEdaCategory] = useState(null)
  const [edaTime, setEdaTime] = useState(null)
  const [edaGender, setEdaGender] = useState(null)
  const [contextualResult, setContextualResult] = useState(null)
  const [contextualLoading, setContextualLoading] = useState(false)

  useEffect(() => {
    getClassDistribution().then(r => setEdaClass(r.data)).catch(() => {})
    getAmountByClass().then(r => setEdaAmount(r.data)).catch(() => {})
    getFraudByCategory().then(r => setEdaCategory(r.data)).catch(() => {})
    getTimePatterns().then(r => setEdaTime(r.data)).catch(() => {})
    getFraudByGender().then(r => setEdaGender(r.data)).catch(() => {})
  }, [])

  const handlePredict = async (values) => {
    setPredLoading(true)
    setPredResult(null)
    try {
      const res = await predict(values)
      setPredResult(res.data)
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message))
    } finally {
      setPredLoading(false)
    }
  }

  const handleContextual = async (values) => {
    setContextualLoading(true)
    setContextualResult(null)
    try {
      const res = await analyzeContextual(values)
      setContextualResult(res.data)
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message))
    } finally {
      setContextualLoading(false)
    }
  }

  const EmptyState = ({ icon, line1, line2 }) => (
    <div className='card' style={{
      color: 'var(--text-muted)',
      textAlign: 'center',
      padding: '52px 32px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: 10,
    }}>
      <div style={{
        width: 52, height: 52,
        borderRadius: '12px',
        background: 'var(--bg-secondary)',
        border: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 4,
      }}>
        {icon}
      </div>
      <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{line1}</div>
      <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>{line2}</div>
    </div>
  )

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar active={section} onChange={setSection} />

      <main style={{
        marginLeft: 220,
        flex: 1,
        padding: 32,
        maxWidth: 1200,
      }}>

        {/* PREDICCIÓN */}
        {section === 'predict' && (
          <div>
            <div className='section-title'>Predicción en vivo</div>
            <div className='section-subtitle'>
              Ingresá los datos de una transacción para analizarla con el modelo seleccionado
            </div>
            <div style={{ display: 'flex', gap: 24, alignItems: 'flex-start' }}>
              <div style={{ flex: '0 0 360px' }}>
                <TransactionForm onPredict={handlePredict} loading={predLoading} />
              </div>
              <div style={{ flex: 1 }}>
                {predResult
                  ? <PredictionResult result={predResult} />
                  : <EmptyState
                      icon={<BoltIcon />}
                      line1='Completá el formulario y hacé clic en'
                      line2='Analizar transacción'
                    />
                }
              </div>
            </div>
          </div>
        )}

        {/* EDA */}
        {section === 'eda' && (
          <div>
            <div className='section-title'>Análisis exploratorio</div>
            <div className='section-subtitle'>
              Patrones del dataset de 1.9M transacciones — enero 2019 a diciembre 2020
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div className='charts-grid'>
                <ClassDistribution data={edaClass} />
                <AmountBoxplot data={edaAmount} />
              </div>
              <FraudByCategory data={edaCategory} />
              <TimePatterns data={edaTime} />
              <FraudByGender data={edaGender} />
            </div>
          </div>
        )}

        {/* MODELOS */}
        {section === 'models' && (
          <div>
            <div className='section-title'>Resultados de modelos</div>
            <div className='section-subtitle'>
              Comparativa final con umbral calibrado en validación y métricas en test
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <ComparisonTable />
              <ComparisonChart />
            </div>
          </div>
        )}

        {/* CONTEXTUAL */}
        {section === 'contextual' && (
          <div>
            <div className='section-title'>Análisis contextual</div>
            <div className='section-subtitle'>
              Ingresá transacciones de referencia normales y analizá una nueva contra ese perfil
            </div>
            <div style={{ display: 'flex', gap: 24, alignItems: 'flex-start' }}>
              <div style={{ flex: '0 0 420px' }}>
                <ContextualForm onAnalyze={handleContextual} loading={contextualLoading} />
              </div>
              <div style={{ flex: 1 }}>
                {contextualResult
                  ? <ContextualResult result={contextualResult} />
                  : <EmptyState
                      icon={<BrainIcon />}
                      line1='Cargá las transacciones de referencia'
                      line2='y completá la transacción a evaluar'
                    />
                }
              </div>
            </div>
          </div>
        )}

      </main>
    </div>
  )
}