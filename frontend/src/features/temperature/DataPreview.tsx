import { useState } from 'react';
import type { DataIssue, DataSelection, WorkbookTable } from '../../api/temperature';
import { columnLetter } from './ChannelMapping';

export function DataPreview({ table, selection, issues, disabled, onChange }: {
  table: WorkbookTable; selection: DataSelection; issues: DataIssue[]; disabled: boolean;
  onChange: (patch: Partial<DataSelection>) => void;
}) {
  const [selected, setSelected] = useState<number[]>([]);
  const [page, setPage] = useState(0);
  const [range, setRange] = useState('');
  const [rangeError, setRangeError] = useState('');
  const [allColumns, setAllColumns] = useState(false);
  const length = Math.max(0, selection.end_row - selection.start_row + 1);
  const totalPages = Math.max(1, Math.ceil(length / 50));
  const currentPage = Math.min(page, totalPages - 1);
  const start = selection.start_row + currentPage * 50;
  const rowNumbers = Array.from({ length: Math.max(0, Math.min(50, selection.end_row - start + 1)) }, (_, i) => start + i);
  const columns = allColumns ? Array.from({ length: Math.max(...table.rows.map(row => row.length)) }, (_, i) => i + 1)
    : [...selection.temperature_columns, selection.ambient_column, selection.current_column];
  const excluded = new Set(selection.excluded_rows);
  function selectRange() {
    const result = new Set<number>();
    for (const token of range.split(',')) {
      const match = token.trim().match(/^(\d+)(?:\s*-\s*(\d+))?$/);
      if (!match) { setRangeError('Enter original row numbers, for example 32-50, 82.'); return; }
      const first = Number(match[1]), last = Number(match[2] ?? first);
      if (first < selection.start_row || last > selection.end_row || first > last) { setRangeError('Choose rows inside the data range.'); return; }
      for (let row = first; row <= last; row++) result.add(row);
    }
    setSelected([...result]); setRangeError('');
  }
  return <details className="temperature-detail" open>
    <summary>Data Preview <span>{length - excluded.size} Included / {excluded.size} Excluded Rows</span></summary>
    <div className="temperature-actions">
      <label>Rows To Select<input aria-label="Rows To Select" value={range} disabled={disabled} placeholder="32-50, 82" onChange={event => setRange(event.target.value)} /></label>
      <button type="button" onClick={selectRange} disabled={disabled || !range}>Select Rows</button>
      <button type="button" disabled={disabled || !selected.length} onClick={() => { onChange({ excluded_rows: [...new Set([...excluded, ...selected])].sort((a, b) => a - b) }); setSelected([]); }}>Exclude Selected Rows</button>
      <button type="button" disabled={disabled || !selected.some(row => excluded.has(row))} onClick={() => { onChange({ excluded_rows: [...excluded].filter(row => !selected.includes(row)) }); setSelected([]); }}>Restore Selected Rows</button>
      <button type="button" disabled={disabled || !excluded.size} onClick={() => onChange({ excluded_rows: [] })}>Restore All Rows</button>
      <label className="temperature-check"><input type="checkbox" checked={allColumns} onChange={event => setAllColumns(event.target.checked)} />All Source Columns</label>
    </div>
    {rangeError && <p role="alert" className="temperature-error">{rangeError}</p>}
    <div className="temperature-table-scroll" tabIndex={0} aria-label="Scanner Data Preview">
      <table><thead><tr><th><input aria-label="Select Visible Rows" type="checkbox" checked={rowNumbers.length > 0 && rowNumbers.every(row => selected.includes(row))}
        disabled={disabled} onChange={event => setSelected(event.target.checked ? [...new Set([...selected, ...rowNumbers])] : selected.filter(row => !rowNumbers.includes(row)))} /></th><th>Original Row</th>
        {columns.map((column, index) => <th key={`${column}-${index}`}>{columnLetter(column)}<br />{String(table.rows[selection.header_row - 1]?.[column - 1] ?? '')}</th>)}
      </tr></thead><tbody>{rowNumbers.map(row => {
        const flagged = issues.some(issue => issue.source_row === row);
        return <tr key={row} className={excluded.has(row) ? 'is-excluded' : flagged ? 'needs-review' : undefined}>
          <td><input type="checkbox" aria-label={`Select Row ${row}`} disabled={disabled} checked={selected.includes(row)} onChange={event => setSelected(old => event.target.checked ? [...old, row] : old.filter(value => value !== row))} /></td>
          <th scope="row">{row}{excluded.has(row) ? ' (Excluded)' : flagged ? ' (Review)' : ''}</th>
          {columns.map((column, index) => <td key={`${column}-${index}`}>{String(table.rows[row - 1]?.[column - 1] ?? '—')}</td>)}
        </tr>;
      })}</tbody></table>
    </div>
    <div className="temperature-pagination"><button type="button" disabled={currentPage === 0} onClick={() => setPage(currentPage - 1)}>Previous Rows</button>
      <span>Rows {start}–{Math.min(start + 49, selection.end_row)} / {selection.end_row}</span>
      <button type="button" disabled={currentPage + 1 >= totalPages} onClick={() => setPage(currentPage + 1)}>Next Rows</button></div>
  </details>;
}
