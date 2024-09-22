<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: [String, Boolean, Number],
    default: ''
  },
  type: {
    type: String,
    default: 'text'
  },
  placeholder: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:modelValue', 'enter']);

const inputValue = ref(props.modelValue);

watch(() => props.modelValue, (newValue) => {
  inputValue.value = newValue;
});

const updateValue = (event) => {
  const value = props.type === 'checkbox' ? event.target.checked : event.target.value;
  inputValue.value = value;
  emit('update:modelValue', value);
};

const handleKeydown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    emit('enter', event);
  }
};

const inputRef = ref(null);

const focus = () => {
  if (inputRef.value) {
    inputRef.value.focus();
  }
};

defineExpose({ focus });
</script>

<template>
  <input
    v-if="type !== 'checkbox'"
    ref="inputRef"
    :type="type"
    :value="inputValue"
    @input="updateValue"
    @keydown="handleKeydown"
    :placeholder="placeholder"
    :disabled="disabled"
    class="input input-bordered w-full"
  />
  <label v-else class="cursor-pointer label">
    <span class="label-text">{{ placeholder }}</span>
    <input
      ref="inputRef"
      type="checkbox"
      :checked="inputValue"
      @change="updateValue"
      :disabled="disabled"
      class="checkbox checkbox-primary"
    />
  </label>
</template>
