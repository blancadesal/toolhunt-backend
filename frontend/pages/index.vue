<script setup>
const { authState } = useAuth()
</script>

<template>
  <div class="hero min-h-screen bg-base-200">
    <div class="hero-content text-center">
      <div class="max-w-md">
        <h1 class="text-5xl font-bold">Welcome to Toolhunt</h1>
        <p class="py-6">Discover and share the best developer tools and resources.</p>
        <NuxtLink to="/leaderboard" class="btn btn-primary">View Leaderboard</NuxtLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  text-align: center;
  padding: 2rem;
}
</style>
