<!-- profile.vue -->
<template>
  <div class="min-h-screen bg-base-200 py-8">
    <div class="container mx-auto px-4">
      <h1 class="text-3xl font-bold mb-6">Profile</h1>
      <div v-if="authState.loading" class="alert alert-info">
        <span class="loading loading-spinner"></span>
        Loading...
      </div>
      <div v-else-if="isLoggedIn" class="card bg-base-100 shadow-xl">
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
const { authState, isLoggedIn, fetchUserData } = useAuth()

onMounted(() => {
  fetchUserData()
})
</script>
