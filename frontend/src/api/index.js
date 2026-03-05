import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api/v1',
  timeout: 60000
})

// Request interceptor
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      const { status, data } = error.response
      
      if (status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        window.location.href = '/login'
      }
      
      return Promise.reject(data.detail || data.message || '请求失败')
    }
    return Promise.reject(error.message)
  }
)

// Auth API
export const auth = {
  login: (username, password) => api.post('/auth/login', null, { params: { username, password } }),
  register: (username, email, password) => api.post('/auth/register', null, { params: { username, password, role: 'user' } }),
}

// User API
export const user = {
  getProfile: () => api.get('/user/profile'),
  getAvailableTemplates: () => api.get('/templates/available'),
  generateImage: (templateId, variables) => api.post('/ai/generate', null, { params: { template_id: templateId, variables: JSON.stringify(variables) } }),
}

// Admin API
export const admin = {
  getUsers: (page, pageSize, status) => api.get('/users', { params: { page, page_size: pageSize, status } }),
  createUser: (username, email, password) => api.post('/users', null, { params: { username, email, password } }),
  updateUserQuota: (userId, dailyLimit, monthlyLimit) => api.patch(`/users/${userId}/quota`, null, { params: { daily_limit: dailyLimit, monthly_limit: monthlyLimit } }),
  disableUser: (userId) => api.patch(`/users/${userId}/disable`),
  getAIModels: () => api.get('/ai-models'),
  createAIModel: (data) => api.post('/ai-models', null, { params: data }),
  getTemplates: () => api.get('/templates'),
  createTemplate: (data) => api.post('/templates', null, { params: data }),
  getAPILogs: (page, pageSize, userId, isError) => api.get('/logs/api', { params: { page, page_size: pageSize, user_id: userId, is_error: isError } }),
  getStats: () => api.get('/stats/users'),
}

export default api
