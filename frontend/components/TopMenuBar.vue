<script setup>

const menuItems = [
  { to: '/leaderboard', label: 'Leaderboard' },
  { to: '/profile', label: 'Profile' },
	{ to: '/about', label: 'About' },
	{ to: '/search', label: 'Search' },
]

const handleAuthAction = async () => {
  if (isLoggedIn.value) {
    await logout()
    router.go(0)
  } else {
    const loginUrl = await login()
    if (loginUrl) window.location.href = loginUrl
  }
}
</script>

<template>
  <div class="navbar bg-base-100 shadow-lg text-lg py-2 sm:py-3 md:py-4 px-2 sm:px-4 md:px-6">
    <div class="flex-1">
      <NuxtLink to="/" class="flex items-center hover:opacity-80 transition-opacity duration-200">
        <img src="@/assets/logo-main.svg" alt="Toolhunt Logo" class="w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 mr-2 sm:mr-3 md:mr-5" />
        <span class="font-bold text-xl sm:text-2xl md:text-3xl">Toolhunt</span>
      </NuxtLink>
    </div>
    <div class="flex-none">
      <ul class="menu menu-horizontal px-1 hidden lg:flex">
        <li v-for="item in menuItems" :key="item.to">
          <NuxtLink :to="item.to" class="btn btn-ghost text-lg">{{ item.label }}</NuxtLink>
        </li>
      </ul>
      <a @click="handleAuthAction" class="btn btn-md ml-3 hidden lg:flex text-lg"
         :class="isLoggedIn ? 'bg-transparent border-primary/70 text-primary hover:bg-primary/10 hover:border-primary' : 'btn-primary'">
        {{ isLoggedIn ? 'Logout' : 'Login' }}
      </a>
      <div class="dropdown dropdown-end lg:hidden ml-auto">
        <label tabindex="0" class="btn btn-ghost lg:hidden">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-6 h-6 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
        </label>
        <ul tabindex="0" class="menu menu-lg dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
          <li v-for="item in menuItems" :key="item.to">
            <NuxtLink :to="item.to" class="text-lg">{{ item.label }}</NuxtLink>
          </li>
          <li>
            <a @click="handleAuthAction" class="text-primary text-lg">
              {{ isLoggedIn ? 'Logout' : 'Login' }}
            </a>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
