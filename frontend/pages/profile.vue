<!-- profile.vue -->
<template>
  <div>
    <h1>Profile</h1>
    <div v-if="loading">Loading...</div>
    <div v-else-if="user">
      <p>Username: {{ user.username }}</p>
      <p>Email: {{ user.email }}</p>
    </div>
    <div v-else>
      <p>Not logged in</p>
      <button @click="login">Log in</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const user = ref(null)
const loading = ref(true)
const route = useRoute()
const router = useRouter()

const fetchUserData = async () => {
  try {
    const token = localStorage.getItem('access_token')
    if (!token) {
      console.log('No access token found, user is not logged in')
      loading.value = false
      return
    }

    console.log('Fetching user data...')
    const response = await fetch('http://localhost:8082/api/user', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (response.ok) {
      user.value = await response.json()
      console.log('User data fetched successfully:', user.value)
    } else {
      console.error('Failed to fetch user data:', response.status)
      localStorage.removeItem('access_token')
    }
  } catch (error) {
    console.error('Error fetching user data:', error)
  } finally {
    loading.value = false
  }
}

const login = async () => {
  try {
    console.log('Initiating login process...')
    const response = await fetch('http://localhost:8082/api/auth/login')
    const data = await response.json()
    console.log('Received login URL:', data.login_url)
    window.location.href = data.login_url
  } catch (error) {
    console.error('Error initiating login:', error)
  }
}

const handleCallback = async (code, state) => {
  try {
    console.log('Handling OAuth callback...')
    console.log('Code:', code)
    console.log('State:', state)
    const response = await fetch('http://localhost:8082/api/auth/callback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code, state }),
    })
    if (response.ok) {
      const data = await response.json()
      console.log('Received data from callback:', data)
      localStorage.setItem('access_token', data.access_token)
      user.value = data.user
      console.log('User logged in successfully:', user.value)
    } else {
      console.error('OAuth callback failed:', response.status)
      const errorText = await response.text()
      console.error('Error details:', errorText)
    }
  } catch (error) {
    console.error('Error handling OAuth callback:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  console.log('Profile component mounted')
  const { code, state } = route.query
  if (code && state) {
    console.log('OAuth callback detected')
    handleCallback(code, state)
  } else {
    console.log('No OAuth callback detected, fetching user data')
    fetchUserData()
  }
})
</script>
