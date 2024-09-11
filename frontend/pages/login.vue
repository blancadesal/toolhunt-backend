<!-- login.vue -->
<template>
  <div>
    <h1>Login</h1>
    <button @click="login">Login with Toolhub</button>
  </div>
</template>

<script setup>
const login = () => {
  window.location.href = 'http://localhost:8082/login'
}
</script>