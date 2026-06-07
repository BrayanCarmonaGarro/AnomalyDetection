import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
})

// EDA
export const getClassDistribution = () => api.get('/eda/class-distribution')
export const getAmountByClass = () => api.get('/eda/amount-by-class')
export const getFraudByCategory = () => api.get('/eda/fraud-by-category')
export const getTimePatterns = () => api.get('/eda/time-patterns')
export const getFraudByGender = () => api.get('/eda/fraud-by-gender')

// Features
export const getFeatures = () => api.get('/features')

// Predicción
export const predict = (data) => api.post('/predict', data)

//analisis contextual
export const analyzeContextual = (data) => api.post('/analyze-contextual', data)