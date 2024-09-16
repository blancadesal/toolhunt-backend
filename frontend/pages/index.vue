<script setup>
import { ref, computed, onMounted, watch, watchEffect, onBeforeUnmount, nextTick } from 'vue';
import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import { useAuth } from '@/composables/useAuth';
import { debounce } from 'lodash-es';

const { isLoggedIn } = useAuth();

const tasks = ref([]);
const currentTaskIndex = ref(0);
const searchQuery = ref('');
const fieldNames = ref([]);
const selectedFields = ref([]);
const showFieldFilter = ref(false);
const submittedTasks = ref(new Set());
const taskInputs = ref({});
const appliedFilters = ref(0);

const annotationsSchema = ref(null);
const fieldSchema = ref(null);
const validateField = ref(null);
const validationErrors = ref([]);

const currentTask = computed(() => tasks.value[currentTaskIndex.value] || null);

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

const fetchTasks = async (toolName = null, fieldNames = null) => {
  try {
    let url = 'http://localhost:8082/api/v1/tasks';
    const params = new URLSearchParams();
    if (toolName) params.append('tool_name', toolName);
    if (fieldNames) params.append('field_names', fieldNames);
    if (params.toString()) url += `?${params.toString()}`;

    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Failed to fetch tasks');
    }
    const newTasks = await response.json();
    tasks.value = newTasks;
  } catch (error) {
    console.error('Error fetching tasks:', error);
    tasks.value = [];
  }
};

const fetchFieldNames = async () => {
  try {
    const response = await fetch('http://localhost:8082/api/v1/fields');
    if (!response.ok) {
      throw new Error('Failed to fetch field names');
    }
    const fields = await response.json();
    fieldNames.value = fields.map(field => ({
      value: field,
      label: toHumanReadable(field)
    }));
  } catch (error) {
    console.error('Error fetching field names:', error);
    fieldNames.value = [];
  }
};

const fetchAnnotationsSchema = async () => {
  try {
    const response = await fetch('http://localhost:8082/api/v1/schema');
    if (!response.ok) {
      throw new Error('Failed to fetch annotations schema');
    }
    const schemaData = await response.json();
    annotationsSchema.value = schemaData;
  } catch (error) {
    console.error('Error fetching annotations schema:', error);
  }
};

const ajv = new Ajv({ allErrors: true, strictSchema: false, strictTypes: false });
addFormats(ajv);

const repositoryUrlPattern = /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/;

ajv.addFormat('repositoryUrl', {
  validate: (str) => repositoryUrlPattern.test(str)
});

watch(annotationsSchema, (newValue) => {
  if (newValue) {
    const schemas = newValue.schemas;
    for (const [key, schema] of Object.entries(schemas)) {
      ajv.addSchema(schema, `#/schemas/${key}`);
    }
  }
});

watch([annotationsSchema, currentTask], ([annotationsSchemaValue, currentTaskValue]) => {
  if (annotationsSchemaValue && currentTaskValue && currentTaskValue.field) {
    const fieldName = currentTaskValue.field.name;
    const annotationsProperties = annotationsSchemaValue.schemas.Annotations.properties;
    if (annotationsProperties && annotationsProperties[fieldName]) {
      let fieldSchemaValue = {
        ...annotationsProperties[fieldName],
        $id: `#/fieldSchema/${fieldName}`
      };

      // Handle nullable fields
      if (fieldSchemaValue.nullable === true) {
        fieldSchemaValue = {
          oneOf: [
            { type: 'null' },
            { ...fieldSchemaValue, nullable: undefined }
          ]
        };
      }

      // Add custom validation for repository field
      if (fieldName === 'repository') {
        fieldSchemaValue.format = 'repositoryUrl';
      }

      fieldSchema.value = fieldSchemaValue;
    } else {
      fieldSchema.value = null;
    }
  } else {
    fieldSchema.value = null;
  }
});

watch(fieldSchema, (newFieldSchema) => {
  if (newFieldSchema) {
    try {
      validateField.value = ajv.compile(newFieldSchema);
    } catch (e) {
      console.error('Error compiling validator for field:', e);
      validateField.value = null;
    }
  } else {
    validateField.value = null;
  }
});

const debouncedValidate = debounce(() => {
  if (validateField.value) {
    const input = currentUserInput.value;
    const isValid = validateField.value(input);
    validationErrors.value = isValid ? [] : (validateField.value.errors || []);
  } else {
    validationErrors.value = [];
  }
}, 300);

watchEffect(() => {
  debouncedValidate();
});

const errorMessage = (error) => {
  if (currentTask.value && currentTask.value.field.name === 'repository') {
    if (error.keyword === 'format') {
      return 'Please enter a valid repository URL (e.g., https://github.com/username/repository)';
    }
  }
  return error.message;
};

