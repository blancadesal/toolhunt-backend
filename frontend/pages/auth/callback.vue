<template>
  <div>Processing login...</div>
</template>

<script setup>
const route = useRoute()
const router = useRouter()
const { authState, fetchUserData } = useAuth()

onMounted(async () => {
  const { code, state } = route.query
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
      await fetchUserData()
      router.push(data.redirect_to || '/')
    } else {
      console.error('Login failed:', response.status)
      router.push('/')
    }
  } catch (error) {
    console.error('Error during login callback:', error)
    router.push('/')
  }
})
</script>
