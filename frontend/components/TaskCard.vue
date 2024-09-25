<script setup>
// Props and emits
const props = defineProps({
  tasks: Array,
  annotationsSchema: Object,
});

const emit = defineEmits(['load-new-batch']);

// Composables
const { isLoggedIn, fetchUserData, authState } = useAuth();
const { submitTask } = useToolhuntApi();

const tasksRef = computed(() => props.tasks);
const {
  currentTaskIndex,
  currentTask,
  isFirstTask,
  isLastTask,
  isTaskChanging,
  navigateTask,
  handleKeyNavigation,
  jumpToTask
} = useTaskNavigation(tasksRef);

const {
  fieldSchema,
  isArrayType,
  fieldDescription,
  fieldInputOptions,
  inputType,
  placeholder,
} = useFieldSchema(currentTask, computed(() => props.annotationsSchema));

const {
  validateInput,
  validationError,
  setValidationError,
  clearValidationError
} = useInputValidation(fieldSchema, isArrayType, computed(() => props.annotationsSchema));

// Refs
const inputRef = ref(null);
const submittedTasks = ref(new Set());
const isSubmitting = ref(false);
const taskInputs = ref({});
const isReportModalOpen = ref(false);
const reportedToolAttributes = ref({});

// Watchers
watch(() => currentTaskIndex.value, (newIndex, oldIndex) => {
  if (newIndex !== oldIndex) {  // Only run this when actually changing tasks
    if (currentTask.value && !(currentTask.value.id in taskInputs.value)) {
      taskInputs.value[currentTask.value.id] = isArrayType.value ? [] : '';
    }
    clearValidationError();  // Clear validation error when changing tasks
    focusInput();
  }
});

// Lifecycle hooks
onMounted(async () => {
  if (currentTask.value) {
    taskInputs.value[currentTask.value.id] = isArrayType.value ? [] : '';
  }
  window.addEventListener('keydown', handleKeyNavigation);
  focusInput();

  // Fetch user data if logged in
  if (isLoggedIn.value) {
    await fetchUserData();
  }
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeyNavigation);
});

// Computed properties
const isCurrentTaskSubmitted = computed(() => {
  return currentTask.value && submittedTasks.value.has(currentTask.value.id);
});

const currentUserInput = computed({
  get: () => {
    if (currentTask.value) {
      const input = taskInputs.value[currentTask.value.id];
      if (isArrayType.value) {
        return Array.isArray(input) ? input : [];
      }
      return input ?? '';
    }
    return '';
  },
  set: (value) => {
    if (currentTask.value) {
      taskInputs.value[currentTask.value.id] = value;
    }
  }
});

const taskIndicators = computed(() => {
  return props.tasks.map((task, index) => ({
    index,
    completed: submittedTasks.value.has(task.id)
  }));
});

const isSubmitDisabled = computed(() => {
  const hasNoInput = isArrayType.value
    ? !currentUserInput.value || currentUserInput.value.length === 0
    : !currentUserInput.value;

  return !isLoggedIn.value ||
         isCurrentTaskSubmitted.value ||
         isTaskChanging.value ||
         isSubmitting.value ||
         hasNoInput;
});

const isCurrentToolReported = computed(() => {
  return !!(currentTask.value && reportedToolAttributes.value[currentTask.value.tool.name]);
});

// Methods
const handleEnterKey = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    if (!isSubmitting.value) {
      submitContribution();
    }
  }
};

const submitContribution = async () => {
  if (isSubmitting.value) return;

  isSubmitting.value = true;
  console.log('submitContribution called');

  if (!isLoggedIn.value || !currentTask.value || !authState.value.user) {
    console.log('Returning early: not logged in, no current task, or no user data');
    isSubmitting.value = false;
    return;
  }

  const { isValid, error } = validateInput(currentUserInput.value);
  if (!isValid) {
    console.log('Input validation failed:', error);
    setValidationError(error || 'Invalid input');
    isSubmitting.value = false;
    return;
  }

  // Clear validation error if input is valid
  clearValidationError();
  submittedTasks.value.add(currentTask.value.id);

  const submission = {
    tool: {
      name: currentTask.value.tool.name,
      title: currentTask.value.tool.title,
    },
    user: {
      id: authState.value.user.id,
    },
    completed_date: new Date().toISOString(),
    value: currentUserInput.value
  };

  console.log('Submission data:', submission);

  try {
    await submitTask(currentTask.value.id, submission);
    console.log('Contribution submitted successfully');
    // We might want to show a success message to the user here
  } catch (error) {
    console.error('Error submitting contribution:', error);
    setValidationError('Failed to submit contribution. Please try again.');
    submittedTasks.value.delete(currentTask.value.id);
    isSubmitting.value = false;
    return;
  }

  // Reset isSubmitting after a short delay
  setTimeout(() => {
    isSubmitting.value = false;
    // Move to the next task after successful submission
    navigateTask('next', () => emit('load-new-batch'));
  }, 100);
};

const resetSubmittedTasks = () => {
  submittedTasks.value.clear();
  taskInputs.value = {};
  clearValidationError();  // Clear validation error when resetting tasks
};

const focusInput = () => {
  nextTick(() => {
    if (inputRef.value && typeof inputRef.value.focus === 'function') {
      inputRef.value.focus();
    }
  });
};

const openReportModal = () => {
  isReportModalOpen.value = true;
};

