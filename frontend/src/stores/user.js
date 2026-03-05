import { defineStore } from 'pinia'
import { ref } from 'vue'
import { auth } from '../api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  async function login(username, password) {
    const response = await auth.login(username, password)
    
    token.value = response.access_token
    userInfo.value = response.admin
    localStorage.setItem('token', token.value)
    localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    
    return response
  }

  async function register(username, email, password) {
    const response = await auth.register(username, email, password)
    return response
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  return {
    token,
    userInfo,
    login,
    register,
    logout
  }
})
