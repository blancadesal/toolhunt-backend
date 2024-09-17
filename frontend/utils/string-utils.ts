// utils/stringUtils.ts

/**
 * Converts a string from snake_case or camelCase to a human-readable format.
 * @param {string} str - The input string to convert.
 * @returns {string} The converted human-readable string.
 */
export const toHumanReadable = (str: string): string => {
  if (str.includes('::')) {
    return str.split('::').map(part => toHumanReadable(part)).join(' - ');
  }
  return str
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};
