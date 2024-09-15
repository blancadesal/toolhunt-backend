<template>
  <div class="min-h-screen bg-base-200 flex items-center justify-center">
    <div class="card w-96 bg-base-100 shadow-xl">
      <div class="card-body items-center text-center">
        <div class="loading loading-spinner loading-lg"></div>
        <h2 class="card-title mt-4">Processing login...</h2>
        <p class="text-base-content/70">Please wait while we complete your authentication.</p>
      </div>
    </div>
  </div>
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
