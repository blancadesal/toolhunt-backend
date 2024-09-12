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

  const logout = async () => {
    try {
      const response = await fetch('http://localhost:8082/api/v1/auth/logout', {
        method: 'POST',
        credentials: 'include'
      })
      if (response.ok) {
        authState.value.user = null
      } else {
        console.error('Logout failed:', response.status)
      }
    } catch (error) {
      console.error('Error during logout:', error)
    }
  }

  const login = async () => {
    const currentRoute = useRoute()
    const currentPath = currentRoute.fullPath
    try {
      const response = await fetch(`http://localhost:8082/api/v1/auth/login?redirect_after=${encodeURIComponent(currentPath)}`, {
        credentials: 'include'
      })
      const data = await response.json()
      return data.login_url
    } catch (error) {
      console.error('Error initiating login:', error)
      return null
    }
  }

  const handleCallback = async (code: string, state: string) => {
    try {
      const response = await fetch('http://localhost:8082/api/v1/auth/callback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code, state }),
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        return data.redirect_to
      } else {
        throw new Error(`Login failed: ${response.status}`)
      }
    } catch (error) {
      console.error('Error during login callback:', error)
      throw error
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
