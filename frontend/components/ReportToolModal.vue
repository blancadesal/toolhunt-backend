<script setup>

const props = defineProps({
  isOpen: Boolean,
  toolName: String,
  isToolReported: Boolean,
  reportedAttributes: {
    type: Object,
    default: () => ({})
  },
});

const emit = defineEmits(['close', 'submit']);

const reportAttributes = ref({
  deprecated: false,
  experimental: false,
});

const modalRef = ref(null);

const isSubmitDisabled = computed(() => {
  return props.isToolReported || (!reportAttributes.value.deprecated && !reportAttributes.value.experimental);
});

const handleModalClick = (event) => {
  if (modalRef.value && !modalRef.value.contains(event.target)) {
    emit('close');
  }
};

const submitReport = () => {
  emit('submit', reportAttributes.value);
};

// Watch for changes in reportedAttributes prop
watch(() => props.reportedAttributes, (newValue) => {
  reportAttributes.value = {
    deprecated: newValue.deprecated || false,
    experimental: newValue.experimental || false
  };
}, { immediate: true });

// Watch for changes in isOpen prop
watch(() => props.isOpen, (newValue) => {
  if (newValue) {
    reportAttributes.value = {
      deprecated: props.reportedAttributes.deprecated || false,
      experimental: props.reportedAttributes.experimental || false
    };
  }
});
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click="handleModalClick">
    <div ref="modalRef" class="modal-box bg-base-100 p-6 rounded-lg shadow-xl w-96">
      <h3 class="font-bold text-lg mb-4">Report Tool: {{ toolName }}</h3>
      <div class="form-control">
        <label class="label cursor-pointer">
          <span class="label-text">Deprecated</span>
          <input 
            type="checkbox" 
            v-model="reportAttributes.deprecated" 
            class="checkbox checkbox-warning" 
            :disabled="isToolReported"
            :class="{'checkbox-disabled': isToolReported}"
          />
        </label>
      </div>
      <div class="form-control">
        <label class="label cursor-pointer">
          <span class="label-text">Experimental</span>
          <input 
            type="checkbox" 
            v-model="reportAttributes.experimental" 
            class="checkbox checkbox-warning" 
            :disabled="isToolReported"
            :class="{'checkbox-disabled': isToolReported}"
          />
        </label>
      </div>
      <div class="modal-action mt-6">
        <button @click="$emit('close')" class="btn btn-ghost">
          {{ isToolReported ? 'Close' : 'Cancel' }}
        </button>
        <button 
          @click="submitReport" 
          class="btn btn-warning" 
          :disabled="isSubmitDisabled"
        >
          {{ isToolReported ? 'Reported' : 'Submit Report' }}
        </button>
      </div>
    </div>
  </div>
</template>
