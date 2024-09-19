<script setup>
import { ref, computed } from 'vue'
import Fuse from 'fuse.js'

const props = defineProps({
  tools: {
    type: Array,
    required: true
  },
  modelValue: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

// Use a computed property to sync with `modelValue`
const selectedTools = computed({
  get() {
    return props.modelValue
  },
  set(val) {
    emit('update:modelValue', val)
  }
})

const searchQuery = ref('')
const searchResults = ref([])
const selectedIndex = ref(-1)

const fuse = computed(() => new Fuse(props.tools, {
  threshold: 0.4,
  distance: 100,
  minMatchCharLength: 2
}))

const performSearch = () => {
  if (searchQuery.value) {
    searchResults.value = fuse.value.search(searchQuery.value)
  } else {
    searchResults.value = []
  }
  selectedIndex.value = -1
}

const navigateResults = (direction) => {
  if (searchResults.value.length === 0) return

  if (direction === 'down') {
    selectedIndex.value = (selectedIndex.value + 1) % searchResults.value.length
  } else {
    selectedIndex.value = (selectedIndex.value - 1 + searchResults.value.length) % searchResults.value.length
  }
}

const selectResult = (index) => {
  if (typeof index === 'number') {
    selectedIndex.value = index
  }
  if (selectedIndex.value > -1) {
    const selectedTool = searchResults.value[selectedIndex.value].item
    if (!selectedTools.value.includes(selectedTool)) {
      selectedTools.value = [...selectedTools.value, selectedTool]
    }
    searchQuery.value = ''
    searchResults.value = []
    selectedIndex.value = -1
  }
}

const removeTool = (tool) => {
  selectedTools.value = selectedTools.value.filter(t => t !== tool)
}

// Remove applyFilter and clearFilter functions
</script>

<template>
  <div class="form-control w-full mb-8">
    <div class="flex flex-wrap gap-2 mb-2">
      <div v-for="tool in selectedTools" :key="tool" class="badge badge-lg badge-primary badge-outline flex items-center">
        {{ tool }}
        <button @click="removeTool(tool)" class="btn btn-xs btn-ghost btn-circle ml-2">✕</button>
      </div>
    </div>
    <div class="flex gap-2 items-start">
      <div class="dropdown flex-grow">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Select one or more tools..."
          class="input input-bordered w-full"
          @input="performSearch"
          @keydown.down.prevent="navigateResults('down')"
          @keydown.up.prevent="navigateResults('up')"
          @keydown.enter.prevent="selectResult"
          tabindex="0"
        />
        <ul v-if="searchResults.length" 
            class="dropdown-content menu p-2 shadow bg-base-200 rounded-box w-full mt-1 max-h-60 overflow-auto z-[1]">
          <li v-for="(result, index) in searchResults" :key="result.item">
            <a @click="selectResult(index)"
               :class="{ 'active': index === selectedIndex }">
              {{ result.item }}
            </a>
          </li>
        </ul>
      </div>
      <!-- Remove Filter and Clear buttons -->
    </div>
  </div>
</template>