<template>
  <div data-theme="emerald" class="bg-gradient-to-b from-blue-100 to-base-300">
    <TopMenuBar />
    <NuxtPage />
    <footer class="footer footer-center bg-primary text-primary-content p-2">
      <aside>
        <p>Copyright © {{ new Date().getFullYear() }} - All rights reserved by Toolhunters Inc.</p>
      </aside>
    </footer>
  </div>
</template>

<script setup>
const { fetchUserData } = useAuth();

onMounted(() => {
  fetchUserData();
});
</script>
