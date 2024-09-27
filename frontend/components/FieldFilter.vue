<script setup>
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

const toggleAllFields = () => {
  if (props.activeFields.length === props.fieldNames.length) {
    emit('updateFilters', [])
  } else {
    emit('updateFilters', [...props.fieldNames])
  }
}
</script>

<template>
  <div class="field-filter w-full flex flex-col">
    <div class="flex gap-2 items-start">
      <button
         class="btn btn-primary w-full"
         type="button"
         @click="toggleCard"
      >
        {{ activeFields.length > 0 ? `Filter by Annotation (${activeFields.length})` : 'Select Annotations' }}
      </button>
    </div>

    <!-- Card for field selection -->
    <div v-if="isCardOpen" class="card bg-base-200 shadow-xl mt-4 flex flex-col">
      <div class="card-body p-4">
        <div class="flex justify-between items-center mb-4">
          <h2 class="card-title text-secondary">Select Annotations</h2>
          <button
            class="btn btn-sm btn-secondary"
            type="button"
            @click="toggleAllFields"
          >
            {{ activeFields.length === fieldNames.length ? 'Clear All' : 'Select All' }}
          </button>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-2">
          <button
            v-for="field in formattedFieldNames"
            :key="field.value"
            type="button"
            class="cursor-pointer p-2 rounded-lg transition-colors duration-200 ease-in-out select-none w-full text-left"
            :class="{
              'bg-primary text-primary-content': activeFields.includes(field.value),
              'hover:bg-primary hover:bg-opacity-20': !activeFields.includes(field.value)
            }"
            @click="toggleField(field.value)"
          >
            {{ field.label }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
