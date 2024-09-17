<script setup>
import { computed, ref, watch, onMounted, onBeforeUnmount } from 'vue';
import { useAuth } from '~/composables/useAuth';

const props = defineProps({
  currentTask: Object,
  tasks: Array,
  submittedTasks: Set,
  currentTaskIndex: Number,
  annotationsSchema: Object,
  isCurrentTaskSubmitted: Boolean,
  isTaskChanging: Boolean,
  isLastTask: Boolean,
  isFirstTask: Boolean,
  fieldInputOptions: Array,
  isArrayType: Boolean,
  currentUserInput: [String, Array],
  validationError: String,
  hasAttemptedSubmit: Boolean,
  validateInput: Function,
});

const emit = defineEmits(['update:currentUserInput', 'changeTask', 'submitContribution', 'loadNewBatch']);

const { isLoggedIn } = useAuth();

const inputRef = ref(null);

const fieldDescription = computed(() => {
  if (props.annotationsSchema && props.currentTask && props.currentTask.field) {
    const fieldName = props.currentTask.field;
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
    const newInput = Array.isArray(props.currentUserInput) ? [...props.currentUserInput, ''] : [''];
    emit('update:currentUserInput', newInput);
  }
};

const removeArrayItem = (index) => {
  if (props.isArrayType && Array.isArray(props.currentUserInput)) {
    const newInput = [...props.currentUserInput];
    newInput.splice(index, 1);
    emit('update:currentUserInput', newInput);
  }
};

const updateCurrentUserInput = (value) => {
  emit('update:currentUserInput', value);
};

const handleKeydown = (event) => {
  if (event.key === 'ArrowLeft' && !props.isFirstTask) {
    emit('changeTask', 'previous');
  } else if (event.key === 'ArrowRight' && !props.isLastTask) {
    emit('changeTask', 'next');
  }
};

const submitContribution = () => {
  if (!isLoggedIn || !props.currentTask) {
    return;
  }

  if (!props.validateInput()) {
    emit('update:validationError', 'Invalid input');
    return;
  }

  emit('update:validationError', '');
  emit('submitContribution');
};

watch(() => props.currentTask, () => {
  nextTick(() => {
    if (inputRef.value && !props.isArrayType && !props.currentTask.field.input_options) {
      inputRef.value.focus();
    }
  });
});

onMounted(() => {
  window.addEventListener('keydown', handleKeydown);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown);
});

const taskIndicators = computed(() => {
  return props.tasks.map(task => ({
    id: task.id,
    completed: props.submittedTasks.has(task.id)
  }));
});
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
            :value="currentUserInput"
            @input="updateCurrentUserInput($event.target.value)"
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
                :checked="currentUserInput.includes(option.value)"
                @change="updateCurrentUserInput(
                  $event.target.checked
                    ? [...currentUserInput, option.value]
                    : currentUserInput.filter(v => v !== option.value)
                )"
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
                :value="item"
                @input="updateCurrentUserInput(
                  currentUserInput.map((v, i) => i === index ? $event.target.value : v)
                )"
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
            v-else
            ref="inputRef"
            :value="currentUserInput"
            @input="updateCurrentUserInput($event.target.value)"
            :type="getInputType(currentTask.field)"
            :placeholder="getPlaceholder(currentTask.field)"
            class="input input-bordered w-full"
            @keyup.enter="$emit('submitContribution')"
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
          @click="$emit('changeTask', 'previous')"
          class="btn btn-outline mr-2"
        >
          &lt; Previous
        </button>
        <button
          @click="$emit('submitContribution')"
          class="btn btn-primary mr-2"
          :disabled="!isLoggedIn || isCurrentTaskSubmitted || isTaskChanging || (isArrayType && Array.isArray(currentUserInput) && currentUserInput.length === 0)"
        >
          {{ isCurrentTaskSubmitted ? 'Submitted' : (isLoggedIn ? 'Submit' : 'Login to Submit') }}
        </button>
        <button
          v-if="!isLastTask"
          @click="$emit('changeTask', 'next')"
          class="btn btn-outline btn-secondary"
        >
          Next &gt;
        </button>
        <button
          v-else
          @click="$emit('loadNewBatch')"
          class="btn btn-outline btn-secondary"
        >
          New Batch &gt;
        </button>
      </div>
    </div>
  </div>
</template>