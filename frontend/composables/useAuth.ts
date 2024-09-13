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

  const isLoggedIn = computed(() => authState.value.user != null)

  const fetchUserData = async () => {
    authState.value.loading = true
    try {
      authState.value.user = await apiFetchUserData()
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
    apiLogin(currentPath)
  }

  const handleCallback = async (code: string, state: string) => {
    try {
      const { user, redirectTo } = await apiHandleCallback(code, state)
      authState.value.user = user
      return redirectTo
    } catch (error) {
      console.error('Error during login callback:', error)
      throw error
    }
  }

  const logout = async () => {
    try {
      await apiLogout()
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
