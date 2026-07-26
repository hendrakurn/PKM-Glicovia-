export function toIsoString(value: Date | string | number = new Date()): string {
  return new Date(value).toISOString();
}

export function formatDateOnly(value: Date | string | number = new Date()): string {
  return new Date(value).toISOString().slice(0, 10);
}