const submitReport = async (attributes) => {
  if (currentTask.value) {
    const toolName = currentTask.value.tool.name;
    const selectedAttributes = Object.entries(attributes)
      .filter(([_, value]) => value)
      .map(([key, _]) => key);

    reportedToolAttributes.value[toolName] = { ...attributes };

    for (const attribute of selectedAttributes) {
      const submission = {
        tool: {
          name: currentTask.value.tool.name,
          title: currentTask.value.tool.title,
        },
        user: {
          id: authState.value.user.id,
        },
        completed_date: new Date().toISOString(),
        value: true,
        field: attribute
      };

      console.log(`Submitting report for ${attribute}:`, submission);
      try {
        await submitTask(currentTask.value.id, submission);
        console.log(`Report for ${attribute} submitted successfully`);
      } catch (error) {
        console.error(`Error submitting report for ${attribute}:`, error);
        // We might want to show an error message to the user here
      }
    }
  }

  isReportModalOpen.value = false;
};

// Expose methods
defineExpose({ resetSubmittedTasks });
</script>

<template>
  <div>
    <div
      v-if="currentTask"
      :key="currentTask.id"
      class="card bg-base-100 shadow-xl w-full max-w-7xl transition-all duration-150 ease-in-out"
      :class="{ 'opacity-85': isTaskChanging }"
    >
      <!-- Task Type Banner -->
      <div class="bg-secondary bg-opacity-90 text-secondary-content p-2 rounded-t-xl">
        <p class="text-center text-lg">
          {{ toHumanReadable(currentTask.field) }}
        </p>
      </div>
      <div class="card-body break-words">
        <!-- Task Progress Indicators -->
        <div class="flex justify-center mb-4 space-x-3">
          <div
            v-for="indicator in taskIndicators"
            :key="indicator.index"
            class="w-6 h-6 rounded-full border-2 border-primary flex items-center justify-center text-sm font-medium transition-all duration-100 cursor-pointer"
            :class="{
              'bg-primary text-white': indicator.completed,
              'ring-2 ring-primary ring-opacity-50': indicator.index === currentTaskIndex,
              'text-primary': !indicator.completed
            }"
            @click="jumpToTask(indicator.index)"
          >
            {{ indicator.index + 1 }}
          </div>
        </div>

        <!-- Tool Info Section -->
        <div class="bg-secondary bg-opacity-10 p-4 mb-4 shadow-md rounded-lg">
          <div class="flex justify-between items-start mb-4">
            <h2 class="card-title text-primary-content text-2xl">
              <a
                :href="`https://toolhub.wikimedia.org/tools/${currentTask.tool.name}`"
                target="_blank"
                class="transition-opacity duration-200 hover:opacity-70"
              >
                {{ currentTask.tool.title }}
              </a>
            </h2>
            <button @click="openReportModal" class="btn btn-sm" :class="isCurrentToolReported ? 'btn-success' : 'btn-warning'">
              {{ isCurrentToolReported ? 'Tool Flagged' : 'Flag Tool' }}
            </button>
          </div>
          <p class="mb-4 text-primary-content">{{ currentTask.tool.description }}</p>
          <div class="flex items-center mb-2 overflow-hidden">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 flex-shrink-0 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <a :href="currentTask.tool.url" target="_blank" class="text-blue-500 hover:underline break-all">{{ currentTask.tool.url }}</a>
          </div>
        </div>

        <div class="form-control">
          <div v-if="currentTask && currentTask.field">
            <label class="label">
              <span class="label-text text-lg font-semibold">{{ fieldDescription }}</span>
            </label>

            <!-- Use SelectInput for non-array types with options -->
            <SelectInput
              v-if="!isArrayType && fieldInputOptions.length > 0"
              ref="inputRef"
              v-model="currentUserInput"
              :options="fieldInputOptions"
              :disabled="isCurrentTaskSubmitted"
              @enter="handleEnterKey"
            />

            <!-- Use CheckboxGroupInput for array types with options -->
            <CheckboxGroupInput
              v-else-if="isArrayType && fieldInputOptions.length > 0"
              ref="inputRef"
              v-model="currentUserInput"
              :options="fieldInputOptions"
              :disabled="isCurrentTaskSubmitted"
              @enter="handleEnterKey"
            />

            <!-- Use SingleInput for all other input types -->
            <SingleInput
              v-else
              ref="inputRef"
              v-model="currentUserInput"
              :type="inputType"
              :placeholder="placeholder"
              :disabled="isCurrentTaskSubmitted"
              @enter="handleEnterKey"
            />

            <!-- Validation Error -->
            <div v-if="validationError" class="text-error text-sm mt-1">
              {{ validationError }}
            </div>
          </div>
        </div>

        <div class="card-actions justify-end mt-4">
          <button
            v-if="!isFirstTask"
            @click="navigateTask('previous', () => {})"
            class="btn btn-outline mr-2"
          >
            &lt; Previous
          </button>
          <button
            @click="submitContribution"
            class="btn btn-primary mr-2"
            :disabled="isSubmitDisabled"
          >
            {{ isCurrentTaskSubmitted ? 'Submitted' : (isLoggedIn ? 'Submit' : 'Login to Submit') }}
          </button>
          <button
            @click="navigateTask('next', () => $emit('load-new-batch'))"
            class="btn btn-outline btn-secondary"
          >
            {{ isLastTask ? 'New Batch' : 'Next' }} &gt;
          </button>
        </div>
      </div>
    </div>

    <!-- Report Tool Modal -->
    <ReportToolModal
      :is-open="isReportModalOpen"
      :tool-name="currentTask?.tool.name"
      :is-tool-reported="isCurrentToolReported"
      :reported-attributes="reportedToolAttributes[currentTask?.tool.name]"
      @close="isReportModalOpen = false"
      @submit="submitReport"
    />
  </div>
</template>
