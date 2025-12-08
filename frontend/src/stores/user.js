import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const username = ref(localStorage.getItem('username') || '')
  const isAuthenticated = ref(!!localStorage.getItem('token'))

  const login = (userData) => {
    username.value = userData.username
    isAuthenticated.value = true
    localStorage.setItem('username', userData.username)
    if (userData.token) {
      localStorage.setItem('token', userData.token)
    }
  }

  const logout = () => {
    username.value = ''
    isAuthenticated.value = false
    localStorage.removeItem('username')
    localStorage.removeItem('token')
  }

  return {
    username,
    isAuthenticated,
    login,
    logout
  }
})

