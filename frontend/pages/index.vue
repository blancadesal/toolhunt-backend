<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import FieldFilter from '@/components/FieldFilter.vue'
import ToolFilter from '@/components/ToolFilter.vue'
import TaskCard from '@/components/TaskCard.vue'

const { tasks, fieldNames, annotationsSchema, toolNames, fetchTasks, fetchFieldNames, fetchAnnotationsSchema, fetchToolNames } = useToolhuntApi()

const currentTaskIndex = ref(0)
const isLoading = ref(true)
const taskCardRef = ref(null)

const activeFilters = ref({
  fields: [],
  tools: []
})

// Remove the hardcoded toolData

const loadNewBatch = async () => {
  // Capture current scroll position
  const scrollPosition = window.scrollY

  isLoading.value = true
  // Remove the line that clears tasks to prevent DOM reflow
  // tasks.value = []
  currentTaskIndex.value = 0
  if (taskCardRef.value) {
    taskCardRef.value.resetSubmittedTasks()
  }

  let toolFilter = activeFilters.value.tools.length > 0
    ? activeFilters.value.tools.map(tool => toolNames.value?.titles[tool] || '').join(',')
    : null
  let fieldFilter = activeFilters.value.fields.length > 0
    ? activeFilters.value.fields.join(',')
    : null

  await fetchTasks(toolFilter, fieldFilter)
  isLoading.value = false

  // Use nextTick to ensure DOM updates are applied before scrolling
  await nextTick()
  window.scrollTo({ top: scrollPosition, behavior: 'smooth' })
}

const updateActiveFilters = (type, filters) => {
  activeFilters.value[type] = filters
  loadNewBatch()
}

const removeActiveFilter = (type, filter) => {
  activeFilters.value[type] = activeFilters.value[type].filter(f => f !== filter)
  loadNewBatch()
}

const clearAllFilters = () => { // Removed event parameter if not needed
  activeFilters.value = { fields: [], tools: [] }
  loadNewBatch()

  // Smooth scroll to top if needed
  if (window.scrollY > 0) {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const hasActiveFilters = computed(() => {
  return activeFilters.value.fields.length > 0 || activeFilters.value.tools.length > 0
})

onMounted(async () => {
  isLoading.value = true
  await Promise.all([
    fetchTasks(),
    fetchFieldNames(),
    fetchAnnotationsSchema(),
    fetchToolNames()
  ])
  isLoading.value = false
})
</script>

<template>
  <div class="flex flex-col min-h-screen items-center p-4">
    <h1 class="text-4xl font-bold mt-4 mb-8">Welcome to Toolhunt!</h1>

    <div class="w-full max-w-7xl mb-8">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Field Filter -->
        <div class="flex flex-col h-full">
          <FieldFilter
            :field-names="fieldNames"
            :active-fields="activeFilters.fields"
            @update-filters="filters => updateActiveFilters('fields', filters)"
            class="flex-grow"
          />
        </div>

        <!-- Tool Filter -->
        <div class="flex flex-col h-full">
          <ToolFilter
            :tools="toolNames?.all_titles || []"
            :active-tools="activeFilters.tools"
            @update-filters="filters => updateActiveFilters('tools', filters)"
            class="flex-grow"
          />
        </div>
      </div>

      <!-- Active Filters Display -->
      <div class="mt-6 p-4 bg-base-200 rounded-lg shadow-md min-h-[100px] transition-all duration-300">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold text-secondary">Active Filters</h2>
          <button
            type="button"
            @click="clearAllFilters"
            class="btn btn-secondary btn-sm"
            :disabled="!hasActiveFilters"
          >
            Clear All Filters
          </button>
        </div>
        <div v-if="hasActiveFilters" class="flex flex-wrap gap-2">
          <div v-for="field in activeFilters.fields" :key="field" class="badge badge-primary badge-lg">
            Task: {{ toHumanReadable(field) }}
            <button @click="removeActiveFilter('fields', field)" class="ml-2 text-xs">✕</button>
          </div>
          <div v-for="tool in activeFilters.tools" :key="tool" class="badge badge-secondary badge-lg">
            Tool: {{ tool }}
            <button @click="removeActiveFilter('tools', tool)" class="ml-2 text-xs">✕</button>
          </div>
        </div>
        <div v-else class="text-gray-500 italic">
          No active filters. Select filters from above to refine your search.
        </div>
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
