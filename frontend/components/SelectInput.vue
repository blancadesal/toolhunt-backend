<script setup>
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
</script>

<template>
  <select
    :value="selectedValue"
    @input="updateValue"
    @keydown="handleKeydown"
    class="select select-bordered w-full"
    :disabled="disabled"
  >
    <option disabled value="">{{ placeholder }}</option>
    <option v-for="option in options" :key="option.value" :value="option.value">
      {{ option.label }}
    </option>
  </select>
</template>
