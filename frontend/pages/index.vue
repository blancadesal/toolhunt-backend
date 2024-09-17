<script setup>
import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import { debounce } from 'lodash-es';

const { isLoggedIn } = useAuth();
const { tasks, fieldNames, annotationsSchema, fetchTasks, fetchFieldNames, fetchAnnotationsSchema } = useToolhuntApi();

const currentTaskIndex = ref(0);
const searchQuery = ref('');
const selectedFields = ref([]);
const isLoading = ref(true);
const taskCardRef = ref(null);

const isArrayType = computed(() => {
  if (!annotationsSchema.value || !tasks.value[currentTaskIndex.value] || !tasks.value[currentTaskIndex.value].field) {
    return false;
  }
  const fieldName = tasks.value[currentTaskIndex.value].field;
  const fieldProperties = annotationsSchema.value.schemas.Annotations.properties;
  return fieldProperties[fieldName]?.type === 'array';
});

const ajv = new Ajv({ allErrors: true, strictSchema: false, strictTypes: false });
addFormats(ajv);

const fieldSchema = ref(null);
const validateField = ref(null);
const validationError = ref('');

watch(annotationsSchema, (newValue) => {
  if (newValue) {
    const schemas = newValue.schemas;
    for (const [key, schema] of Object.entries(schemas)) {
      ajv.addSchema(schema, `#/schemas/${key}`);
    }
  }
});

watch([annotationsSchema, tasks, currentTaskIndex], ([annotationsSchemaValue, tasksValue, currentTaskIndexValue]) => {
  if (annotationsSchemaValue && tasksValue[currentTaskIndexValue] && tasksValue[currentTaskIndexValue].field) {
    const fieldName = tasksValue[currentTaskIndexValue].field;
    const annotationsProperties = annotationsSchemaValue.schemas.Annotations.properties;
    if (annotationsProperties && annotationsProperties[fieldName]) {
      let fieldSchemaValue = {
        ...annotationsProperties[fieldName],
        $id: `#/fieldSchema/${fieldName}`
      };

      if (fieldSchemaValue.nullable === true) {
        fieldSchemaValue = {
          oneOf: [
            { type: 'null' },
            { ...fieldSchemaValue, nullable: undefined }
          ]
        };
      }

      if (fieldName === 'repository') {
        fieldSchemaValue.format = 'uri';
      }

      fieldSchema.value = fieldSchemaValue;
    } else {
      fieldSchema.value = null;
    }
  } else {
    fieldSchema.value = null;
  }
});

const validateInput = (input) => {
  if (fieldSchema.value) {
    try {
      const validate = ajv.compile(fieldSchema.value);
      if (isArrayType.value && Array.isArray(input) && input.length === 0) {
        return false;
      }
      return validate(input);
    } catch (e) {
      console.error('Error compiling validator for field:', e);
      return true; // If we can't validate, assume it's valid
    }
  }
  return true;
};

const searchTools = () => {
  // Implement search functionality
};

const applyFieldFilter = async (filters) => {
  selectedFields.value = filters;
  isLoading.value = true;
  await fetchTasks(null, filters.length > 0 ? filters.join(',') : null);
  currentTaskIndex.value = 0; // Reset to the first task after applying filters
  isLoading.value = false;
};

const clearFilters = async () => {
  selectedFields.value = [];
  isLoading.value = true;
  await fetchTasks();
  currentTaskIndex.value = 0; // Reset to the first task after clearing filters
  isLoading.value = false;
};

const fieldInputOptions = computed(() => {
  if (!annotationsSchema.value || !tasks.value[currentTaskIndex.value] || !tasks.value[currentTaskIndex.value].field) {
    return [];
  }

  const fieldName = tasks.value[currentTaskIndex.value].field;
  const fieldProperties = annotationsSchema.value.schemas.Annotations.properties;
  const fieldSchema = fieldProperties[fieldName];

  let options = [];

  if (fieldSchema?.type === 'array' && fieldSchema.items?.$ref) {
    const enumName = fieldSchema.items.$ref.split('/').pop();
    const enumSchema = annotationsSchema.value.schemas[enumName];
    options = enumSchema?.enum || [];
  } else if (fieldSchema?.allOf && fieldSchema.allOf[0]?.$ref) {
    const enumName = fieldSchema.allOf[0].$ref.split('/').pop();
    const enumSchema = annotationsSchema.value.schemas[enumName];
    options = enumSchema?.enum || [];
  }

  return options.map(option => ({
    value: option,
    label: toHumanReadable(option)
  }));
});

const loadNewBatch = async () => {
  isLoading.value = true;
  tasks.value = [];
  currentTaskIndex.value = 0;
  if (taskCardRef.value) {
    taskCardRef.value.resetSubmittedTasks();
  }
  await fetchTasks(null, selectedFields.value.length > 0 ? selectedFields.value.join(',') : null);
  isLoading.value = false;
};

onMounted(async () => {
  isLoading.value = true;
  await fetchTasks();
  await fetchFieldNames();
  await fetchAnnotationsSchema();
  isLoading.value = false;
});
</script>

<template>
  <div class="flex flex-col min-h-screen items-center p-4">
    <h1 class="text-4xl font-bold mt-4 mb-4">Welcome to Toolhunt!</h1>
    <div class="w-full max-w-3xl mb-4 mt-4">
        <div class="relative">
          <input v-model="searchQuery" type="text" placeholder="Search for a tool" class="input input-bordered w-full pr-10" />
          <button @click="searchTools" class="absolute right-2 top-1/2 transform -translate-y-1/2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
          </button>
        </div>
    </div>

    <FieldFilter
      :field-names="fieldNames"
      v-model="selectedFields"
      @apply-filter="applyFieldFilter"
      @clear-filters="clearFilters"
    />

    <div v-if="isLoading" class="text-center mt-8">
      <p class="text-xl">Loading tasks...</p>
    </div>

    <div v-else-if="tasks.length === 0" class="text-center mt-8">
      <p class="text-xl">No tasks available. Try clearing filters or refreshing the page.</p>
    </div>

    <TaskCard
      v-else-if="tasks.length > 0"
      ref="taskCardRef"
      :tasks="tasks"
      :current-task-index="currentTaskIndex"
      :annotations-schema="annotationsSchema"
      :field-input-options="fieldInputOptions"
      :is-array-type="isArrayType"
      :validate-input="validateInput"
      @update:current-task-index="currentTaskIndex = $event"
      @load-new-batch="loadNewBatch"
    />
  </div>
</template>
