<template>
  <div class="flex flex-col min-h-screen py-12">
    <div class="container mx-auto px-4">
      <h1 class="text-4xl font-bold mb-12 text-center text-secondary text-base-content">Toolhunt Leaderboard</h1>

      <!-- Top Hunters from the Last 30 Days -->
      <div class="mb-16">
        <h2 class="text-3xl font-semibold mb-4 text-base-content">Top Hunters from the Last 30 Days</h2>
        <p class="text-base-content/70 mb-6">Rising stars illuminating the vast toolscape</p>
        <LeaderboardTable :users="topHuntersLastMonth" />
      </div>

      <!-- All Time Greats -->
      <div>
        <h2 class="text-3xl font-semibold mb-4 text-base-content">All Time Greats</h2>
        <p class="text-base-content/70 mb-6">Legendary contributors to the Toolhunt community</p>
        <LeaderboardTable :users="allTimeGreats" />
      </div>
    </div>
  </div>
</template>

<script setup>
const topHuntersLastMonth = ref([
  { rank: 1, username: 'RisingStarDev', contributions: 75 },
  { rank: 2, username: 'NewCodeWhiz', contributions: 68 },
  { rank: 3, username: 'FreshByteMaster', contributions: 62 },
  { rank: 4, username: 'SprintCoder', contributions: 55 },
  { rank: 5, username: 'QuickLearnPro', contributions: 49 },
])

const allTimeGreats = ref([
  { rank: 1, username: 'CodeNinja42', contributions: 1250 },
  { rank: 2, username: 'BugSlayer99', contributions: 1120 },
  { rank: 3, username: 'PixelWizard', contributions: 980 },
  { rank: 4, username: 'SyntaxSorcerer', contributions: 925 },
  { rank: 5, username: 'DevDragon', contributions: 870 },
])
</script>
