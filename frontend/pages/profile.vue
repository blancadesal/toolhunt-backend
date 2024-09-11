<!-- profile.vue -->
<template>
  <div class="min-h-screen bg-base-200 py-8">
    <div class="container mx-auto px-4">
      <h1 class="text-3xl font-bold mb-6">Profile</h1>
      <div v-if="authState.loading" class="alert alert-info">
        <span class="loading loading-spinner"></span>
        Loading...
      </div>
      <div v-else-if="authState.user" class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">{{ authState.user.username }}</h2>
          <p><strong>Email:</strong> {{ authState.user.email }}</p>
        </div>
      </div>
      <div v-else class="alert alert-warning">
        Please log in to view your profile.
      </div>
    </div>
  </div>
</template>

<script setup>
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
