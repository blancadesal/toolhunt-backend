<!-- profile.vue -->
<template>
  <div class="profile">
    <h1>Profile</h1>
    <div v-if="authState.loading">Loading...</div>
    <div v-else-if="authState.user">
      <p><strong>Username:</strong> {{ authState.user.username }}</p>
      <p><strong>Email:</strong> {{ authState.user.email }}</p>
    </div>
    <div v-else>
      <p>Please log in to view your profile.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const { authState, fetchUserData } = useAuth()
const route = useRoute()
const router = useRouter()

const handleCallback = async (code, state) => {
  try {
    const response = await fetch('http://localhost:8082/api/auth/callback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code, state }),
      credentials: 'include'
    })
    if (response.ok) {
      const data = await response.json()
      authState.value.user = data.user
      router.replace({ query: null })
    } else {
      console.error('OAuth callback failed:', response.status)
      router.push('/')
    }
  } catch (error) {
    console.error('Error handling OAuth callback:', error)
    router.push('/')
  }
}

onMounted(() => {
  const { code, state } = route.query
  if (code && state) {
    handleCallback(code, state)
  } else {
    fetchUserData()
  }
})
</script>

<style scoped>
.profile {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
}
</style>
