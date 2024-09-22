import Ajv from 'ajv';
import addFormats from 'ajv-formats';

export function useInputValidation(fieldSchema: { value: any; }, isArrayType: { value: any; }) {
  const ajv = new Ajv({ allErrors: true, strictSchema: false, strictTypes: false });
  addFormats(ajv);

  const validationError = ref('');

  const validateInput = (input: string | any[]) => {
    if (fieldSchema.value) {
      try {
        const validate = ajv.compile(fieldSchema.value);
        if (isArrayType.value && Array.isArray(input) && input.length === 0) {
          return { isValid: false, error: 'Input cannot be empty' };
        }
        const isValid = validate(input);
        if (!isValid) {
          // Look for format or pattern errors
          const formatError = validate.errors?.find(e => e.keyword === 'format');
          const patternError = validate.errors?.find(e => e.keyword === 'pattern');

          if (formatError) {
            return { isValid: false, error: `Input must match format "${formatError.params.format}"` };
          } else if (patternError) {
            return { isValid: false, error: `Input must match pattern "${patternError.params.pattern}"` };
          }

          // If no format or pattern error, return a generic message
          return { isValid: false, error: 'Invalid input' };
        }
        return { isValid: true, error: null };
      } catch (e) {
        console.error('Error compiling validator for field:', e);
        return { isValid: true, error: null }; // If we can't validate, assume it's valid
      }
    }
    return { isValid: true, error: null };
  };

  const setValidationError = (error: string) => {
    validationError.value = error;
  };

  const clearValidationError = () => {
    validationError.value = '';
  };

  return {
    validateInput,
    validationError: computed(() => validationError.value),
    setValidationError,
    clearValidationError
  };
}
