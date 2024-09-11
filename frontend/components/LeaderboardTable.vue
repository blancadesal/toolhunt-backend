<template>
  <div class="bg-base-100 shadow-xl rounded-box overflow-x-auto">
    <table class="table w-full">
      <thead>
        <tr>
          <th>Rank</th>
          <th>Username</th>
          <th>Contributions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.rank">
          <th>{{ user.rank }}</th>
          <td>{{ user.username }}</td>
          <td>{{ user.contributions }}</td>
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
