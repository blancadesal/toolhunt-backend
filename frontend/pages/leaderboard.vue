<template>
  <div class="min-h-screen bg-base-200 py-8">
    <div class="container mx-auto px-4">
      <h1 class="text-3xl font-bold mb-6">Toolhunt Leaderboard</h1>
      
      <!-- Top Hunters from the Last 30 Days -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold mb-2">Top Hunters from the Last 30 Days</h2>
        <p class="text-gray-600 mb-4">Rising stars illuminating the vast toolscape</p>
        <LeaderboardTable :users="topHuntersLastMonth" />
      </div>
      
      <!-- All Time Greats -->
      <div>
        <h2 class="text-2xl font-bold mb-2">All Time Greats</h2>
        <p class="text-gray-600 mb-4">Legendary contributors to the Toolhunt community</p>
        <LeaderboardTable :users="allTimeGreats" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import LeaderboardTable from '@/components/LeaderboardTable.vue'

// Fun mock data for Top Hunters from the Last 30 Days
const topHuntersLastMonth = ref([
  { rank: 1, username: 'RisingStarDev', contributions: 75 },
  { rank: 2, username: 'NewCodeWhiz', contributions: 68 },
  { rank: 3, username: 'FreshByteMaster', contributions: 62 },
  { rank: 4, username: 'SprintCoder', contributions: 55 },
  { rank: 5, username: 'QuickLearnPro', contributions: 49 },
])

// Fun mock data for All Time Greats
const allTimeGreats = ref([
  { rank: 1, username: 'CodeNinja42', contributions: 1250 },
  { rank: 2, username: 'BugSlayer99', contributions: 1120 },
  { rank: 3, username: 'PixelWizard', contributions: 980 },
  { rank: 4, username: 'SyntaxSorcerer', contributions: 925 },
  { rank: 5, username: 'DevDragon', contributions: 870 },
])

// You can replace this with actual data fetching logic when ready
// const fetchLeaderboardData = async () => {
//   try {
//     const response = await fetch('your-api-endpoint-for-leaderboard')
//     const data = await response.json()
//     topHuntersLastMonth.value = data.topHuntersLastMonth
//     allTimeGreats.value = data.allTimeGreats
//   } catch (error) {
//     console.error('Error fetching leaderboard data:', error)
//   }
// }

// onMounted(() => {
//   fetchLeaderboardData()
// })
</script>
