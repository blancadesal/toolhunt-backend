<!-- profile.vue -->
<template>
  <div>
    <h1>Profile</h1>
    <div v-if="user">
      <p>Welcome, {{ user.username }}!</p>
      <p>Email: {{ user.email }}</p>
      <!-- Display other user information as needed -->
    </div>
    <div v-else-if="loading">
      Loading user data...
    </div>
    <div v-else>
      <p>Not logged in. <a href="/login">Go to login</a></p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const user = ref(null)
const loading = ref(true)

const fetchUserData = async () => {
  try {
    const response = await fetch('http://localhost:8082/api/user', {
      credentials: 'include'
    })
    if (response.ok) {
      user.value = await response.json()
    } else {
      console.error('Failed to fetch user data')
    }
  } catch (error) {
    console.error('Error:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchUserData()
})
</script>