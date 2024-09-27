<script setup>
const { isLoggedIn, logout, login } = useAuth()
const router = useRouter()

const menuItems = [
  { to: '/leaderboard', label: 'Leaderboard' },
  { to: '/profile', label: 'Profile' },
  { to: '/about', label: 'About' },
]

const handleAuthAction = async () => {
  if (isLoggedIn.value) {
    await logout()
    router.go(0)
  }
  else {
    const loginUrl = await login()
    if (loginUrl) window.location.href = loginUrl
  }
}
</script>

<template>
  <div class="navbar bg-base-100 shadow-lg text-base py-2 sm:py-3 px-3 sm:px-4">
    <div class="flex-1">
      <NuxtLink
        to="/"
        class="flex items-center hover:opacity-80 transition-opacity duration-200"
      >
        <img
          src="@/assets/logo-main.svg"
          alt="Toolhunt Logo"
          class="w-9 h-9 sm:w-11 sm:h-11 mr-2 sm:mr-3"
        >
        <span class="font-bold text-xl sm:text-2xl">Toolhunt</span>
      </NuxtLink>
    </div>
    <div class="flex-none">
      <ul class="menu menu-horizontal px-1 hidden lg:flex">
        <li
          v-for="item in menuItems"
          :key="item.to"
        >
          <NuxtLink
            :to="item.to"
            class="btn btn-ghost text-base sm:text-lg"
          >
            {{ item.label }}
          </NuxtLink>
        </li>
      </ul>
      <a
        class="btn btn-md ml-3 hidden lg:flex text-base sm:text-lg"
        :class="isLoggedIn ? 'bg-transparent border-primary/70 text-primary hover:bg-primary/10 hover:border-primary' : 'btn-primary'"
        @click="handleAuthAction"
      >
        {{ isLoggedIn ? 'Logout' : 'Login' }}
      </a>
      <div class="dropdown dropdown-end lg:hidden ml-auto">
        <label
          tabindex="0"
          class="btn btn-ghost lg:hidden"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            class="inline-block w-6 h-6 stroke-current"
          ><path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 6h16M4 12h16M4 18h16"
          /></svg>
        </label>
        <ul
          tabindex="0"
          class="menu menu-md dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52"
        >
          <li
            v-for="item in menuItems"
            :key="item.to"
          >
            <NuxtLink
              :to="item.to"
              class="text-base sm:text-lg"
            >
              {{ item.label }}
            </NuxtLink>
          </li>
          <li>
            <a
              class="text-primary text-base sm:text-lg"
              @click="handleAuthAction"
            >
              {{ isLoggedIn ? 'Logout' : 'Login' }}
            </a>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
