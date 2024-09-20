<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

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
const cardRef = ref(null)

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

// Prevent scroll on the document body when the card is open
const preventDefault = (e) => {
  e.preventDefault()
}

const handleWheel = (e) => {
  if (!cardRef.value) return
  const { deltaY } = e
  const { scrollTop, scrollHeight, clientHeight } = cardRef.value
  
  if ((deltaY < 0 && scrollTop > 0) || (deltaY > 0 && scrollTop < scrollHeight - clientHeight)) {
    e.preventDefault()
  }
}

onMounted(() => {
  if (cardRef.value) {
    cardRef.value.addEventListener('wheel', handleWheel, { passive: false })
  }
  document.body.addEventListener('touchmove', preventDefault, { passive: false })
})

onBeforeUnmount(() => {
  if (cardRef.value) {
    cardRef.value.removeEventListener('wheel', handleWheel)
  }
  document.body.removeEventListener('touchmove', preventDefault)
})

// Utility function (assuming it's defined elsewhere)
function toHumanReadable(str) {
  // Convert snake_case or other formats to Human Readable
  return str.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
}
</script>

<template>
  <div class="field-filter w-full h-full flex flex-col">
    <div class="flex gap-2 items-start">
      <button 
        @click="toggleCard" 
        class="btn btn-primary w-full" 
        type="button"
      >
        {{ activeFields.length > 0 ? `Filter by Task (${activeFields.length})` : 'Select Fields' }}
      </button>
    </div>

    <!-- Card for field selection -->
    <div v-if="isCardOpen" class="card bg-base-200 shadow-xl mt-4 flex-grow flex flex-col" ref="cardRef">
      <div class="card-body flex-grow flex flex-col overflow-hidden">
        <h2 class="card-title text-secondary mb-4">Select Fields</h2>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-2 overflow-y-auto flex-grow">
          <button
            v-for="field in formattedFieldNames" 
            :key="field.value" 
            @click.stop="toggleField(field.value)"
            type="button"
            class="cursor-pointer p-2 rounded-lg transition-colors duration-200 ease-in-out select-none w-full text-left"
            :class="{
              'bg-primary text-primary-content': activeFields.includes(field.value),
              'hover:bg-primary hover:bg-opacity-20': !activeFields.includes(field.value)
            }"
          >
            {{ field.label }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Add any necessary styles here */
</style>