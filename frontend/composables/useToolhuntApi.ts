// composables/useToolhuntApi.ts

import { ref } from 'vue'
import type { Ref } from 'vue'
import { toolhuntApi } from '~/utils/ToolhuntApiClient'
import type { Task, AnnotationsSchema, ContributionsResponse, ContributionsParams, UserContributionsResponse } from '~/utils/ToolhuntApiClient'

export function useToolhuntApi() {
  const tasks: Ref<Task[]> = ref([])
  const fieldNames: Ref<string[]> = ref([])
  const annotationsSchema: Ref<AnnotationsSchema | null> = ref(null)
  const contributions: Ref<ContributionsResponse | null> = ref(null)
  const userContributions: Ref<UserContributionsResponse> = ref({ contributions: [], total_contributions: 0 })
  const error: Ref<string | null> = ref(null)

  const fetchTasks = async (toolNames: string | null = null, fieldNames: string | null = null): Promise<void> => {
    try {
      tasks.value = await toolhuntApi.fetchTasks(toolNames, fieldNames)
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

  const fetchContributions = async (params?: ContributionsParams): Promise<void> => {
    try {
      contributions.value = await toolhuntApi.fetchContributions(params)
    } catch (error) {
      console.error('Error fetching contributions:', error)
      contributions.value = null
    }
  }

  const fetchUserContributions = async (username: string, limit?: number): Promise<void> => {
    error.value = null
    try {
      userContributions.value = await toolhuntApi.fetchUserContributions(username, limit)
    } catch (err) {
      console.error('Error fetching user contributions:', err)
      error.value = err instanceof Error ? err.message : String(err)
      userContributions.value = { contributions: [], total_contributions: 0 }
    }
  }

  const submitTask = async (taskId: number, submission: TaskSubmission): Promise<void> => {
    try {
      await toolhuntApi.submitTask(taskId, submission);
    } catch (error) {
      console.error('Error submitting task:', error);
      throw error;
    }
  };

  return {
    tasks,
    fieldNames,
    annotationsSchema,
    fetchTasks,
    fetchFieldNames,
    fetchAnnotationsSchema,
    contributions,
    fetchContributions,
    userContributions,
    fetchUserContributions,
    error,
    submitTask
  }
}