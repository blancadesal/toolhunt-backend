import type { Schema } from 'ajv'

interface FieldSchemaInfo {
  fieldSchema: ComputedRef<Schema | null>
  isArrayType: ComputedRef<boolean>
  fieldDescription: ComputedRef<string>
  fieldInputOptions: ComputedRef<{ value: string, label: string }[]>
  inputType: ComputedRef<string>
  placeholder: ComputedRef<string>
}

export function useFieldSchema(currentTask: ComputedRef<Task>, annotationsSchema: ComputedRef<AnnotationsSchema>): FieldSchemaInfo {
  const fieldSchema = computed(() => {
    const fieldName = currentTask.value?.field
    const fieldProperties = annotationsSchema.value?.schemas?.Annotations?.properties?.[fieldName]

    if (!fieldProperties) return null

    let fieldSchemaValue = {
      ...fieldProperties,
      $id: `#/fieldSchema/${fieldName}`,
    }

    if (fieldSchemaValue.nullable === true) {
      fieldSchemaValue = {
        oneOf: [
          { type: 'null' },
          { ...fieldSchemaValue, nullable: undefined },
        ],
      }
    }

    if (fieldName === 'repository') {
      fieldSchemaValue.format = 'uri'
    }

    return fieldSchemaValue
  })

  const isArrayType = computed(() => {
    const fieldName = currentTask.value?.field
    return annotationsSchema.value?.schemas?.Annotations?.properties?.[fieldName]?.type === 'array'
  })

  const fieldDescription = computed(() => {
    const fieldName = currentTask.value?.field
    const description = annotationsSchema.value?.schemas?.Annotations?.properties?.[fieldName]?.description
    return description ?? `Enter ${toHumanReadable(fieldName)}`
  })

  const fieldInputOptions = computed(() => {
    const fieldName = currentTask.value?.field
    const fieldSchema = annotationsSchema.value?.schemas?.Annotations?.properties?.[fieldName]

    if (!fieldSchema) return []

    let options = []

    if (fieldSchema.type === 'array' && fieldSchema.items?.$ref) {
      const enumName = fieldSchema.items.$ref.split('/').pop()
      options = annotationsSchema.value?.schemas?.[enumName]?.enum ?? []
    }
    else if (fieldSchema.allOf?.[0]?.$ref) {
      const enumName = fieldSchema.allOf[0].$ref.split('/').pop()
      options = annotationsSchema.value?.schemas?.[enumName]?.enum ?? []
    }

    return options.map((option: string) => ({
      value: option,
      label: toHumanReadable(option),
    }))
  })

  const inputType = computed(() => {
    const fieldName = currentTask.value?.field
    switch (fieldName) {
      case 'repository':
      case 'api_url':
      case 'bugtracker_url':
      case 'translate_url':
        return 'url'
      case 'deprecated':
      case 'experimental':
        return 'checkbox'
      case 'user_docs_url':
      case 'developer_docs_url':
        return 'languageUrl'
      default:
        return 'text'
    }
  })

  const placeholder = computed(() => {
    const fieldName = currentTask.value?.field
    switch (fieldName) {
      case 'repository':
        return 'Enter repository URL (e.g., https://github.com/username/repository)'
      case 'api_url':
        return 'Enter API URL'
      case 'bugtracker_url':
        return 'Enter bug tracker URL'
      case 'translate_url':
        return 'Enter translation interface URL'
      case 'icon':
        return 'Enter icon URL (e.g., https://commons.wikimedia.org/wiki/File:some_tool_logo_mini.svg)'
      case 'wikidata_qid':
        return 'Enter wikidata ID (e.g., Q43649390)'
      case 'user_docs_url':
        return 'Enter user documentation URL'
      case 'developer_docs_url':
        return 'Enter developer documentation URL'
      default:
        return `Enter ${fieldName}`
    }
  })

  return {
    fieldSchema,
    isArrayType,
    fieldDescription,
    fieldInputOptions,
    inputType,
    placeholder,
  }
}
