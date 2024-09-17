// composables/useToolhuntApi.ts

import { ref } from 'vue'
import type { Ref } from 'vue'

export interface Task {
  id: string;
  field: string;
  tool: {
    title: string;
    description: string;
    url: string;
  };
  // Add other task properties as needed
}

export interface AnnotationsSchema {
  schemas: {
    Annotations: {
      properties: Record<string, any>;
    };
    [key: string]: any;
  };
  // Add other schema properties as needed
}

export function useToolhuntApi() {
  const tasks: Ref<Task[]> = ref([])
  const fieldNames: Ref<string[]> = ref([])
  const annotationsSchema: Ref<AnnotationsSchema | null> = ref(null)

  const fetchTasks = async (toolName: string | null = null, fieldNames: string | null = null): Promise<void> => {
    try {
      let url = 'http://localhost:8082/api/v1/tasks'
      const params = new URLSearchParams()
      if (toolName) params.append('tool_name', toolName)
      if (fieldNames) params.append('field_names', fieldNames)
      if (params.toString()) url += `?${params.toString()}`

      const response = await fetch(url)
      if (!response.ok) {
        throw new Error('Failed to fetch tasks')
      }
      const newTasks: Task[] = await response.json()
      tasks.value = newTasks
    } catch (error) {
      console.error('Error fetching tasks:', error)
      tasks.value = []
    }
  }

  const fetchFieldNames = async (): Promise<void> => {
    try {
      const response = await fetch('http://localhost:8082/api/v1/fields')
      if (!response.ok) {
        throw new Error('Failed to fetch field names')
      }
      const fields: string[] = await response.json()
      fieldNames.value = fields
    } catch (error) {
      console.error('Error fetching field names:', error)
      fieldNames.value = []
    }
  }

  const fetchAnnotationsSchema = async (): Promise<void> => {
    try {
      const response = await fetch('http://localhost:8082/api/v1/schema')
      if (!response.ok) {
        throw new Error('Failed to fetch annotations schema')
      }
      const schemaData: AnnotationsSchema = await response.json()
      annotationsSchema.value = schemaData
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