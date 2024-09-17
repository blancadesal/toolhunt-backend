<script setup>
const { tasks, fieldNames, annotationsSchema, fetchTasks, fetchFieldNames, fetchAnnotationsSchema } = useToolhuntApi();

const searchQuery = ref('');
const selectedFields = ref([]);
const isLoading = ref(true);
const taskCardRef = ref(null);

const searchTools = () => {
  // Implement search functionality
};

const applyFieldFilter = async (filters) => {
  selectedFields.value = filters;
  isLoading.value = true;
  await fetchTasks(null, filters.length > 0 ? filters.join(',') : null);
  isLoading.value = false;
};

const clearFilters = async () => {
  selectedFields.value = [];
  isLoading.value = true;
  await fetchTasks();
  isLoading.value = false;
};

const loadNewBatch = async () => {
  isLoading.value = true;
  tasks.value = [];
  if (taskCardRef.value) {
    taskCardRef.value.resetSubmittedTasks();
  }
  await fetchTasks(null, selectedFields.value.length > 0 ? selectedFields.value.join(',') : null);
  isLoading.value = false;
};

onMounted(async () => {
  isLoading.value = true;
  await fetchTasks();
  await fetchFieldNames();
  await fetchAnnotationsSchema();
  isLoading.value = false;
});
</script>

<template>
  <div class="flex flex-col min-h-screen items-center p-4">
    <h1 class="text-4xl font-bold mt-4 mb-4">Welcome to Toolhunt!</h1>
    <div class="w-full max-w-3xl mb-4 mt-4">
      <div class="relative">
        <input v-model="searchQuery" type="text" placeholder="Search for a tool" class="input input-bordered w-full pr-10" />
        <button @click="searchTools" class="absolute right-2 top-1/2 transform -translate-y-1/2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
        </button>
      </div>
    </div>

    <FieldFilter
      :field-names="fieldNames"
      v-model="selectedFields"
      @apply-filter="applyFieldFilter"
      @clear-filters="clearFilters"
    />

    <div v-if="isLoading" class="text-center mt-8">
      <p class="text-xl">Loading tasks...</p>
    </div>

    <div v-else-if="tasks.length === 0" class="text-center mt-8">
      <p class="text-xl">No tasks available. Try clearing filters or refreshing the page.</p>
    </div>

    <TaskCard
      v-else-if="tasks.length > 0"
      ref="taskCardRef"
      :tasks="tasks"
      :annotations-schema="annotationsSchema"
      @load-new-batch="loadNewBatch"
    />
  </div>
</template>
