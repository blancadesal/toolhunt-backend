<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  options: {
    type: Array,
    required: true
  },
  disabled: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: 'Select an option'
  }
});

const emit = defineEmits(['update:modelValue', 'enter']);

const selectedValue = ref(props.modelValue);

watch(() => props.modelValue, (newValue) => {
  selectedValue.value = newValue;
});

const updateValue = (event) => {
  selectedValue.value = event.target.value;
  emit('update:modelValue', selectedValue.value);
};

const handleKeydown = (event) => {
  if (event.key === 'Enter') {
    emit('enter', event);
  }
};

const selectRef = ref(null);

const focus = () => {
  if (selectRef.value) {
    selectRef.value.focus();
  }
};

defineExpose({ focus });
</script>

<template>
  <select
    ref="selectRef"
    :value="selectedValue"
    class="select select-bordered w-full"
    :disabled="disabled"
    @input="updateValue"
    @keydown="handleKeydown"
  >
    <option disabled value="">{{ placeholder }}</option>
    <option v-for="option in options" :key="option.value" :value="option.value">
      {{ option.label }}
    </option>
  </select>
</template>
