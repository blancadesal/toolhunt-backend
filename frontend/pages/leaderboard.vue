<script setup>
import { ref, onMounted } from 'vue';
import { toolhuntApi } from '@/utils/ToolhuntApiClient';

const topHuntersLastMonth = ref([]);
const allTimeGreats = ref([]);

const fetchContributions = async (days = undefined) => {
  try {
    const response = await toolhuntApi.fetchContributions(days);
    return response.contributions;
  } catch (error) {
    console.error('Error fetching contributions:', error);
    return [];
  }
};

onMounted(async () => {
  topHuntersLastMonth.value = await fetchContributions(30);
  allTimeGreats.value = await fetchContributions();
});
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
