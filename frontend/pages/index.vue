<script setup>

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
const isClosing = ref(false);

const currentTask = computed(() => tasks.value[currentTaskIndex.value] || null);

const currentUserInput = computed({
  get: () => {
    if (currentTask.value) {
      return taskInputs.value[currentTask.value.id] || '';
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

const validateInput = () => {
  const field = currentTask.value.field;
  if (field.input_options) {
    return field.input_options.hasOwnProperty(currentUserInput.value);
  } else if (field.pattern) {
    return new RegExp(field.pattern).test(currentUserInput.value);
  }
  return true;
};

const searchTools = () => {
  // Implement search functionality
};

const toggleFieldFilter = () => {
  showFieldFilter.value = !showFieldFilter.value;
  isClosing.value = false;
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

  if (showFieldFilter.value) {
    isClosing.value = true;
    setTimeout(() => {
      showFieldFilter.value = false;
      isClosing.value = false;
    }, 300); // Match this duration with the CSS transition duration
  }
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

onMounted(() => {
  fetchTasks();
  fetchFieldNames();
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
    <transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 transform scale-95"
      enter-to-class="opacity-100 transform scale-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 transform scale-100"
      leave-to-class="opacity-0 transform scale-95"
    >
      <div v-if="showFieldFilter && !isClosing" class="card bg-base-100 shadow-xl w-full max-w-7xl mb-4">
        <div class="card-body">
          <h2 class="card-title text-xl mb-4">Filter by Fields</h2>
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
            <button @click="applyFieldFilter" class="btn btn-secondary">Apply Filter</button>
          </div>
        </div>
      </div>
    </transition>

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
          <label class="label">
            <span class="label-text">Help complete this tool's information:</span>
          </label>
          <div v-if="currentTask.field.input_options">
            <select
              v-model="currentUserInput"
              class="select select-bordered w-full"
              :disabled="submittedTasks.has(currentTask.id)"
            >
              <option disabled value="">Select an option</option>
              <option v-for="(label, value) in currentTask.field.input_options" :key="value" :value="value">
                {{ label }}
              </option>
            </select>
          </div>
          <input
            v-else
            v-model="currentUserInput"
            type="text"
            :placeholder="`Enter ${currentTask.field.name}`"
            class="input input-bordered w-full"
            :disabled="submittedTasks.has(currentTask.id)"
          />
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
            {{ isCurrentTaskSubmitted ? 'Next' : 'Skip' }} &gt;
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
