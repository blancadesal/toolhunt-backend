<script setup>

const props = defineProps({
  isOpen: Boolean,
  toolName: {
    type: String,
    default: ''
  },
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
  return (!reportAttributes.value.deprecated && !reportAttributes.value.experimental) ||
         (reportAttributes.value.deprecated === props.reportedAttributes.deprecated &&
          reportAttributes.value.experimental === props.reportedAttributes.experimental);
});

const submitReport = () => {
  showConfirmation.value = true;
};

const confirmSubmit = () => {
  emit('submit', reportAttributes.value);
  showConfirmation.value = false;
  showSuccess.value = true;
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
    showSuccess.value = false;
  }
});

const tooltips = {
  deprecated: "The tool is no longer maintained or recommended for use.",
  experimental: "The tool is in an early stage and may be unstable or change significantly."
};
</script>

<template>
  <div class="modal modal-open" @click.self="closeModal">
    <div class="modal-box relative" @click.stop>
      <h3 class="font-bold text-lg mb-4">Flag Tool: {{ toolName }}</h3>
      <div v-if="!showConfirmation && !showSuccess">
        <div class="form-control">
          <label class="label cursor-pointer justify-start items-center">
            <input
              v-model="reportAttributes.deprecated"
              type="checkbox"
              class="checkbox checkbox-warning"
              :disabled="props.reportedAttributes.deprecated"
            >
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
              v-model="reportAttributes.experimental"
              type="checkbox"
              class="checkbox checkbox-warning"
              :disabled="props.reportedAttributes.experimental"
            >
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
          <button class="btn btn-ghost" @click="closeModal">Cancel</button>
          <button
            class="btn btn-warning"
            :disabled="isSubmitDisabled"
            @click="submitReport"
          >
            Submit
          </button>
        </div>
      </div>
      <div v-else-if="showConfirmation" class="text-left">
        <p class="mb-4">Are you sure you want to flag this tool? This action cannot be undone and will remove this tool from future task batches.</p>
        <div class="flex justify-center space-x-4">
          <button class="btn btn-ghost" @click="showConfirmation = false">Cancel</button>
          <button class="btn btn-warning" @click="confirmSubmit">Confirm</button>
        </div>
      </div>
      <div v-else-if="showSuccess" class="text-center">
        <div class="alert alert-success">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <div>
            <h3 class="font-bold">Tool Flagged Successfully</h3>
            <div class="text-xs">Thank you for your feedback. The tool has been flagged and will be removed from future batches.</div>
          </div>
        </div>
        <button class="btn btn-primary mt-4" @click="closeModal">Dismiss</button>
      </div>
    </div>
  </div>
</template>
