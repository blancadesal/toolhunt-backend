import type { Task } from '~/utils/ToolhuntApiClient'

export function useTaskNavigation(tasks: Ref<Task[]>) {
  const currentTaskIndex = ref(0)
  const isTaskChanging = ref(false)

  const currentTask: ComputedRef<Task | null> = computed(() => tasks.value[currentTaskIndex.value] || null)
  const isFirstTask: ComputedRef<boolean> = computed(() => currentTaskIndex.value === 0)
  const isLastTask: ComputedRef<boolean> = computed(() => currentTaskIndex.value === tasks.value.length - 1)

  const changeTask = (direction: 'next' | 'previous') => {
    if (direction === 'next' && !isLastTask.value) {
      currentTaskIndex.value += 1
    }
    else if (direction === 'previous' && !isFirstTask.value) {
      currentTaskIndex.value -= 1
    }
  }

  const navigateTask = (direction: 'next' | 'previous', onNewBatch?: () => void) => {
    isTaskChanging.value = true
    setTimeout(() => {
      if (direction === 'next' && !isLastTask.value) {
        changeTask('next')
      }
      else if (direction === 'previous' && !isFirstTask.value) {
        changeTask('previous')
      }
      else if (direction === 'next' && isLastTask.value && onNewBatch) {
        onNewBatch()
      }
      isTaskChanging.value = false
    }, 150)
  }

  const handleKeyNavigation = (event: KeyboardEvent, onNewBatch?: () => void) => {
    if (event.key === 'ArrowLeft') {
      navigateTask('previous')
    }
    else if (event.key === 'ArrowRight') {
      navigateTask('next', onNewBatch)
    }
  }

  const jumpToTask = (index: number) => {
    if (index >= 0 && index < tasks.value.length) {
      isTaskChanging.value = true
      setTimeout(() => {
        currentTaskIndex.value = index
        isTaskChanging.value = false
      }, 150)
    }
  }

  return {
    currentTaskIndex,
    currentTask,
    isFirstTask,
    isLastTask,
    isTaskChanging,
    changeTask,
    navigateTask,
    handleKeyNavigation,
    jumpToTask,
  }
}
