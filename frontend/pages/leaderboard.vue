<script setup>
const { contributions, fetchContributions } = useToolhuntApi()

const topHuntersLastMonth = ref([])
const allTimeGreats = ref([])

const getContributions = async (days = undefined, limit = undefined) => {
  const params = {}
  if (days !== undefined) params.days = days
  if (limit !== undefined) params.limit = limit
  await fetchContributions(params)
  return contributions.value?.contributions || []
}

onMounted(async () => {
  topHuntersLastMonth.value = await getContributions(30, 5)  // Top 5 for last 30 days
  allTimeGreats.value = await getContributions(undefined, 10)  // Top 10 all-time
})
</script>

<template>
  <div class="flex flex-col min-h-screen py-12">
    <div class="container mx-auto px-4">
      <h1 class="text-4xl font-bold mb-12 text-center text-secondary text-base-content">Toolhunt Leaderboard</h1>

      <!-- Top Hunters from the Last 30 Days -->
      <div class="mb-16">
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
</template>
