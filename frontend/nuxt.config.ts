// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },
  ssr: false,  // Disable server-side rendering for simplicity in this OAuth flow
  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8082'  // Your FastAPI backend URL
    }
  },
})
