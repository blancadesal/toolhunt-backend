// composables/useAuth.ts

import { computed } from 'vue'
import { useState, useRoute } from '#app'
import { toolhuntApi, type User } from '~/utils/ToolhuntApiClient'

export interface AuthState {
  user: User | null
  loading: boolean
}

export const useAuth = () => {
  const authState = useState<AuthState>('auth', () => ({
    user: null,
    loading: false
  }))

  const isLoggedIn = computed(() => authState.value.user != null)

  const fetchUserData = async () => {
    authState.value.loading = true
    try {
      authState.value.user = await toolhuntApi.fetchUserData()
    } catch (error) {
      console.error('Error fetching user data:', error)
      authState.value.user = null
    } finally {
      authState.value.loading = false
    }
  }

  const login = () => {
    const currentRoute = useRoute()
    const currentPath = currentRoute.fullPath
    toolhuntApi.login(currentPath)
  }

  const handleCallback = async (code: string, state: string) => {
    try {
      const { user, redirectTo } = await toolhuntApi.handleCallback(code, state)
      authState.value.user = user
      return redirectTo
    } catch (error) {
      console.error('Error during login callback:', error)
      throw error
    }
  }

  const logout = async () => {
    try {
      await toolhuntApi.logout()
      authState.value.user = null
    } catch (error) {
      console.error('Error during logout:', error)
    }
  }

  return {
    authState,
    isLoggedIn,
    fetchUserData,
    logout,
    login,
    handleCallback
  }
}