<template>
  <div data-theme="emerald">
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
