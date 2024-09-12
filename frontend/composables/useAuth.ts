import { useState } from '#app'

export interface User {
  id: string
  username: string
  email: string
  // Add any other user properties here
}

export interface AuthState {
  user: User | null
  loading: boolean
}

export const useAuth = () => {
  const authState = useState<AuthState>('auth', () => ({
    user: null,
    loading: false
  }))

  const fetchUserData = async () => {
    authState.value.loading = true
    try {
      const response = await fetch('http://localhost:8082/api/v1/user', {
        credentials: 'include'
      })
      if (response.ok) {
        authState.value.user = await response.json()
      } else {
        authState.value.user = null
      }
    } catch (error) {
      console.error('Error fetching user data:', error)
      authState.value.user = null
    } finally {
      authState.value.loading = false
    }
  }

  return {
    authState,
    fetchUserData
  }
}
