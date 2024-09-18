<script setup>
const { authState, isLoggedIn, fetchUserData } = useAuth()
const { userContributions, fetchUserContributions, error: contributionsError } = useToolhuntApi()
const loadingContributions = ref(false)

const fetchContributions = async () => {
  if (!isLoggedIn.value || !authState.value?.user?.username) return

  loadingContributions.value = true
  try {
    await fetchUserContributions(authState.value.user.username, 10) // Fetch last 10 contributions
  } finally {
    loadingContributions.value = false
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

onMounted(async () => {
  await fetchUserData()
  await fetchContributions()
})
</script>

<template>
  <div class="flex flex-col min-h-screen py-12">
    <div class="container mx-auto px-4 max-w-3xl">
      <h1 class="text-4xl font-bold mb-8 text-center text-secondary">Profile</h1>
      <div v-if="authState.loading" class="flex justify-center">
        <span class="loading loading-spinner loading-lg"></span>
      </div>
      <div v-else-if="isLoggedIn" class="card bg-base-100 shadow-xl mb-12">
        <div class="card-body">
          <h2 class="card-title text-2xl">{{ authState.user.username }}</h2>
          <p class="text-base-content/70">{{ authState.user.email }}</p>
        </div>
      </div>
      <div v-else class="alert alert-warning mb-8">
        Please log in to view your profile.
      </div>

      <!-- Latest Activity Section -->
      <div v-if="isLoggedIn" class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title text-2xl mb-4">Latest Activity</h2>
          <div v-if="loadingContributions" class="flex justify-center">
            <span class="loading loading-spinner loading-lg"></span>
          </div>
          <div v-else-if="contributionsError" class="alert alert-error">
            {{ contributionsError }}
          </div>
          <div v-else-if="userContributions.contributions.length > 0" class="overflow-x-auto">
            <table class="table w-full">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Tool Name</th>
                  <th>Annotation</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="contribution in userContributions.contributions" :key="contribution.date">
                  <td>{{ formatDate(contribution.date) }}</td>
                  <td>{{ contribution.tool_title }}</td>
                  <td>{{ toHumanReadable(contribution.field) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="text-center text-base-content/70">
            No activity found. Start contributing to see your activity here!
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
