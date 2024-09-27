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
  const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }
  return new Date(dateString).toLocaleString(undefined, options)
}

// Add this computed property to get the total contributions
const totalContributions = computed(() => userContributions.value.total_contributions || 0)

onMounted(async () => {
  await fetchUserData()
  await fetchContributions()
})
</script>

<template>
  <div class="flex flex-col min-h-screen py-12">
    <div class="container mx-auto px-4 sm:max-w-5xl">
      <div v-if="loadingContributions" class="flex justify-center">
        <span class="loading loading-spinner loading-lg"/>
      </div>
      <div v-else>
        <div v-if="isLoggedIn">
          <!-- Welcome and Total Contributions Section -->
          <div class="text-center mb-8">
            <h2 class="text-3xl font-bold mb-2">Welcome, <span class="text-accent">{{ authState.user.username }}</span>!</h2>
            <p class="text-lg">
              Total Contributions: <span class="font-bold text-accent">{{ totalContributions }}</span>
            </p>
          </div>

          <!-- Latest Activity Section -->
          <div class="card bg-base-100 shadow-xl">
            <div class="bg-secondary text-secondary-content p-4 pl-6 sm:pl-10 rounded-t-xl">
              <h2 class="text-2xl font-bold">Latest Activity</h2>
            </div>
            <div class="card-body pt-4 px-2 sm:px-6">
              <div v-if="loadingContributions" class="flex justify-center">
                <span class="loading loading-spinner loading-lg"/>
              </div>
              <div v-else-if="contributionsError" class="alert alert-error">
                {{ contributionsError }}
              </div>
              <div v-else-if="userContributions.contributions.length > 0" class="overflow-x-auto">
                <table class="table w-full mb-6">
                  <thead>
                    <tr>
                      <th class="px-2 sm:px-4">Date</th>
                      <th class="px-2 sm:px-4">Tool Name</th>
                      <th class="px-2 sm:px-4">Annotation</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="contribution in paginatedContributions" :key="contribution.date">
                      <td class="px-2 sm:px-4 text-xs sm:text-sm">{{ formatDate(contribution.date) }}</td>
                      <td class="px-2 sm:px-4 text-xs sm:text-sm">{{ contribution.tool_title }}</td>
                      <td class="px-2 sm:px-4 text-xs sm:text-sm">{{ toHumanReadable(contribution.field) }}</td>
                    </tr>
                  </tbody>
                </table>
                <!-- Refined Responsive Pagination controls -->
                <div class="flex flex-wrap justify-center items-center mt-6 mb-4 space-y-2">
                  <!-- Mobile view -->
                  <div class="flex items-center space-x-3 sm:hidden w-full justify-center">
                    <button
                      class="btn btn-xs btn-outline btn-secondary px-2"
                      :disabled="currentPage === 1"
                      @click="changePage(currentPage - 1)"
                    >
                      &lt;
                    </button>
                    <span class="text-sm">Page {{ currentPage }} of {{ totalPages }}</span>
                    <button
                      class="btn btn-xs btn-outline btn-secondary px-2"
                      :disabled="currentPage === totalPages"
                      @click="changePage(currentPage + 1)"
                    >
                      &gt;
                    </button>
                  </div>
                  <!-- Desktop view -->
                  <div class="hidden sm:flex items-center space-x-1">
                    <button
                      class="btn btn-xs btn-outline btn-secondary px-2"
                      :disabled="currentPage === 1"
                      @click="changePage(1)"
                    >
                      First
                    </button>
                    <button
                      class="btn btn-xs btn-outline btn-secondary px-2"
                      :disabled="currentPage === 1"
                      @click="changePage(currentPage - 1)"
                    >
                      &lt;
                    </button>
                    <button
                      v-for="page in pageRange"
                      :key="page"
                      class="btn btn-xs btn-outline btn-secondary px-2"
                      :class="{ 'btn-active': page === currentPage }"
                      @click="changePage(page)"
                    >
                      {{ page }}
                    </button>
                    <button
                      class="btn btn-xs btn-outline btn-secondary px-2"
                      :disabled="currentPage === totalPages"
                      @click="changePage(currentPage + 1)"
                    >
                      &gt;
                    </button>
                    <button
                      class="btn btn-xs btn-outline btn-secondary px-2"
                      :disabled="currentPage === totalPages"
                      @click="changePage(totalPages)"
                    >
                      Last
                    </button>
                  </div>
                </div>
              </div>
              <div v-else class="text-center text-base-content/70">
                No activity found. Start contributing to see your activity here!
              </div>
            </div>
          </div>
        </div>
        <div v-else class="alert alert-warning mb-8">
          Please log in to view your profile.
        </div>
      </div>
    </div>
  </div>
</template>
