<script setup>
const { contributions, fetchContributions } = useToolhuntApi()

const topHuntersLastMonth = ref([])
const allTimeGreats = ref([])
const loading = ref(true)

const getContributions = async (days = undefined, limit = undefined) => {
  const params = {}
  if (days !== undefined) params.days = days
  if (limit !== undefined) params.limit = limit
  await fetchContributions(params)
  return contributions.value?.contributions || []
}

onMounted(async () => {
  loading.value = true
  try {
    topHuntersLastMonth.value = await getContributions(30, 5) // Top 5 for last 30 days
    allTimeGreats.value = await getContributions(undefined, 10) // Top 10 all-time
  }
  finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="flex flex-col min-h-screen py-12">
    <div class="container mx-auto px-4 max-w-5xl">
      <h1 class="text-3xl font-bold mb-8 text-center">
        Toolhunt Leaderboard
      </h1>

      <div
        v-if="loading"
        class="flex justify-center"
      >
        <span class="loading loading-spinner loading-lg" />
      </div>
      <div v-else>
        <!-- Top Hunters from the Last 30 Days -->
        <div class="mb-8">
          <LeaderboardTable
            :users="topHuntersLastMonth"
            title="Top Hunters from the Last 30 Days"
            subtitle="Rising stars illuminating the vast toolscape"
          />
        </div>

        <!-- All Time Greats -->
        <div>
          <LeaderboardTable
            :users="allTimeGreats"
            title="All Time Greats"
            subtitle="Legendary contributors to the Toolhunt community"
          />
        </div>
      </div>
    </div>
  </div>
</template>
