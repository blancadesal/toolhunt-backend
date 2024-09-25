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

const showConfirmation = ref(false);
const showSuccess = ref(false);

const isSubmitDisabled = computed(() => {
  return props.isToolReported || (!reportAttributes.value.deprecated && !reportAttributes.value.experimental);
});

const submitReport = () => {
  showConfirmation.value = true;
};

const confirmSubmit = () => {
  emit('submit', reportAttributes.value);
  showConfirmation.value = false;
  showSuccess.value = true;
  setTimeout(() => {
    closeModal();
  }, 3000);
};

const closeModal = () => {
  showConfirmation.value = false;
  showSuccess.value = false;
  emit('close');
};

watch(() => props.reportedAttributes, (newValue) => {
  reportAttributes.value = {
    deprecated: newValue.deprecated || false,
    experimental: newValue.experimental || false
  };
}, { immediate: true });

watch(() => props.isOpen, (newValue) => {
  if (newValue) {
    reportAttributes.value = {
      deprecated: props.reportedAttributes.deprecated || false,
      experimental: props.reportedAttributes.experimental || false
    };
  }
});

const tooltips = {
  deprecated: "The tool is no longer maintained or recommended for use.",
  experimental: "The tool is in an early stage and may be unstable or change significantly."
};
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-auto bg-black bg-opacity-50 flex items-center justify-center">
    <div class="modal modal-open">
      <div class="modal-box relative">
        <h3 class="font-bold text-lg mb-4">Flag Tool: {{ toolName }}</h3>
        <div v-if="!showConfirmation && !showSuccess">
          <div class="form-control">
            <label class="label cursor-pointer justify-start items-center">
              <input
                type="checkbox"
                v-model="reportAttributes.deprecated"
                class="checkbox checkbox-warning"
                :disabled="isToolReported"
              />
              <span class="label-text ml-2 flex-grow">
                Deprecated
                <div class="dropdown dropdown-hover dropdown-right inline-block ml-1">
                  <label tabindex="0" class="text-info cursor-help">&#9432;</label>
                  <div tabindex="0" class="dropdown-content z-[1] card card-compact w-64 p-2 shadow bg-primary text-primary-content">
                    <div class="card-body">
                      <p>{{ tooltips.deprecated }}</p>
                    </div>
                  </div>
                </div>
              </span>
            </label>
          </div>
          <div class="form-control">
            <label class="label cursor-pointer justify-start items-center">
              <input
                type="checkbox"
                v-model="reportAttributes.experimental"
                class="checkbox checkbox-warning"
                :disabled="isToolReported"
              />
              <span class="label-text ml-2 flex-grow">
                Experimental
                <div class="dropdown dropdown-hover dropdown-right inline-block ml-1">
                  <label tabindex="0" class="text-info cursor-help">&#9432;</label>
                  <div tabindex="0" class="dropdown-content z-[1] card card-compact w-64 p-2 shadow bg-primary text-primary-content">
                    <div class="card-body">
                      <p>{{ tooltips.experimental }}</p>
                    </div>
                  </div>
                </div>
              </span>
            </label>
          </div>
          <div class="modal-action">
            <button @click="closeModal" class="btn btn-ghost">
              {{ isToolReported ? 'Close' : 'Cancel' }}
            </button>
            <button
              @click="submitReport"
              class="btn btn-warning"
              :disabled="isSubmitDisabled"
            >
              {{ isToolReported ? 'Flagged' : 'Submit' }}
            </button>
          </div>
        </div>
        <div v-else-if="showConfirmation" class="text-center">
          <p class="mb-4">Are you sure you want to flag this tool? This action cannot be undone and will remove this tool from future batches.</p>
          <div class="flex justify-center space-x-4">
            <button @click="showConfirmation = false" class="btn btn-ghost">Cancel</button>
            <button @click="confirmSubmit" class="btn btn-warning">Confirm</button>
          </div>
        </div>
        <div v-else-if="showSuccess" class="text-center">
          <div class="alert alert-success">
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <div>
              <h3 class="font-bold">Report Submitted Successfully</h3>
              <div class="text-xs">Thank you for your feedback. The tool has been reported and associated tasks will be removed.</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
