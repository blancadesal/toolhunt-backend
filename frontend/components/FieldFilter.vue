<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  fieldNames: {
    type: Array,
    required: true
  },
  modelValue: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['update:modelValue', 'applyFilter', 'clearFilters']);

const selectedFields = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

const showFieldFilter = ref(false);

const toggleFieldFilter = () => {
  showFieldFilter.value = !showFieldFilter.value;
};

const applyFieldFilter = () => {
  emit('applyFilter', selectedFields.value);
  showFieldFilter.value = false;
};

const clearFilters = () => {
  selectedFields.value = [];
  emit('clearFilters');
};

const formattedFieldNames = computed(() => {
  return props.fieldNames.map(field => ({
    value: field,
    label: toHumanReadable(field)
  }));
});

// Watch for changes in selectedFields and emit the update
watch(selectedFields, (newValue) => {
  emit('update:modelValue', newValue);
});
</script>

<template>
  <div class="field-filter w-full max-w-2xl mb-4">
    <div class="flex items-center">
      <button
        @click="toggleFieldFilter"
        :class="[
          'btn btn-sm mr-2',
          showFieldFilter ? 'btn-secondary' : 'btn-outline btn-secondary'
        ]"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
        </svg>
        {{ showFieldFilter ? 'Hide Filter' : 'Task Filter' }}
      </button>
      <button
        v-if="selectedFields.length > 0"
        @click="clearFilters"
        class="btn btn-sm btn-outline btn-primary"
      >
        Clear Filters ({{ selectedFields.length }})
      </button>
    </div>

    <div v-if="showFieldFilter" class="card bg-base-100 shadow-xl w-full mt-4">
      <div class="card-body">
        <h2 class="card-title text-xl mb-4">Filter by Task Types</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <div v-for="field in formattedFieldNames" :key="field.value" class="flex items-center">
            <input
              type="checkbox"
              :id="field.value"
              v-model="selectedFields"
              :value="field.value"
              class="checkbox checkbox-secondary border-2 mr-2"
            />
            <label :for="field.value" class="cursor-pointer text-m">{{ field.label }}</label>
          </div>
        </div>
        <div class="card-actions justify-end mt-6">
          <button
            @click="applyFieldFilter"
            class="btn btn-sm btn-secondary"
            :disabled="selectedFields.length === 0"
          >
            Apply Filter
          </button>
        </div>
      </div>
    </div>
  </div>
</template>