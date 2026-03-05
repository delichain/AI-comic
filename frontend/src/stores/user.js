import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  const isLoggedIn = computed(() => !!token.value)

  async function login(username, password) {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    token.value = response.access_token
    userInfo.value = response.admin
    localStorage.setItem('token', token.value)
    localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    
    return response
  }

  async function register(username, email, password) {
    const response = await api.post('/users', {
      username,
      email,
      password
    })
    return response
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  async function getUserProfile() {
    const response = await api.get('/user/profile')
    userInfo.value = response
    localStorage.setItem('userInfo', JSON.stringify(response))
    return response
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    login,
    register,
    logout,
    getUserProfile
  }
})
