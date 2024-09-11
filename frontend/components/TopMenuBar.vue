<template>
  <div class="top-menu-bar">
    <NuxtLink to="/" class="logo">Toolhunt</NuxtLink>
    <div class="spacer"></div>
    <NuxtLink to="/leaderboard">Leaderboard</NuxtLink>
    <NuxtLink to="/profile">Profile</NuxtLink>
    <button v-if="authState.user" @click="logout" class="login-button">Logout</button>
    <button v-else @click="login" class="login-button">Login</button>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const { authState, fetchUserData } = useAuth()
const router = useRouter()

const login = async () => {
  try {
    const response = await fetch('http://localhost:8082/api/auth/login', {
      credentials: 'include'
    })
    const data = await response.json()
    window.location.href = data.login_url
  } catch (error) {
    console.error('Error initiating login:', error)
  }
}

const logout = async () => {
  try {
    const response = await fetch('http://localhost:8082/api/auth/logout', {
      method: 'POST',
      credentials: 'include'
    })
    if (response.ok) {
      authState.value.user = null
      router.push('/')
    } else {
      console.error('Logout failed:', response.status)
    }
  } catch (error) {
    console.error('Error during logout:', error)
  }
}

onMounted(() => {
  fetchUserData()
})
</script>

<style scoped>
.top-menu-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #f0f0f0;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  text-decoration: none;
  color: #333;
}

.spacer {
  flex-grow: 1;
}

.login-button {
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.login-button:hover {
  background-color: #0056b3;
}

a {
  margin-right: 1rem;
  text-decoration: none;
  color: #007bff;
}

a:hover {
  text-decoration: underline;
}
</style>
