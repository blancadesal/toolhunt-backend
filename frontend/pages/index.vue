<script setup>
const { authState } = useAuth()
</script>

<template>
  <div class="home">
    <h1>Welcome to Our App</h1>
    <p v-if="authState.user">Hello, {{ authState.user.username }}!</p>
    <p v-else>This is the homepage of our amazing application.</p>
  </div>
</template>

<style scoped>
.home {
  text-align: center;
  padding: 2rem;
}
</style>
