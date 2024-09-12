<template>
  <div class="navbar bg-base-100 shadow-lg">
    <div class="navbar-start">
      <NuxtLink to="/" class="btn btn-ghost normal-case text-2xl flex items-center">
        <img src="@/assets/logo-main.svg" alt="Toolhunt Logo" class="w-12 h-12 mr-3" />
        <span class="font-bold">Toolhunt</span>
      </NuxtLink>
    </div>
    <div class="navbar-end">
      <div class="dropdown dropdown-end">
        <label tabindex="0" class="btn btn-ghost lg:hidden">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h8m-8 6h16" /></svg>
        </label>
        <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
          <li><NuxtLink to="/leaderboard">Leaderboard</NuxtLink></li>
          <li><NuxtLink to="/profile">Profile</NuxtLink></li>
          <li>
            <a v-if="authState.user" @click="logout" class="text-primary hover:text-primary-focus">Logout</a>
            <a v-else @click="login" class="text-primary hover:text-primary-focus">Login</a>
          </li>
        </ul>
      </div>
      <ul class="menu menu-horizontal px-1 hidden lg:flex items-center">
        <li><NuxtLink to="/leaderboard" class="text-lg px-4 py-2">Leaderboard</NuxtLink></li>
        <li><NuxtLink to="/profile" class="text-lg px-4 py-2">Profile</NuxtLink></li>
        <li class="ml-2">
          <a v-if="authState.user" @click="logout" class="btn btn-outline btn-primary normal-case">Logout</a>
          <a v-else @click="login" class="btn btn-primary normal-case">Login</a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
const { authState, fetchUserData } = useAuth()
const router = useRouter()
const route = useRoute()

const login = async () => {
  try {
    const currentPath = route.fullPath
    const response = await fetch(`http://localhost:8082/api/v1/auth/login?redirect_after=${encodeURIComponent(currentPath)}`, {
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
    const response = await fetch('http://localhost:8082/api/v1/auth/logout', {
      method: 'POST',
      credentials: 'include'
    })
    if (response.ok) {
      authState.value.user = null
      // Instead of redirecting to '/', refresh the current page
      router.go(0)
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
