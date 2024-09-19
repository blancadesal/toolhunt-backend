<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  fieldNames: {
    type: Array,
    required: true
  },
  activeFields: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['updateFilters'])

const formattedFieldNames = computed(() => {
  return props.fieldNames.map(field => ({
    value: field,
    label: toHumanReadable(field)
  }))
})

const isCardOpen = ref(false)

const toggleCard = () => {
  isCardOpen.value = !isCardOpen.value
}

const toggleField = (field) => {
  if (props.activeFields.includes(field)) {
    emit('updateFilters', props.activeFields.filter(f => f !== field))
  } else {
    emit('updateFilters', [...props.activeFields, field])
  }
}

const clearFilter = () => {
  emit('updateFilters', [])
  isCardOpen.value = false
}
</script>

<template>
  <div class="field-filter w-full mb-4">
    <div class="flex gap-2 items-start">
      <button @click="toggleCard" class="btn btn-primary w-full">
        {{ activeFields.length > 0 ? `Filter by Task (${activeFields.length})` : 'Select Fields' }}
      </button>
    </div>

    <!-- Card for field selection -->
    <div v-if="isCardOpen" class="card bg-base-200 shadow-xl mt-4">
      <div class="card-body">
        <h2 class="card-title text-secondary">Select Fields</h2>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-2">
          <label v-for="field in formattedFieldNames" :key="field.value" class="cursor-pointer flex items-center">
            <input
              type="checkbox"
              :checked="activeFields.includes(field.value)"
              @change="toggleField(field.value)"
              class="checkbox checkbox-primary mr-2"
            />
            <span>{{ field.label }}</span>
          </label>
        </div>
        <div class="card-actions justify-end mt-4">
          <button @click="clearFilter" class="btn btn-secondary" :disabled="activeFields.length === 0">Clear All</button>
        </div>
      </div>
    </div>
  </div>
</template>