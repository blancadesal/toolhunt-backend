<template>
  <nav class="top-menu-bar">
    <div class="logo">Your App Name</div>
    <div class="spacer"></div>
    <button @click="login" class="login-button">Login</button>
  </nav>
</template>

<script setup lang="ts">
const login = async () => {
  try {
    console.log('Attempting to fetch from:', '/login');
    const response = await fetch('/login', {
      method: 'GET',
      credentials: 'include',
      redirect: 'manual',
    });
    
    console.log('Response status:', response.status);
    console.log('Response headers:', response.headers);

    if (response.status === 307) {
      const redirectUrl = response.headers.get('Location');
      if (redirectUrl) {
        console.log('Redirect URL:', redirectUrl);
        window.location.href = redirectUrl;
      } else {
        console.error('No redirect URL found');
      }
    } else if (response.status === 0) {
      console.error('Network error: No response from server. Check if the server is running and accessible.');
    } else {
      console.error('Unexpected response:', response.status);
      const text = await response.text();
      console.error('Response text:', text);
    }
  } catch (error) {
    console.error('Error during login:', error);
  }
};
</script>

<style scoped>
.top-menu-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #f0f0f0;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
}

.spacer {
  flex-grow: 1;
}

.login-button {
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.login-button:hover {
  background-color: #0056b3;
}
</style>