const validateInput = () => {
  if (validateField.value) {
    const input = currentUserInput.value;
    const isValid = validateField.value(input);
    validationErrors.value = isValid ? [] : (validateField.value.errors || []);
    return isValid;
  }
  return true;
};

const fieldSchemaType = computed(() => {
  return fieldSchema.value ? fieldSchema.value.type : null;
});

const isArrayType = computed(() => {
  return fieldSchema.value && fieldSchema.value.type === 'array';
});

const addArrayItem = () => {
  if (isArrayType.value) {
    if (!Array.isArray(currentUserInput.value)) {
      currentUserInput.value = [];
    }
    currentUserInput.value.push('');
  }
};

const removeArrayItem = (index) => {
  if (isArrayType.value && Array.isArray(currentUserInput.value)) {
    currentUserInput.value.splice(index, 1);
  }
};

const submitContribution = async () => {
  if (!isLoggedIn.value || !currentTask.value) {
    return;
  }

  if (!validateInput()) {
    return;
  }

  // Fake submission
  submittedTasks.value.add(currentTask.value.id);

  // Move to the next task automatically
  nextTask();
};

const nextTask = () => {
  if (currentTaskIndex.value < tasks.value.length - 1) {
    currentTaskIndex.value++;
  }
};

const previousTask = () => {
  if (currentTaskIndex.value > 0) {
    currentTaskIndex.value--;
  }
};

const searchTools = () => {
  // Implement search functionality
};

const toggleFieldFilter = () => {
  showFieldFilter.value = !showFieldFilter.value;
};

const applyFieldFilter = () => {
  fetchTasks(null, selectedFields.value.join(','));
  showFieldFilter.value = false;
  appliedFilters.value = selectedFields.value.length;
};

const clearFilters = () => {
  selectedFields.value = [];
  appliedFilters.value = 0;
  fetchTasks();
};

const toHumanReadable = (str) => {
  return str
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

const taskIndicators = computed(() => {
  return tasks.value.map(task => ({
    id: task.id,
    completed: submittedTasks.value.has(task.id)
  }));
});

const isCurrentTaskSubmitted = computed(() => {
  return currentTask.value && submittedTasks.value.has(currentTask.value.id);
});

const isLastTask = computed(() => currentTaskIndex.value === tasks.value.length - 1);
const isFirstTask = computed(() => currentTaskIndex.value === 0);

const loadNewBatch = async () => {
  // Clear the current batch
  tasks.value = [];
  currentTaskIndex.value = 0;
  submittedTasks.value.clear();
  taskInputs.value = {};

  // Fetch new tasks
  await fetchTasks();
};

const isTaskChanging = ref(false);

const changeTask = (direction) => {
  isTaskChanging.value = true;
  setTimeout(() => {
    if (direction === 'next') {
      nextTask();
    } else if (direction === 'previous') {
      previousTask();
    }
    isTaskChanging.value = false;
  }, 150); // Increased to 150ms for a slightly longer transition
};

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

const handleKeydown = (event) => {
  if (event.key === 'ArrowLeft' && !isFirstTask.value) {
    changeTask('previous');
  } else if (event.key === 'ArrowRight' && !isLastTask.value) {
    changeTask('next');
  }
};

const inputRef = ref(null);

const focusInput = () => {
  nextTick(() => {
    if (inputRef.value && !isArrayType.value && !currentTask.value.field.input_options) {
      inputRef.value.focus();
    }
  });
};

watch(currentTask, () => {
  focusInput();
});

onMounted(() => {
  fetchTasks();
  fetchFieldNames();
  fetchAnnotationsSchema();
  window.addEventListener('keydown', handleKeydown);
  focusInput();
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown);
});
</script>

