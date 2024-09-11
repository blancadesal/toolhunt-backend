<template>
  <div class="min-h-screen bg-base-200 py-8">
    <div class="container mx-auto px-4">
      <h1 class="text-3xl font-bold mb-2">Toolhunt Leaderboard</h1>
      <p class="text-gray-600 mb-6">Top contributors to the Toolhunt community</p>
      
      <div class="bg-base-100 shadow-xl rounded-box overflow-x-auto">
        <table class="table w-full">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Username</th>
              <th>Score</th>
              <th>Contributions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in leaderboardData" :key="user.rank">
              <th>{{ user.rank }}</th>
              <td>{{ user.username }}</td>
              <td>{{ user.score }}</td>
              <td>{{ user.contributions }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'

const leaderboardData = ref([
  { rank: 1, username: 'TechWizard', score: 1250, contributions: 42 },
  { rank: 2, username: 'CodeNinja', score: 1100, contributions: 38 },
  { rank: 3, username: 'BugSlayer', score: 950, contributions: 35 },
  { rank: 4, username: 'AlgorithmAce', score: 800, contributions: 30 },
  { rank: 5, username: 'DataDiva', score: 750, contributions: 28 },
  { rank: 6, username: 'CloudMaster', score: 700, contributions: 25 },
  { rank: 7, username: 'SecurityGuru', score: 650, contributions: 22 },
  { rank: 8, username: 'UIUnicorn', score: 600, contributions: 20 },
  { rank: 9, username: 'DevOpsHero', score: 550, contributions: 18 },
  { rank: 10, username: 'AIInnovator', score: 500, contributions: 15 },
])
</script>
