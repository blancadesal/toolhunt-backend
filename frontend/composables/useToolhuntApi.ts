// composables/useToolhuntApi.ts

import { ref } from 'vue'
import type { Ref } from 'vue'
import { toolhuntApi } from '~/utils/ToolhuntApiClient'
import type { Task, AnnotationsSchema } from '~/utils/ToolhuntApiClient'

export function useToolhuntApi() {
  const tasks: Ref<Task[]> = ref([])
  const fieldNames: Ref<string[]> = ref([])
  const annotationsSchema: Ref<AnnotationsSchema | null> = ref(null)

  const fetchTasks = async (toolName: string | null = null, fieldNames: string | null = null): Promise<void> => {
    try {
      tasks.value = await toolhuntApi.fetchTasks(toolName, fieldNames)
    } catch (error) {
      console.error('Error fetching tasks:', error)
      tasks.value = []
    }
  }

  const fetchFieldNames = async (): Promise<void> => {
    try {
      fieldNames.value = await toolhuntApi.fetchFieldNames()
    } catch (error) {
      console.error('Error fetching field names:', error)
      fieldNames.value = []
    }
  }

  const fetchAnnotationsSchema = async (): Promise<void> => {
    try {
      annotationsSchema.value = await toolhuntApi.fetchAnnotationsSchema()
    } catch (error) {
      console.error('Error fetching annotations schema:', error)
      annotationsSchema.value = null
    }
  }

  return {
    tasks,
    fieldNames,
    annotationsSchema,
    fetchTasks,
    fetchFieldNames,
    fetchAnnotationsSchema
  }
}