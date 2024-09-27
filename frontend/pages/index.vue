<script setup>
const { tasks, fieldNames, annotationsSchema, toolNames, fetchTasks, fetchFieldNames, fetchAnnotationsSchema, fetchToolNames } = useToolhuntApi()

const currentTaskIndex = ref(0)
const isLoading = ref(true)
const taskCardRef = ref(null)

const selectedFilters = ref({
  fields: [],
  tools: []
})

const activeFilters = ref({
  fields: [],
  tools: []
})

const isApplyingFilters = ref(false)

const loadNewBatch = async () => {
  const scrollPosition = window.scrollY

  isLoading.value = true
  currentTaskIndex.value = 0
  if (taskCardRef.value) {
    taskCardRef.value.resetSubmittedTasks()
  }

  const toolFilter = activeFilters.value.tools.length > 0
    ? activeFilters.value.tools.map(tool => toolNames.value?.titles[tool] || '').join(',')
    : null
  const fieldFilter = activeFilters.value.fields.length > 0
    ? activeFilters.value.fields.join(',')
    : null

  await fetchTasks(toolFilter, fieldFilter)
  isLoading.value = false

  await nextTick()
  window.scrollTo({ top: scrollPosition, behavior: 'smooth' })
}

const updateSelectedFilters = (type, filters) => {
  selectedFilters.value[type] = filters
}

const removeSelectedFilter = (type, filter) => {
  selectedFilters.value[type] = selectedFilters.value[type].filter(f => f !== filter)
}

const applyFilters = async () => {
  isApplyingFilters.value = true
  activeFilters.value = JSON.parse(JSON.stringify(selectedFilters.value))
  await loadNewBatch()
  isApplyingFilters.value = false
}

const clearAllFilters = () => {
  selectedFilters.value = { fields: [], tools: [] }
  activeFilters.value = { fields: [], tools: [] }
  loadNewBatch()

  if (window.scrollY > 0) {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const hasSelectedFilters = computed(() => {
  return selectedFilters.value.fields.length > 0 || selectedFilters.value.tools.length > 0
})

const hasActiveFilters = computed(() => {
  return activeFilters.value.fields.length > 0 || activeFilters.value.tools.length > 0
})

const isFiltersDirty = computed(() => {
  return JSON.stringify(selectedFilters.value) !== JSON.stringify(activeFilters.value)
})

const handleReportSubmitted = async (toolName) => {
  console.log(`Tool reported: ${toolName}`);
  await fetchToolNames();
};

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
            :active-fields="selectedFilters.fields"
            class="flex-grow"
            @update-filters="filters => updateSelectedFilters('fields', filters)"
          />
        </div>

        <!-- Tool Filter -->
        <div class="flex flex-col h-full">
          <ToolFilter
            :tools="toolNames?.all_titles || []"
            :active-tools="selectedFilters.tools"
            class="flex-grow"
            @update-filters="filters => updateSelectedFilters('tools', filters)"
          />
        </div>
      </div>

      <!-- Combined Filters Display -->
      <div class="mt-6 p-4 bg-base-200 rounded-lg shadow-md min-h-[100px] transition-all duration-300">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold text-secondary">Filters</h2>
          <div class="flex gap-2">
            <button
              type="button"
              class="btn btn-primary btn-sm"
              :disabled="!isFiltersDirty || isApplyingFilters"
              @click="applyFilters"
            >
              {{ isApplyingFilters ? 'Applying...' : 'Apply Filters' }}
            </button>
            <button
              type="button"
              class="btn btn-secondary btn-sm"
              :disabled="!hasSelectedFilters && !hasActiveFilters"
              @click="clearAllFilters"
            >
              Clear All Filters
            </button>
          </div>
        </div>
        <div v-if="hasSelectedFilters || hasActiveFilters" class="flex flex-wrap gap-2">
          <div
            v-for="field in new Set([...selectedFilters.fields, ...activeFilters.fields])"
            :key="field"
            class="badge badge-lg"
            :class="{
              'badge-primary': activeFilters.fields.includes(field),
              'badge-outline badge-primary': !activeFilters.fields.includes(field) && selectedFilters.fields.includes(field),
              'opacity-50': !selectedFilters.fields.includes(field) && activeFilters.fields.includes(field)
            }"
          >
            Annotation: {{ toHumanReadable(field) }}
            <button
              v-if="selectedFilters.fields.includes(field)"
              class="ml-2 text-xs"
              @click="removeSelectedFilter('fields', field)"
            >
              ✕
            </button>
          </div>
          <div
            v-for="tool in new Set([...selectedFilters.tools, ...activeFilters.tools])"
            :key="tool"
            class="badge badge-lg"
            :class="{
              'badge-secondary': activeFilters.tools.includes(tool),
              'badge-outline badge-secondary': !activeFilters.tools.includes(tool) && selectedFilters.tools.includes(tool),
              'opacity-50': !selectedFilters.tools.includes(tool) && activeFilters.tools.includes(tool)
            }"
          >
            Tool: {{ tool }}
            <button
              v-if="selectedFilters.tools.includes(tool)"
              class="ml-2 text-xs"
              @click="removeSelectedFilter('tools', tool)"
            >
              ✕
            </button>
          </div>
        </div>
        <div v-else class="text-gray-500 italic">
          No filters selected. Select filters from above and click 'Apply Filters' to refine your task selection.
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
      class="w-full max-w-7xl"
      @update:current-task-index="currentTaskIndex = $event"
      @load-new-batch="loadNewBatch"
      @report-submitted="handleReportSubmitted"
    />
  </div>
</template>
