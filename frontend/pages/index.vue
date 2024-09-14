<script setup>
const { isLoggedIn } = useAuth();

const tasks = ref([]);
const currentTaskIndex = ref(0);
const userInput = ref('');
const searchQuery = ref('');

const currentTask = computed(() => tasks.value[currentTaskIndex.value] || null);

const fetchTasks = async (toolName = null, fieldName = null) => {
  try {
    let url = 'http://localhost:8082/api/v1/tasks';
    const params = new URLSearchParams();
    if (toolName) params.append('tool_name', toolName);
    if (fieldName) params.append('field_name', fieldName);
    if (params.toString()) url += `?${params.toString()}`;

    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Failed to fetch tasks');
    }
    tasks.value = await response.json();
  } catch (error) {
    console.error('Error fetching tasks:', error);
    tasks.value = [];
  }
};

const nextTask = () => {
  currentTaskIndex.value = (currentTaskIndex.value + 1) % tasks.value.length;
  userInput.value = '';
};

const previousTask = () => {
  currentTaskIndex.value = (currentTaskIndex.value - 1 + tasks.value.length) % tasks.value.length;
  userInput.value = '';
};

const submitContribution = async () => {
  if (!isLoggedIn.value) {
    return;
  }

  if (!validateInput()) {
    return;
  }

  // Submit contribution logic here
  console.log(`Submitting ${userInput.value} for ${currentTask.value.tool.name}'s ${currentTask.value.field.name}`);
  nextTask();
};

const validateInput = () => {
  const field = currentTask.value.field;
  if (field.input_options) {
    return field.input_options.hasOwnProperty(userInput.value);
  } else if (field.pattern) {
    return new RegExp(field.pattern).test(userInput.value);
  }
  return true;
};

const searchTools = () => {
  // Implement search functionality
};

onMounted(() => fetchTasks());
</script>

<template>
  <div class="min-h-screen bg-base-200 flex flex-col items-center p-4">
    <h1 class="text-4xl font-bold mt-4 mb-4">Welcome to Toolhunt!</h1>

    <div class="w-full max-w-lg mb-8 mt-4">
      <div class="form-control">
        <div class="relative">
          <input v-model="searchQuery" type="text" placeholder="Search for tools..." class="input input-bordered w-full pr-10" />
          <button @click="searchTools" class="absolute right-2 top-1/2 transform -translate-y-1/2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
          </button>
        </div>
      </div>
    </div>

    <div v-if="currentTask" class="card bg-base-100 shadow-xl w-full max-w-lg">
      <div class="card-body">
        <h2 class="card-title text-2xl mb-2">{{ currentTask.tool.title }}</h2>
        <p class="mb-4 text-gray-600">{{ currentTask.tool.description }}</p>
        <div class="flex items-center mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
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
            <select v-model="userInput" class="select select-bordered w-full">
              <option disabled value="">Select an option</option>
              <option v-for="(label, value) in currentTask.field.input_options" :key="value" :value="value">
                {{ label }}
              </option>
            </select>
          </div>
          <input v-else v-model="userInput" type="text" :placeholder="`Enter ${currentTask.field.name}`" class="input input-bordered w-full" />
        </div>

        <div class="card-actions justify-between mt-4">
          <button @click="previousTask" class="btn btn-outline">Previous</button>
          <div>
            <button @click="submitContribution" class="btn btn-primary mr-2" :disabled="!isLoggedIn">
              {{ isLoggedIn ? 'Submit' : 'Login to Submit' }}
            </button>
            <button @click="nextTask" class="btn btn-ghost">Skip</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
