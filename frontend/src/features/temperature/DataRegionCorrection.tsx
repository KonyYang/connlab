import { useState } from 'react';
import type { DataRegion, WorkbookTable } from '../../api/temperature';
import { columnLetter } from './ChannelMapping';

export function DataRegionCorrection({ table, message, disabled, onApply }: {
  table: WorkbookTable; message: string; disabled: boolean;
  onApply: (region: DataRegion) => void;
}) {
  const [rows, setRows] = useState({ header_row: '', start_row: '', end_row: '' });
  const [page, setPage] = useState(0);
  const region = { header_row: Number(rows.header_row), start_row: Number(rows.start_row), end_row: Number(rows.end_row) };
  const valid = Object.values(rows).every(value => value.trim()) && Object.values(region).every(Number.isInteger)
    && region.header_row >= 1 && region.header_row < region.start_row
    && region.start_row <= region.end_row && region.end_row <= table.rows.length;
  const totalPages = Math.max(1, Math.ceil(table.rows.length / 50));
  const start = page * 50;
  const width = Math.max(0, ...table.rows.map(row => row.length));
  const columns = Array.from({ length: width }, (_, index) => index + 1);

  return <section className="temperature-review temperature-region-correction" aria-label="Data Region Needs Review">
    <p role="alert">{message}</p>
    <form onSubmit={event => { event.preventDefault(); if (valid && !disabled) onApply(region); }}>
      <div className="temperature-region-fields">
        {([['header_row', 'Header Row'], ['start_row', 'First Data Row'], ['end_row', 'Last Data Row']] as const).map(([key, label]) =>
          <label key={key}>{label}<input type="number" min={key === 'header_row' ? 1 : 2} max={table.rows.length}
            value={rows[key]} disabled={disabled} onChange={event => setRows(old => ({ ...old, [key]: event.target.value }))} /></label>)}
      </div>
      <button type="submit" disabled={disabled || !valid}>Apply Data Rows</button>
    </form>
    <details className="temperature-detail" open>
      <summary>Source Rows</summary>
      <div className="temperature-table-scroll" role="region" tabIndex={0} aria-label="Source Rows">
        <table><thead><tr><th>Original Row</th>{columns.map(column => <th key={column}>{columnLetter(column)}</th>)}</tr></thead>
          <tbody>{table.rows.slice(start, start + 50).map((row, index) => <tr key={start + index}>
            <th scope="row">{start + index + 1}</th>{columns.map(column => <td key={column}>{String(row[column - 1] ?? '—')}</td>)}
          </tr>)}</tbody>
        </table>
      </div>
      <div className="temperature-pagination">
        <button type="button" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous Rows</button>
        <span>Rows {table.rows.length ? start + 1 : 0}–{Math.min(start + 50, table.rows.length)} / {table.rows.length}</span>
        <button type="button" disabled={page + 1 >= totalPages} onClick={() => setPage(page + 1)}>Next Rows</button>
      </div>
    </details>
  </section>;
}
