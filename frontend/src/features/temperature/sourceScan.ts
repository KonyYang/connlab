import type { DataIssue, WorkbookTable } from '../../api/temperature';

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

/** Compact display only: callers retain every original issue and worksheet-row editing key. */
export function reviewMessages(table: WorkbookTable | null, issues: DataIssue[]) {
  const messages: { severity: string; message: string }[] = [];
  const unpowered = (issue: DataIssue) => issue.code === 'zero_current' && issue.severity === 'warning';
  const scanNumber = (row: number) => {
    const scan = sourceScan(table, row);
    return scan !== null && /^\d+$/.test(scan) && Number.isSafeInteger(Number(scan)) ? Number(scan) : null;
  };
  for (let index = 0; index < issues.length; index++) {
    const issue = issues[index];
    if (!unpowered(issue)) {
      messages.push({ severity: issue.severity, message: scanMessage(table, issue.message, issue.source_row) });
      continue;
    }
    let last = issue;
    while (index + 1 < issues.length) {
      const next = issues[index + 1];
      const previousScan = scanNumber(last.source_row), nextScan = scanNumber(next.source_row);
      if (!unpowered(next) || next.source_row !== last.source_row + 1 || previousScan === null
        || nextScan !== previousScan + 1) break;
      last = next;
      index++;
    }
    const label = last === issue ? scanLabel(table, issue.source_row)
      : `${scanLabel(table, issue.source_row)}~${sourceScan(table, last.source_row)}`;
    messages.push({ severity: issue.severity, message: `${label}: |current| < 0.1 A is treated as unpowered.` });
  }
  return messages;
}
