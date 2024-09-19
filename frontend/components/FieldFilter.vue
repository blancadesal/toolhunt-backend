<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  fieldNames: {
    type: Array,
    required: true
  },
  appliedFields: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['applyFilter', 'clearFilter'])

const selectedFields = ref([])

const formattedFieldNames = computed(() => {
  return props.fieldNames.map(field => ({
    value: field,
    label: toHumanReadable(field)
  }))
})

const isCardOpen = ref(false)

watch(() => props.appliedFields, (newAppliedFields) => {
  selectedFields.value = [...newAppliedFields]
}, { immediate: true })

const toggleCard = () => {
  isCardOpen.value = !isCardOpen.value
}

const applyFilter = () => {
  emit('applyFilter', selectedFields.value)
  isCardOpen.value = false
}

const clearFilter = () => {
  selectedFields.value = []
  emit('clearFilter')
  isCardOpen.value = false
}
</script>

<template>
  <div class="field-filter w-full mb-4">
    <div class="flex gap-2 items-start">
      <button @click="toggleCard" class="btn btn-outline btn-secondary w-full">
        {{ selectedFields.length > 0 ? 'Filter by Task' : 'Select Fields' }}
      </button>
    </div>

    <!-- Card for field selection -->
    <div v-if="isCardOpen" class="card bg-base-100 shadow-xl mt-4">
      <div class="card-body">
        <h2 class="card-title">Select Fields</h2>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-2">
          <label v-for="field in formattedFieldNames" :key="field.value" class="cursor-pointer flex items-center">
            <input
              type="checkbox"
              v-model="selectedFields"
              :value="field.value"
              class="checkbox checkbox-secondary mr-2"
            />
            <span>{{ field.label }}</span>
          </label>
        </div>
        <div class="card-actions justify-end mt-4">
          <button @click="clearFilter" class="btn btn-outline">Clear</button>
          <button @click="applyFilter" class="btn btn-primary" :disabled="selectedFields.length === 0">Apply</button>
        </div>
      </div>
    </div>
  </div>
</template>