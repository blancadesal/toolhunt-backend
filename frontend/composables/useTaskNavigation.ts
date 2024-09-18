export function useTaskNavigation(tasks: Ref<any[]>) {
  const currentTaskIndex = ref(0);
  const isTaskChanging = ref(false);

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

  const navigateTask = (direction: 'next' | 'previous', onNewBatch: () => void) => {
    isTaskChanging.value = true;
    setTimeout(() => {
      if (direction === 'next' && !isLastTask.value) {
        changeTask('next');
      } else if (direction === 'previous' && !isFirstTask.value) {
        changeTask('previous');
      } else if (direction === 'next' && isLastTask.value) {
        onNewBatch();
      }
      isTaskChanging.value = false;
    }, 150);
  };

  const handleKeyNavigation = (event: KeyboardEvent) => {
    if (event.key === 'ArrowLeft') {
      navigateTask('previous', () => {});
    } else if (event.key === 'ArrowRight') {
      navigateTask('next', () => {});
    }
  };

  return {
    currentTaskIndex,
    currentTask,
    isFirstTask,
    isLastTask,
    isTaskChanging,
    changeTask,
    navigateTask,
    handleKeyNavigation
  };
}
