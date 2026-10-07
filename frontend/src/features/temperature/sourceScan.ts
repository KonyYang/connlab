import type { WorkbookTable } from '../../api/temperature';

/** Scan identifiers are display values; worksheet row numbers remain the editing keys. */
export function sourceScan(table: WorkbookTable | null, sourceRow: number): string | null {
  const value = table?.rows[sourceRow - 1]?.[0];
  if (typeof value === 'number') return Number.isFinite(value) ? String(value) : null;
  return typeof value === 'string' && value.trim() ? value.trim() : null;
}

export function scanLabel(table: WorkbookTable | null, sourceRow: number): string {
  const scan = sourceScan(table, sourceRow);
  return scan === null ? 'Scan unavailable' : `Scan ${scan}`;
}

export function scanMessage(table: WorkbookTable | null, message: string, sourceRow?: number): string {
  if (!table) return message;
  // Structured review issues own their row key; plain API errors use the existing Row N prefix.
  if (sourceRow !== undefined) return message.replace(/^Row \d+(?=[:,])/, scanLabel(table, sourceRow));
  return message.replace(/\bRow (\d+)(?=[:,])/g, (_, row: string) => scanLabel(table, Number(row)));
}
