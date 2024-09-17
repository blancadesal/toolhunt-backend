export function useTaskNavigation(tasks: Ref<any[]>) {
  const currentTaskIndex = ref(0);

  const currentTask: ComputedRef<any | null> = computed(() => tasks.value[currentTaskIndex.value] || null);
  const isFirstTask: ComputedRef<boolean> = computed(() => currentTaskIndex.value === 0);
  const isLastTask: ComputedRef<boolean> = computed(() => currentTaskIndex.value === tasks.value.length - 1);

  const changeTask = (direction: 'next' | 'previous') => {
    if (direction === 'next' && !isLastTask.value) {
      currentTaskIndex.value += 1;
    } else if (direction === 'previous' && !isFirstTask.value) {
      currentTaskIndex.value -= 1;
    }
  };

  return {
    currentTaskIndex,
    currentTask,
    isFirstTask,
    isLastTask,
    changeTask
  };
}
