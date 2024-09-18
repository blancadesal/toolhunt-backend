<script setup>
const { authState, isLoggedIn, fetchUserData } = useAuth()
const { userContributions, fetchUserContributions, error: contributionsError } = useToolhuntApi()
const loadingContributions = ref(false)

// Pagination
const currentPage = ref(1)
const itemsPerPage = 10

const paginatedContributions = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return userContributions.value.contributions.slice(start, end)
})

const totalPages = computed(() => 
  Math.ceil(userContributions.value.contributions.length / itemsPerPage)
)

const changePage = (newPage) => {
  if (newPage >= 1 && newPage <= totalPages.value) {
    currentPage.value = newPage
  }
}

const pageRange = computed(() => {
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
})

const fetchContributions = async () => {
  if (!isLoggedIn.value || !authState.value?.user?.username) return

  loadingContributions.value = true
  try {
    await fetchUserContributions(authState.value.user.username)
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
    <div class="container mx-auto px-4 max-w-5xl">
      <div v-if="authState.loading" class="flex justify-center">
        <span class="loading loading-spinner loading-lg"></span>
      </div>
      <div v-else-if="isLoggedIn">
        <h2 class="text-3xl font-bold mb-8 text-center text-accent">Welcome, {{ authState.user.username }}!</h2>
      </div>
      <div v-else class="alert alert-warning mb-8">
        Please log in to view your profile.
      </div>

      <!-- Latest Activity Section -->
      <div v-if="isLoggedIn" class="card bg-base-100 shadow-xl">
        <div class="bg-secondary text-secondary-content p-4 pl-10 rounded-t-xl">
          <h2 class="text-2xl font-bold">Latest Activity</h2>
        </div>
        <div class="card-body pt-4">
          <div v-if="loadingContributions" class="flex justify-center">
            <span class="loading loading-spinner loading-lg"></span>
          </div>
          <div v-else-if="contributionsError" class="alert alert-error">
            {{ contributionsError }}
          </div>
          <div v-else-if="userContributions.contributions.length > 0" class="overflow-x-auto">
            <table class="table w-full mb-4">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Tool Name</th>
                  <th>Annotation</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="contribution in paginatedContributions" :key="contribution.date">
                  <td>{{ formatDate(contribution.date) }}</td>
                  <td>{{ contribution.tool_title }}</td>
                  <td>{{ toHumanReadable(contribution.field) }}</td>
                </tr>
              </tbody>
            </table>
            <!-- Simplified Pagination controls -->
            <div class="flex justify-center items-center mt-4 space-x-2">
              <button 
                class="btn btn-sm btn-outline btn-secondary" 
                @click="changePage(1)" 
                :disabled="currentPage === 1"
              >
                First
              </button>
              <button 
                class="btn btn-sm btn-outline btn-secondary" 
                @click="changePage(currentPage - 1)" 
                :disabled="currentPage === 1"
              >
                &lt;
              </button>
              <button 
                v-for="page in pageRange" 
                :key="page" 
                @click="changePage(page)" 
                class="btn btn-sm btn-outline btn-secondary" 
                :class="{ 'btn-active': page === currentPage }"
              >
                {{ page }}
              </button>
              <button 
                class="btn btn-sm btn-outline btn-secondary" 
                @click="changePage(currentPage + 1)" 
                :disabled="currentPage === totalPages"
              >
                &gt;
              </button>
              <button 
                class="btn btn-sm btn-outline btn-secondary" 
                @click="changePage(totalPages)" 
                :disabled="currentPage === totalPages"
              >
                Last
              </button>
            </div>
          </div>
          <div v-else class="text-center text-base-content/70">
            No activity found. Start contributing to see your activity here!
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
