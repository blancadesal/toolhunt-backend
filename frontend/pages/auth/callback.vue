<template>
  <div>Processing login...</div>
</template>

<script setup>
const route = useRoute()
const router = useRouter()
const { handleCallback } = useAuth()

onMounted(async () => {
  const { code, state } = route.query
  try {
    const redirectTo = await handleCallback(code, state)
    router.push(redirectTo || '/')
  } catch (error) {
    console.error('Error during login callback:', error)
    router.push('/')
  }
})
</script>
