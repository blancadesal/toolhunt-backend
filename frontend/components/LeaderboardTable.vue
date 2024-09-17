<script setup>
defineProps({
  users: {
    type: Array,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    required: true
  }
})
</script>

<template>
  <div>
    <h2 class="text-3xl font-semibold mb-4 text-base-content">{{ title }}</h2>
    <p class="text-base-content/70 mb-6">{{ subtitle }}</p>
    <div class="overflow-x-auto bg-base-100 rounded-lg shadow-lg">
      <table class="table w-full">
        <thead>
          <tr class="bg-base-200 text-base-content text-lg font-semibold">
            <th>Rank</th>
            <th>Username</th>
            <th class="text-right">Contributions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.rank">
            <td class="font-bold text-xl text-accent">{{ user.rank }}</td>
            <td class="font-medium text-lg">{{ user.username }}</td>
            <td class="text-right font-semibold text-lg">{{ user.contributions }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
