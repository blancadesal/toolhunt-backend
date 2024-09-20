<template>
	<div data-theme="emerald" class="flex flex-col min-h-screen bg-gradient-to-b from-blue-100 to-base-300">
		<TopMenuBar class="flex-shrink-0" />
		<div class="flex-grow">
			<NuxtPage />
		</div>
		<footer class="footer footer-center bg-primary text-primary-content p-2 flex-shrink-0">
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