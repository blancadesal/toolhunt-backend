// services/api.ts
const API_BASE_URL = 'http://localhost:8082'; // Your FastAPI backend URL

export const api = {
  async getLoginUrl() {
    const response = await fetch(`${API_BASE_URL}/login`);
    if (!response.ok) {
      throw new Error('Failed to get login URL');
    }
    const data = await response.json();
    return data.login_url;
  },

  async getUser() {
    const response = await fetch(`${API_BASE_URL}/api/v1/user`, {
      credentials: 'include',
    });
    if (!response.ok) {
      throw new Error('Failed to get user data');
    }
    return response.json();
  }
};
