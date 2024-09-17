<!-- profile.vue -->
<template>
  <div class="flex flex-col min-h-screen py-12">
    <div class="container mx-auto px-4 max-w-md">
      <h1 class="text-4xl font-bold mb-8 text-center text-secondary">Profile</h1>
      <div v-if="authState.loading" class="flex justify-center">
        <span class="loading loading-spinner loading-lg"></span>
      </div>
      <div v-else-if="isLoggedIn" class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title text-2xl">{{ authState.user.username }}</h2>
          <p class="text-base-content/70">{{ authState.user.email }}</p>
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
