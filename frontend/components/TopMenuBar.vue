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
            <a @click="handleAuthAction" class="text-primary hover:text-primary-focus">
              {{ isLoggedIn ? 'Logout' : 'Login' }}
            </a>
          </li>
        </ul>
      </div>
      <ul class="menu menu-horizontal px-1 hidden lg:flex items-center">
        <li><NuxtLink to="/leaderboard" class="text-lg px-4 py-2">Leaderboard</NuxtLink></li>
        <li><NuxtLink to="/profile" class="text-lg px-4 py-2">Profile</NuxtLink></li>
        <li class="ml-2">
          <a @click="handleAuthAction" :class="isLoggedIn ? 'btn btn-outline btn-primary' : 'btn btn-primary'" class="normal-case">
            {{ isLoggedIn ? 'Logout' : 'Login' }}
          </a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
const { isLoggedIn, logout, login } = useAuth()
const router = useRouter()

const handleAuthAction = async () => {
  if (isLoggedIn.value) {
    await logout()
    router.go(0)
  } else {
    const loginUrl = await login()
    if (loginUrl) {
      window.location.href = loginUrl
    }
  }
}
</script>
