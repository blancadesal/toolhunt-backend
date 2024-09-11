<template>
  <div class="navbar bg-base-100 shadow-lg">
    <div class="flex-1">
      <NuxtLink to="/" class="btn btn-ghost normal-case text-2xl">Toolhunt</NuxtLink>
    </div>
    <div class="flex-none">
      <ul class="menu menu-horizontal px-1 items-center">
        <li><NuxtLink to="/leaderboard" class="text-lg px-4 py-2">Leaderboard</NuxtLink></li>
        <li><NuxtLink to="/profile" class="text-lg px-4 py-2">Profile</NuxtLink></li>
        <li class="ml-2">
          <a v-if="authState.user" @click="logout" class="btn btn-outline btn-primary normal-case px-4 py-2">Logout</a>
          <a v-else @click="login" class="btn btn-primary normal-case px-4 py-2">Login</a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
const { authState, fetchUserData } = useAuth()
const router = useRouter()

const login = async () => {
  try {
    const response = await fetch('http://localhost:8082/api/auth/login', {
      credentials: 'include'
    })
    const data = await response.json()
    window.location.href = data.login_url
  } catch (error) {
    console.error('Error initiating login:', error)
  }
}

const logout = async () => {
  try {
    const response = await fetch('http://localhost:8082/api/auth/logout', {
      method: 'POST',
      credentials: 'include'
    })
    if (response.ok) {
      authState.value.user = null
      router.push('/')
    } else {
      console.error('Logout failed:', response.status)
    }
  } catch (error) {
    console.error('Error during logout:', error)
  }
}

onMounted(() => {
  fetchUserData()
})
</script>
