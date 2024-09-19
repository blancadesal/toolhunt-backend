<script setup>
import { ref, onMounted } from 'vue'
import FieldFilter from '@/components/FieldFilter.vue'
import ToolFilter from '@/components/ToolFilter.vue'
import TaskCard from '@/components/TaskCard.vue'

const { tasks, fieldNames, annotationsSchema, fetchTasks, fetchFieldNames, fetchAnnotationsSchema } = useToolhuntApi()

const currentTaskIndex = ref(0)
const isLoading = ref(true)
const taskCardRef = ref(null)

const appliedFields = ref([])
const appliedTools = ref([])

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
  
  let toolFilter = appliedTools.value.length > 0 ? appliedTools.value.map(tool => toolData.titles[tool]).join(',') : null
  let fieldFilter = appliedFields.value.length > 0 ? appliedFields.value.join(',') : null

  await fetchTasks(toolFilter, fieldFilter)
  isLoading.value = false
}

const applyFieldFilter = (selectedFields) => {
  appliedFields.value = selectedFields
  loadNewBatch()
}

const applyToolFilter = (selectedTools) => {
  appliedTools.value = selectedTools
  loadNewBatch()
}

const clearFieldFilter = () => {
  appliedFields.value = []
  loadNewBatch()
}

const clearToolFilter = () => {
  appliedTools.value = []
  loadNewBatch()
}

const removeAppliedField = (field) => {
  appliedFields.value = appliedFields.value.filter(f => f !== field)
  loadNewBatch()
}

const removeAppliedTool = (tool) => {
  appliedTools.value = appliedTools.value.filter(t => t !== tool)
  loadNewBatch()
}

const clearAllFilters = () => {
  appliedFields.value = []
  appliedTools.value = []
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
    <h1 class="text-4xl font-bold mt-4 mb-4">Welcome to Toolhunt!</h1>
    
    <div class="w-full max-w-7xl mb-8">
      <div class="flex flex-col lg:flex-row gap-6 justify-center">
        <!-- Field Filter -->
        <FieldFilter
          :field-names="fieldNames"
          :applied-fields="appliedFields"
          @apply-filter="applyFieldFilter"
          @clear-filter="clearFieldFilter"
          class="w-full lg:w-1/2"
        />

        <!-- Tool Filter -->
        <ToolFilter
          :tools="toolData.all_titles"
          :applied-tools="appliedTools"
          @apply-filter="applyToolFilter"
          @clear-filter="clearToolFilter"
          class="w-full lg:w-1/2"
        />
      </div>

      <!-- Applied Filters Display -->
      <div v-if="appliedFields.length > 0 || appliedTools.length > 0" class="mt-6">
        <h2 class="text-lg font-semibold mb-2">Active Filters:</h2>
        <div class="flex flex-wrap gap-2">
          <div v-for="field in appliedFields" :key="field" class="badge badge-lg badge-accent">
            Field: {{ field }}
            <button @click="removeAppliedField(field)" class="ml-2 text-xs">✕</button>
          </div>
          <div v-for="tool in appliedTools" :key="tool" class="badge badge-lg badge-primary">
            Tool: {{ tool }}
            <button @click="removeAppliedTool(tool)" class="ml-2 text-xs">✕</button>
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