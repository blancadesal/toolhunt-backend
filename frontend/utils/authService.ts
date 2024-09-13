const API_BASE_URL = 'http://localhost:8082/api/v1'

export const apiFetchUserData = async () => {
  const response = await fetch(`${API_BASE_URL}/user`, {
    credentials: 'include'
  })
  if (response.ok) {
    return await response.json()
  } else {
    return null
  }
}

export const apiLogin = (redirectPath: string) => {
  const loginUrl = `${API_BASE_URL}/auth/login?redirect_after=${encodeURIComponent(redirectPath)}`
  window.location.href = loginUrl
}

export const apiHandleCallback = async (code: string, state: string) => {
  const response = await fetch(`${API_BASE_URL}/auth/callback`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ code, state }),
    credentials: 'include'
  })
  if (response.ok) {
    const data = await response.json()
    return {
      user: data.user,
      redirectTo: data.redirect_to
    }
  } else {
    throw new Error(`Login failed: ${response.status}`)
  }
}

export const apiLogout = async () => {
  const response = await fetch(`${API_BASE_URL}/auth/logout`, {
    method: 'POST',
    credentials: 'include'
  })
  if (!response.ok) {
    throw new Error(`Logout failed: ${response.status}`)
  }
}
