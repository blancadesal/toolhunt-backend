<script setup>
import { ref } from 'vue'

// Mock data for the leaderboard
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

<template>
  <div class="leaderboard">
    <h1>Toolhunt Leaderboard</h1>
    <p>Top contributors to the Toolhunt community</p>
    
    <table>
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
          <td>{{ user.rank }}</td>
          <td>{{ user.username }}</td>
          <td>{{ user.score }}</td>
          <td>{{ user.contributions }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.leaderboard {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  color: #333;
  margin-bottom: 0.5rem;
}

p {
  color: #666;
  margin-bottom: 2rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

th, td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f2f2f2;
  font-weight: bold;
  color: #333;
}

tr:nth-child(even) {
  background-color: #f8f8f8;
}

tr:hover {
  background-color: #e8e8e8;
}
</style>
