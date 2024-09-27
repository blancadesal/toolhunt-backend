<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  options: {
    type: Array,
    required: true
  },
  disabled: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:modelValue', 'enter']);

const selectedValues = ref(props.modelValue);

watch(() => props.modelValue, (newValue) => {
  selectedValues.value = newValue;
});

const updateValue = (option) => {
  const index = selectedValues.value.indexOf(option.value);
  if (index === -1) {
    selectedValues.value.push(option.value);
  } else {
    selectedValues.value.splice(index, 1);
  }
  emit('update:modelValue', selectedValues.value);
};

const handleKeydown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    emit('enter', event);
  }
};

const firstCheckboxRef = ref(null);

const focus = () => {
  if (firstCheckboxRef.value) {
    firstCheckboxRef.value.focus();
  }
};

defineExpose({ focus });
</script>

<template>
  <div
    class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2"
    @keydown="handleKeydown"
  >
    <div v-for="(option, index) in options" :key="option.value" class="flex items-center">
      <input
        :id="`checkbox-${option.value}`"
        :ref="index === 0 ? (el) => { firstCheckboxRef = el } : undefined"
        type="checkbox"
        :value="option.value"
        :checked="selectedValues.includes(option.value)"
        class="checkbox checkbox-primary border-2 mr-2"
        :disabled="disabled"
        @change="updateValue(option)"
      >
      <label :for="`checkbox-${option.value}`" class="cursor-pointer">{{ option.label }}</label>
    </div>
  </div>
</template>