<template>
  <div class="min-h-screen bg-base-200 flex flex-col items-center p-4">
    <h1 class="text-4xl font-bold mt-4 mb-4">Welcome to Toolhunt!</h1>

    <div class="w-full max-w-7xl mb-8 mt-4">
      <div class="form-control">
        <div class="relative">
          <input v-model="searchQuery" type="text" placeholder="Filter by tool" class="input input-bordered w-full pr-10" />
          <button @click="searchTools" class="absolute right-2 top-1/2 transform -translate-y-1/2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
          </button>
        </div>
      </div>
    </div>

    <div class="w-full max-w-7xl mb-4 flex">
      <button
        @click="toggleFieldFilter"
        :class="[
          'btn mr-2',
          showFieldFilter ? 'btn-secondary' : 'btn-outline btn-secondary'
        ]"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
        </svg>
        {{ showFieldFilter ? 'Hide Filter' : 'Field Filter' }}
      </button>
      <button
        v-if="appliedFilters > 0"
        @click="clearFilters"
        class="btn btn-outline btn-primary"
      >
        Clear Filters ({{ appliedFilters }})
      </button>
    </div>

    <!-- Field Filter Card -->
    <div v-if="showFieldFilter" class="card bg-base-100 shadow-xl w-full max-w-7xl mb-4">
      <div class="card-body">
        <h2 class="card-title text-xl mb-4">Filter by fields to complete</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <div v-for="field in fieldNames" :key="field.value" class="flex items-center">
            <input
              type="checkbox"
              :id="field.value"
              v-model="selectedFields"
              :value="field.value"
              class="checkbox checkbox-secondary mr-2"
            />
            <label :for="field.value" class="cursor-pointer text-sm">{{ field.label }}</label>
          </div>
        </div>
        <div class="card-actions justify-end mt-6">
          <button
            @click="applyFieldFilter"
            class="btn btn-secondary"
            :disabled="selectedFields.length === 0"
          >
            Apply Filter
          </button>
        </div>
      </div>
    </div>

    <!-- Task Card -->
    <div
      v-if="currentTask"
      :key="currentTask.id"
      class="card bg-base-100 shadow-xl w-full max-w-7xl transition-all duration-150 ease-in-out"
      :class="{ 'opacity-85': isTaskChanging }"
    >
      <div class="card-body">
        <!-- Task Indicators -->
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

        <h2 class="card-title text-2xl mb-2">{{ currentTask.tool.title }}</h2>
        <p class="mb-4 text-gray-600">{{ currentTask.tool.description }}</p>
        <div class="flex items-center mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <a :href="currentTask.tool.url" target="_blank" class="text-blue-500 hover:underline">{{ currentTask.tool.url }}</a>
        </div>
        <div class="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-4">
          <p class="font-bold">Missing Information:</p>
          <p>{{ currentTask.field.name }}</p>
          <p class="text-sm mt-2">{{ currentTask.field.description }}</p>
        </div>

        <div class="form-control">
          <div v-if="currentTask && currentTask.field">
            <label class="label">
              <span class="label-text">{{ currentTask.field.description || `Enter ${currentTask.field.name}` }}</span>
            </label>

            <!-- Single select dropdown -->
            <select
              v-if="currentTask.field.input_options && !isArrayType"
              v-model="currentUserInput"
              class="select select-bordered w-full"
              :disabled="submittedTasks.has(currentTask.id)"
            >
              <option disabled value="">Select an option</option>
              <option v-for="(label, value) in currentTask.field.input_options" :key="value" :value="value">
                {{ label }}
              </option>
            </select>

            <!-- Checkbox group for multi-select -->
            <div v-else-if="currentTask.field.input_options && isArrayType" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
              <div v-for="(label, value) in currentTask.field.input_options" :key="value" class="flex items-center">
                <input
                  :id="`checkbox-${value}`"
                  type="checkbox"
                  :value="value"
                  v-model="currentUserInput"
                  class="checkbox checkbox-primary mr-2"
                  :disabled="submittedTasks.has(currentTask.id)"
                />
                <label :for="`checkbox-${value}`" class="cursor-pointer">{{ label }}</label>
              </div>
            </div>

            <!-- Array input for non-predefined options -->
            <div v-else-if="isArrayType" class="space-y-2">
              <div v-for="(item, index) in currentUserInput" :key="index" class="flex items-center space-x-2">
                <input
                  v-model="currentUserInput[index]"
                  type="text"
                  :placeholder="`Enter item ${index + 1}`"
                  class="input input-bordered flex-grow"
                  :disabled="submittedTasks.has(currentTask.id)"
                />
                <button @click="removeArrayItem(index)" class="btn btn-ghost btn-sm" :disabled="submittedTasks.has(currentTask.id)">X</button>
              </div>
              <button @click="addArrayItem" class="btn btn-ghost btn-sm" :disabled="submittedTasks.has(currentTask.id)">+ Add Item</button>
            </div>

            <!-- Single input for non-array types -->
            <input
              v-else
              ref="inputRef"
              v-model="currentUserInput"
              :type="getInputType(currentTask.field.name)"
              :placeholder="getPlaceholder(currentTask.field.name)"
              class="input input-bordered w-full"
              :disabled="submittedTasks.has(currentTask.id)"
              @keyup.enter="submitContribution"
            />

            <!-- Validation Errors -->
            <div v-if="validationErrors.length > 0" class="text-red-500 text-sm mt-1">
              <div v-for="error in validationErrors" :key="error.instancePath">
                {{ errorMessage(error) }}
              </div>
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
            :disabled="!isLoggedIn || isCurrentTaskSubmitted || isTaskChanging"
          >
            {{ isCurrentTaskSubmitted ? 'Submitted' : (isLoggedIn ? 'Submit' : 'Login to Submit') }}
          </button>
          <button
            v-if="!isLastTask"
            @click="changeTask('next')"
            :class="[
              'btn btn-outline',
              isCurrentTaskSubmitted ? 'btn-secondary' : 'btn-accent'
            ]"
          >
            Next &gt;
          </button>
          <button
            v-else
            @click="loadNewBatch"
            class="btn btn-outline btn-secondary"
          >
            New Batch &gt;
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
