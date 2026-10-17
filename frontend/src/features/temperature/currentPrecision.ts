/** Intl's decimal half-expand formatting agrees with Excel ROUND at decimal ties. */
export function formatCurrent(value: number, decimals = 0): string {
  const text = new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals, maximumFractionDigits: decimals, useGrouping: false,
  }).format(value);
  return Number(text) === 0 ? (0).toFixed(decimals) : text;
}
