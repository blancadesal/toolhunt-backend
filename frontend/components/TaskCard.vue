<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue';
import { debounce } from 'lodash-es';

const props = defineProps({
  tasks: Array,
  currentTaskIndex: Number,
  annotationsSchema: Object,
  fieldInputOptions: Array,
  isArrayType: Boolean,
  validationError: String,
  validateInput: Function,
});

const emit = defineEmits([
  'update:current-task-index',
  'submit-contribution',
  'load-new-batch',
  'update:validation-error'
]);

const { isLoggedIn } = useAuth();

const inputRef = ref(null);
const submittedTasks = ref(new Set());
const isSubmitting = ref(false);
const hasAttemptedSubmit = ref(false);
const taskInputs = ref({});

const currentTask = computed(() => props.tasks[props.currentTaskIndex] || null);

const isCurrentTaskSubmitted = computed(() => {
  return currentTask.value && submittedTasks.value.has(currentTask.value.id);
});

const currentUserInput = computed({
  get: () => {
    if (currentTask.value) {
      const input = taskInputs.value[currentTask.value.id];
      if (props.isArrayType) {
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

const fieldDescription = computed(() => {
  if (props.annotationsSchema && currentTask.value && currentTask.value.field) {
    const fieldName = currentTask.value.field;
    const fieldProperties = props.annotationsSchema.schemas.Annotations.properties;
    return fieldProperties[fieldName]?.description || `Enter ${toHumanReadable(fieldName)}`;
  }
  return '';
});

const getPlaceholder = (fieldName) => {
  switch (fieldName) {
    case 'repository':
      return 'Enter repository URL (e.g., https://github.com/username/repository)';
    case 'api_url':
      return 'Enter API URL';
    case 'bugtracker_url':
      return 'Enter bug tracker URL';
    case 'translate_url':
      return 'Enter translation interface URL';
    default:
      return `Enter ${fieldName}`;
  }
};

const getInputType = (fieldName) => {
  switch (fieldName) {
    case 'repository':
    case 'api_url':
    case 'bugtracker_url':
    case 'translate_url':
      return 'url';
    case 'deprecated':
    case 'experimental':
      return 'checkbox';
    default:
      return 'text';
  }
};

const addArrayItem = () => {
  if (props.isArrayType) {
    const newInput = Array.isArray(currentUserInput.value) ? [...currentUserInput.value, ''] : [''];
    currentUserInput.value = newInput;
  }
};

const removeArrayItem = (index) => {
  if (props.isArrayType && Array.isArray(currentUserInput.value)) {
    const newInput = [...currentUserInput.value];
    newInput.splice(index, 1);
    currentUserInput.value = newInput;
  }
};

const handleEnterKey = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    if (!isSubmitting.value) {
      submitContribution();
    }
  }
};

const submitContribution = () => {
  if (isSubmitting.value) return;
  
  isSubmitting.value = true;
  hasAttemptedSubmit.value = true;
  console.log('submitContribution called');
  console.log('isLoggedIn:', isLoggedIn);
  console.log('currentTask:', currentTask.value);
  console.log('currentUserInput:', currentUserInput.value);

  if (!isLoggedIn.value || !currentTask.value) {
    console.log('Returning early: not logged in or no current task');
    isSubmitting.value = false;
    return;
  }

  if (!props.validateInput(currentUserInput.value)) {
    console.log('Input validation failed');
    emit('update:validation-error', 'Invalid input');
    isSubmitting.value = false;
    return;
  }

  emit('update:validation-error', '');
  submittedTasks.value.add(currentTask.value.id);
  emit('submit-contribution', currentUserInput.value);
  
  // Reset isSubmitting after a short delay
  setTimeout(() => {
    isSubmitting.value = false;
    // Move to the next task after successful submission
    changeTask('next');
  }, 300);
};

const resetSubmittedTasks = () => {
  submittedTasks.value.clear();
  hasAttemptedSubmit.value = false;
  taskInputs.value = {};
};

// Expose the resetSubmittedTasks method to the parent component
defineExpose({ resetSubmittedTasks });

const focusInput = () => {
  nextTick(() => {
    if (inputRef.value) {
      inputRef.value.focus();
    }
  });
};

watch(() => props.currentTaskIndex, () => {
  if (currentTask.value && !(currentTask.value.id in taskInputs.value)) {
    taskInputs.value[currentTask.value.id] = props.isArrayType ? [] : '';
  }
  hasAttemptedSubmit.value = false;
  emit('update:validation-error', '');
  focusInput();
});

onMounted(() => {
  if (currentTask.value) {
    taskInputs.value[currentTask.value.id] = props.isArrayType ? [] : '';
  }
  window.addEventListener('keydown', handleKeydown);
  focusInput();
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown);
});

const taskIndicators = computed(() => {
  return props.tasks.map(task => ({
    id: task.id,
    completed: submittedTasks.value.has(task.id)
  }));
});

const isTaskChanging = ref(false);

const changeTask = (direction) => {
  isTaskChanging.value = true;
  emit('update:validation-error', '');
  setTimeout(() => {
    if (direction === 'next') {
      nextTask();
    } else if (direction === 'previous') {
      previousTask();
    }
    isTaskChanging.value = false;
  }, 150);
};

const nextTask = () => {
  if (!isLastTask.value) {
    emit('update:current-task-index', props.currentTaskIndex + 1);
  }
};

const previousTask = () => {
  if (!isFirstTask.value) {
    emit('update:current-task-index', props.currentTaskIndex - 1);
  }
};

const isFirstTask = computed(() => props.currentTaskIndex === 0);
const isLastTask = computed(() => props.currentTaskIndex === props.tasks.length - 1);

const handleKeydown = (event) => {
  if (event.key === 'ArrowLeft' && !isFirstTask.value) {
    changeTask('previous');
  } else if (event.key === 'ArrowRight' && !isLastTask.value) {
    changeTask('next');
  }
};
</script>

<template>
  <div
    v-if="currentTask"
    :key="currentTask.id"
    class="card bg-base-100 shadow-xl w-full max-w-7xl transition-all duration-150 ease-in-out"
    :class="{ 'opacity-85': isTaskChanging }"
  >
    <!-- Task Type Banner -->
    <div class="bg-secondary bg-opacity-90 text-secondary-content p-2 rounded-t-xl">
      <p class="text-center text-lg font-semibold">
        Task: {{ toHumanReadable(currentTask.field) }}
      </p>
    </div>
    <div class="card-body">
      <!-- Task Progress Indicators -->
      <div class="flex justify-center mb-4 space-x-2">
        <div
          v-for="(indicator, index) in taskIndicators"
          :key="indicator.id"
          class="w-3 h-3 rounded-full border-2 border-primary transition-all duration-300"
          :class="{
            'bg-primary': indicator.completed,
            'ring-2 ring-primary ring-opacity-50': index === currentTaskIndex
          }"
        ></div>
      </div>

      <!-- Tool Info Section -->
      <div class="bg-secondary bg-opacity-10 p-4 mb-2 shadow-md rounded-lg">
        <h2 class="card-title text-primary-content text-2xl mb-4">{{ currentTask.tool.title }}</h2>
        <p class="mb-4 text-primary-content">{{ currentTask.tool.description }}</p>
        <div class="flex items-center mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          <a :href="currentTask.tool.url" target="_blank" class="text-blue-500 hover:underline">{{ currentTask.tool.url }}</a>
        </div>
      </div>

      <div class="form-control">
        <div v-if="currentTask && currentTask.field">
          <label class="label">
            <span class="label-text text-lg font-semibold mb-4">{{ fieldDescription }}</span>
          </label>

          <!-- Single select dropdown (for tool_type and other non-array types with options) -->
          <select
            v-if="!isArrayType && fieldInputOptions.length > 0"
            ref="inputRef"
            v-model="currentUserInput"
            @keydown="handleEnterKey"
            class="select select-bordered w-full"
            :disabled="isCurrentTaskSubmitted"
          >
            <option disabled value="">Select an option</option>
            <option v-for="option in fieldInputOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>

          <!-- Checkbox group for multi-select (for array types) -->
          <div v-else-if="isArrayType && fieldInputOptions.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
            <div v-for="option in fieldInputOptions" :key="option.value" class="flex items-center">
              <input
                :id="`checkbox-${option.value}`"
                type="checkbox"
                :value="option.value"
                v-model="currentUserInput"
                @keydown="handleEnterKey"
                class="checkbox checkbox-primary border-2 mr-2"
                :disabled="isCurrentTaskSubmitted"
              />
              <label :for="`checkbox-${option.value}`" class="cursor-pointer">{{ option.label }}</label>
            </div>
          </div>

          <!-- Array input for non-predefined options -->
          <div v-else-if="isArrayType" class="space-y-2">
            <div v-for="(item, index) in currentUserInput" :key="index" class="flex items-center space-x-2">
              <input
                v-model="currentUserInput[index]"
                :ref="index === 0 ? inputRef : undefined"
                @keydown="handleEnterKey"
                type="text"
                :placeholder="`Enter item ${index + 1}`"
                class="input input-bordered flex-grow"
                :disabled="isCurrentTaskSubmitted"
              />
              <button @click="removeArrayItem(index)" class="btn btn-ghost btn-sm" :disabled="isCurrentTaskSubmitted">X</button>
            </div>
            <button @click="addArrayItem" class="btn btn-ghost btn-sm" :disabled="isCurrentTaskSubmitted">+ Add Item</button>
          </div>

          <!-- Single input for non-array types -->
          <input
            v-if="!isArrayType && fieldInputOptions.length === 0"
            ref="inputRef"
            v-model="currentUserInput"
            :type="getInputType(currentTask.field)"
            :placeholder="getPlaceholder(currentTask.field)"
            class="input input-bordered w-full"
            @keydown="handleEnterKey"
            :disabled="isCurrentTaskSubmitted"
          />

          <!-- Validation Error -->
          <div v-if="hasAttemptedSubmit && validationError" class="text-error text-sm mt-1">
            {{ validationError }}
          </div>
        </div>
      </div>

      <div class="card-actions justify-end mt-4">
        <button
          v-if="!isFirstTask"
          @click="changeTask('previous')"
          class="btn btn-outline mr-2"
        >
          &lt; Previous
        </button>
        <button
          @click="submitContribution"
          class="btn btn-primary mr-2"
          :disabled="!isLoggedIn || isCurrentTaskSubmitted || isTaskChanging || isSubmitting || (isArrayType && Array.isArray(currentUserInput) && currentUserInput.length === 0)"
        >
          {{ isCurrentTaskSubmitted ? 'Submitted' : (isLoggedIn ? 'Submit' : 'Login to Submit') }}
        </button>
        <button
          v-if="!isLastTask"
          @click="changeTask('next')"
          class="btn btn-outline btn-secondary"
        >
          Next &gt;
        </button>
        <button
          v-else
          @click="$emit('load-new-batch')"
          class="btn btn-outline btn-secondary"
        >
          New Batch &gt;
        </button>
      </div>
    </div>
  </div>
</template>