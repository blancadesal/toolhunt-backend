<script setup>
import { ref, computed } from 'vue'
import Fuse from 'fuse.js'

const props = defineProps({
  tools: {
    type: Array,
    required: true
  },
  activeTools: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['updateFilters'])

const searchQuery = ref('')
const searchResults = ref([])
const selectedIndex = ref(-1)
const isCardOpen = ref(false)

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
    if (!props.activeTools.includes(selectedTool)) {
      emit('updateFilters', [...props.activeTools, selectedTool])
    }
    searchQuery.value = ''
    searchResults.value = []
    selectedIndex.value = -1
  }
}

const clearFilter = () => {
  emit('updateFilters', [])
  isCardOpen.value = false
}

const toggleCard = () => {
  isCardOpen.value = !isCardOpen.value
}
</script>

<template>
  <div class="tool-filter w-full mb-4">
    <div class="flex gap-2 items-start">
      <button @click="toggleCard" class="btn btn-primary w-full">
        {{ activeTools.length > 0 ? `Filter by Tool (${activeTools.length})` : 'Select Tools' }}
      </button>
    </div>

    <!-- Card for tool selection -->
    <div v-if="isCardOpen" class="card  bg-base-200 shadow-xl mt-4">
      <div class="card-body">
        <h2 class="card-title text-secondary">Select Tools</h2>
        <div class="form-control w-full">
          <div class="flex gap-2 items-start">
            <div class="dropdown flex-grow">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search for tools..."
                class="input input-bordered input-primary w-full"
                @input="performSearch"
                @keydown.down.prevent="navigateResults('down')"
                @keydown.up.prevent="navigateResults('up')"
                @keydown.enter.prevent="selectResult"
                tabindex="0"
              />
              <ul v-if="searchResults.length" 
                  class="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-full mt-1 max-h-60 overflow-auto z-[1]">
                <li v-for="(result, index) in searchResults" :key="result.item">
                  <a @click="selectResult(index)"
                     :class="{ 'bg-accent text-accent-content': index === selectedIndex }">
                    {{ result.item }}
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div class="card-actions justify-end mt-4">
          <button @click="clearFilter" class="btn btn-secondary" :disabled="activeTools.length === 0">Clear All</button>
        </div>
      </div>
    </div>
  </div>
</template>