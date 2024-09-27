<script setup>
import { ref, watch, onMounted } from 'vue';

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  disabled: Boolean
});

const emit = defineEmits(['update:modelValue', 'enter']);

const languageUrlPairs = ref([{ language: '', url: '' }]);

onMounted(() => {
  if (props.modelValue.length) {
    languageUrlPairs.value = props.modelValue;
  }
});

watch(() => props.modelValue, (newValue) => {
  if (newValue.length) {
    languageUrlPairs.value = newValue;
  } else if (languageUrlPairs.value.length === 0) {
    languageUrlPairs.value = [{ language: '', url: '' }];
  }
}, { deep: true });

const updateModelValue = () => {
  emit('update:modelValue', languageUrlPairs.value.filter(pair => pair.language || pair.url));
};

const addPair = () => {
  languageUrlPairs.value.push({ language: '', url: '' });
  updateModelValue();
};

const removePair = (index) => {
  if (languageUrlPairs.value.length > 1) {
    languageUrlPairs.value.splice(index, 1);
    updateModelValue();
  }
};

const handleKeydown = (event) => {
  if (event.key === 'Enter') {
    event.preventDefault();
    emit('enter', event);
  }
};
</script>

<template>
  <div>
    <div v-for="(pair, index) in languageUrlPairs" :key="index" class="flex mb-2 items-center">
      <input
        :value="pair.language"
        @input="(e) => { pair.language = e.target.value; updateModelValue(); }"
        type="text"
        placeholder="Language (e.g., en)"
        class="input input-bordered w-1/4 mr-2"
        :disabled="disabled"
        @keydown="handleKeydown"
      />
      <input
        :value="pair.url"
        @input="(e) => { pair.url = e.target.value; updateModelValue(); }"
        type="url"
        placeholder="URL"
        class="input input-bordered flex-1 mr-2"
        :disabled="disabled"
        @keydown="handleKeydown"
      />
      <button 
        v-if="languageUrlPairs.length > 1"
        @click="removePair(index)" 
        class="btn btn-ghost btn-sm p-1 h-8 w-8 min-h-0 hover:bg-base-200"
        :disabled="disabled"
        title="Remove"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
    <button @click="addPair" class="btn btn-outline btn-sm mt-2" :disabled="disabled">
      Add Language
    </button>
  </div>
</template>
