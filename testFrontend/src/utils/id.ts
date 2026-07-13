let counter = 0;

/** Stable, collision-free id generator for client-only mock entities. */
export const generateId = (prefix = 'id'): string => {
  counter += 1;
  return `${prefix}_${Date.now().toString(36)}_${counter}`;
};
