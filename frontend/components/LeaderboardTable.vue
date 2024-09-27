<script setup>
defineProps({
  users: {
    type: Array,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    required: true,
  },
})
</script>

<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="bg-secondary text-secondary-content p-4 pl-10 rounded-t-xl">
      <h2 class="text-2xl font-bold">
        {{ title }}
      </h2>
    </div>
    <div class="card-body pt-4">
      <p class="text-base-content/70 mb-6">
        {{ subtitle }}
      </p>
      <div class="overflow-x-auto">
        <table class="table w-full">
          <thead>
            <tr class="bg-base-200 text-base-content">
              <th>Rank</th>
              <th>Username</th>
              <th class="text-right">
                Contributions
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="user in users"
              :key="user.rank"
            >
              <td class="font-bold text-xl text-accent">
                {{ user.rank }}
              </td>
              <td class="font-medium text-lg">
                {{ user.username }}
              </td>
              <td class="text-right font-semibold text-lg">
                {{ user.contributions }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
