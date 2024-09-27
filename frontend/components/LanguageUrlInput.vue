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
  emit('update:modelValue', [...languageUrlPairs.value]);
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

const updatePair = (index, field, value) => {
  languageUrlPairs.value[index][field] = value;
  updateModelValue();
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
    <div v-for="(pair, index) in languageUrlPairs" :key="index" class="flex mb-2">
      <input
        :value="pair.language"
        @input="(e) => updatePair(index, 'language', e.target.value)"
        type="text"
        placeholder="Language (e.g., en)"
        class="input input-bordered w-1/4 mr-2"
        :disabled="disabled"
        @keydown="handleKeydown"
      />
      <input
        :value="pair.url"
        @input="(e) => updatePair(index, 'url', e.target.value)"
        type="url"
        placeholder="URL"
        class="input input-bordered flex-1 mr-2"
        :disabled="disabled"
        @keydown="handleKeydown"
      />
      <button 
        v-if="languageUrlPairs.length > 1"
        @click="removePair(index)" 
        class="btn btn-error" 
        :disabled="disabled"
      >
        Remove
      </button>
    </div>
    <button @click="addPair" class="btn btn-primary mt-2" :disabled="disabled">Add Language-URL Pair</button>
  </div>
</template>
