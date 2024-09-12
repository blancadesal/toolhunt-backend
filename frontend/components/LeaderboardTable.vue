<template>
  <div class="overflow-x-auto bg-base-100 rounded-lg shadow-lg">
    <table class="table w-full">
      <thead>
        <tr>
          <th class="bg-base-200 text-base-content text-lg font-semibold">Rank</th>
          <th class="bg-base-200 text-base-content text-lg font-semibold">Username</th>
          <th class="bg-base-200 text-base-content text-lg font-semibold text-right">Contributions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.rank" class="hover:bg-base-200 transition-colors duration-200">
          <td class="font-bold text-xl text-accent">{{ user.rank }}</td>
          <td class="font-medium text-lg">{{ user.username }}</td>
          <td class="text-right font-semibold text-lg">{{ user.contributions }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  users: {
    type: Array,
    required: true
  }
})
</script>
