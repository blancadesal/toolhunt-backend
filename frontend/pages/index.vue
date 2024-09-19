<script setup>
import { ref, onMounted } from 'vue'
import FieldFilter from '@/components/FieldFilter.vue'
import ToolFilter from '@/components/ToolFilter.vue'
import TaskCard from '@/components/TaskCard.vue'

const { tasks, fieldNames, annotationsSchema, fetchTasks, fetchFieldNames, fetchAnnotationsSchema } = useToolhuntApi()

const currentTaskIndex = ref(0)
const isLoading = ref(true)
const taskCardRef = ref(null)

const activeFilters = ref({
  fields: [],
  tools: []
})

// Hardcoded tool data
const toolData = {
  "all_titles": [
    "Testy McFull-Tool",
    "Testy McTest-Tool",
    "Testy McTool-Type"
  ],
  "titles": {
    "Testy McFull-Tool": "testy-mc-full-tool",
    "Testy McTest-Tool": "testy-mc-test-tool",
    "Testy McTool-Type": "testy-mc-tool-type"
  }
}

const loadNewBatch = async () => {
  isLoading.value = true
  tasks.value = []
  currentTaskIndex.value = 0
  if (taskCardRef.value) {
    taskCardRef.value.resetSubmittedTasks()
  }
  
  let toolFilter = activeFilters.value.tools.length > 0 ? activeFilters.value.tools.map(tool => toolData.titles[tool]).join(',') : null
  let fieldFilter = activeFilters.value.fields.length > 0 ? activeFilters.value.fields.join(',') : null

  await fetchTasks(toolFilter, fieldFilter)
  isLoading.value = false
}

const updateActiveFilters = (type, filters) => {
  activeFilters.value[type] = filters
  loadNewBatch()
}

const removeActiveFilter = (type, filter) => {
  activeFilters.value[type] = activeFilters.value[type].filter(f => f !== filter)
  loadNewBatch()
}

const clearAllFilters = () => {
  activeFilters.value = { fields: [], tools: [] }
  loadNewBatch()
}

onMounted(async () => {
  isLoading.value = true
  await fetchTasks()
  await fetchFieldNames()
  await fetchAnnotationsSchema()
  isLoading.value = false
})
</script>

<template>
  <div class="flex flex-col min-h-screen items-center p-4">
    <h1 class="text-4xl font-bold mt-4 mb-8">Welcome to Toolhunt!</h1>
    
    <div class="w-full max-w-7xl mb-8">
      <div class="flex flex-col lg:flex-row gap-6 justify-center">
        <!-- Field Filter -->
        <FieldFilter
          :field-names="fieldNames"
          :active-fields="activeFilters.fields"
          @update-filters="filters => updateActiveFilters('fields', filters)"
          class="w-full lg:w-1/2"
        />

        <!-- Tool Filter -->
        <ToolFilter
          :tools="toolData.all_titles"
          :active-tools="activeFilters.tools"
          @update-filters="filters => updateActiveFilters('tools', filters)"
          class="w-full lg:w-1/2"
        />
      </div>

      <!-- Active Filters Display -->
      <div v-if="activeFilters.fields.length > 0 || activeFilters.tools.length > 0" class="mt-6">
        <h2 class="text-lg font-semibold mb-2 text-secondary">Active Filters:</h2>
        <div class="flex flex-wrap gap-2 mb-2">
          <div v-for="field in activeFilters.fields" :key="field" class="badge badge-primary badge-lg">
            Task: {{ toHumanReadable(field) }}
            <button @click="removeActiveFilter('fields', field)" class="ml-2 text-xs">✕</button>
          </div>
          <div v-for="tool in activeFilters.tools" :key="tool" class="badge badge-secondary badge-lg">
            Tool: {{ tool }}
            <button @click="removeActiveFilter('tools', tool)" class="ml-2 text-xs">✕</button>
          </div>
        </div>
        <button @click="clearAllFilters" class="btn btn-outline btn-sm mt-2">Clear All Filters</button>
      </div>
    </div>

    <div v-if="isLoading" class="text-center mt-8">
      <p class="text-xl">Loading tasks...</p>
    </div>

    <div v-else-if="tasks.length === 0" class="text-center mt-8">
      <p class="text-xl">No tasks available. Try clearing filters or refreshing the page.</p>
    </div>

    <TaskCard
      v-else
      ref="taskCardRef"
      :tasks="tasks"
      :current-task-index="currentTaskIndex"
      :annotations-schema="annotationsSchema"
      @update:current-task-index="currentTaskIndex = $event"
      @load-new-batch="loadNewBatch"
      class="w-full max-w-7xl"
    />
  </div>
</template>