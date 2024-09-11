<!-- login.vue -->
<template>
  <div>
    <h1>Login</h1>
    <button @click="login">Login with Toolhub</button>
  </div>
</template>

<script setup>
const login = async () => {
  try {
    const response = await fetch('http://localhost:8082/api/auth/login')
    if (!response.ok) {
      throw new Error('Failed to get login URL')
    }
    const data = await response.json()
    window.location.href = data.login_url
  } catch (error) {
    console.error('Error initiating login:', error)
  }
}
</script>