import Ajv from 'ajv';
import addFormats from 'ajv-formats';

interface Task {
  id: number | string;
  field: string;
}

interface FieldSchema {
  type?: string;
  format?: string;
  enum?: string[];
  items?: {
    $ref?: string;
  };
  allOf?: Array<{ $ref?: string } | FieldSchema>;
  pattern?: string;
  nullable?: boolean;
}

interface AnnotationsSchema {
  schemas: {
    Annotations: {
      properties: Record<string, FieldSchema>;
    };
    [key: string]: any;
  };
}

export function useInputHandling(
  currentTask: ComputedRef<Task | null>,
  isArrayType: ComputedRef<boolean>,
  fieldSchema: ComputedRef<FieldSchema | null>,
  annotationsSchema: ComputedRef<AnnotationsSchema>
) {
  const ajv = new Ajv({ allErrors: true, strictSchema: false, strictTypes: false });
  addFormats(ajv);

  const taskInputs = ref<Record<string | number, string | string[]>>({});
  const validationError = ref<string>('');

  const currentUserInput = computed<string | string[]>({
    get: () => {
      if (currentTask.value) {
        const input = taskInputs.value[currentTask.value.id];
        if (isArrayType.value) {
          return Array.isArray(input) ? input : [];
        }
        return input ?? '';
      }
      return '';
    },
    set: (value: string | string[]) => {
      if (currentTask.value) {
        taskInputs.value[currentTask.value.id] = value;
      }
    }
  });

  watch(() => annotationsSchema.value, (newSchema) => {
    if (newSchema && newSchema.schemas) {
      Object.entries(newSchema.schemas).forEach(([key, schema]) => {
        ajv.addSchema(schema, `#/schemas/${key}`);
      });
    }
  }, { immediate: true });

  const addArrayItem = () => {
    if (isArrayType.value) {
      const newInput = Array.isArray(currentUserInput.value) ? [...currentUserInput.value, ''] : [''];
      currentUserInput.value = newInput;
    }
  };

  const removeArrayItem = (index: number) => {
    if (isArrayType.value && Array.isArray(currentUserInput.value)) {
      const newInput = [...currentUserInput.value];
      newInput.splice(index, 1);
      currentUserInput.value = newInput;
    }
  };

  const resetTaskInputs = () => {
    taskInputs.value = {};
    validationError.value = '';
  };

  const validateInput = (): boolean => {
    validationError.value = '';

    if (!fieldSchema.value || !currentTask.value) {
      return true; // If no schema is provided, assume the input is valid
    }

    const input = currentUserInput.value;
    const fieldName = currentTask.value.field;

    try {
      let schemaToValidate = fieldSchema.value;

      // Handle allOf case
      if (schemaToValidate.allOf) {
        schemaToValidate = {
          type: 'string',
          enum: schemaToValidate.allOf.flatMap(ref => {
            if ('$ref' in ref) {
              const enumName = ref.$ref?.split('/').pop();
              return enumName ? annotationsSchema.value.schemas[enumName]?.enum || [] : [];
            }
            return [];
          })
        };
      }

      // Ensure type is always defined
      if (!schemaToValidate.type) {
        schemaToValidate.type = 'string';
      }

      // Handle nullable fields
      if (schemaToValidate.nullable) {
        schemaToValidate = {
          allOf: [
            { type: 'null' },
            schemaToValidate
          ]
        };
      }

      const validate = ajv.compile(schemaToValidate);
      const isValid = validate(input);

      if (!isValid) {
        validationError.value = ajv.errorsText(validate.errors);
        return false;
      }

      // Additional custom validations
      if (isArrayType.value && Array.isArray(input) && input.length === 0) {
        validationError.value = 'At least one item is required';
        return false;
      }

      // Specific validation for repository field
      if (fieldName === 'repository') {
        try {
          new URL(input as string);
        } catch {
          validationError.value = 'Invalid URL format for repository';
          return false;
        }
      }

      return true;
    } catch (error) {
      console.error('Error during validation:', error);
      validationError.value = 'An error occurred during validation';
      return false;
    }
  };

  return {
    taskInputs,
    currentUserInput,
    addArrayItem,
    removeArrayItem,
    resetTaskInputs,
    validateInput,
    validationError
  };
}