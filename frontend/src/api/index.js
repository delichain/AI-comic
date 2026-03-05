import axios from 'axios'
import { useUserStore } from '../stores/user'
import router from '../router'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 60000
})

// Request interceptor
api.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
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
        const userStore = useUserStore()
        userStore.logout()
        router.push('/login')
      }
      
      return Promise.reject(data.detail || '请求失败')
    }
    return Promise.reject(error.message)
  }
)

export default api
