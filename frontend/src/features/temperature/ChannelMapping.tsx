import { useState } from 'react';
import type { DataSelection, WorkbookTable } from '../../api/temperature';

export function columnLetter(index: number): string {
  let value = '';
  while (index > 0) { index -= 1; value = String.fromCharCode(65 + index % 26) + value; index = Math.floor(index / 26); }
  return value;
}
export function sourceColumns(table: WorkbookTable, headerRow: number) {
  const width = Math.max(...table.rows.map(row => row.length));
  return Array.from({ length: width }, (_, index) => ({ id: index + 1,
    label: `${columnLetter(index + 1)} — ${table.rows[headerRow - 1]?.[index] ?? '(No Header)'}` }));
}

export function ChannelMapping({ table, selection, onChange, disabled }: {
  table: WorkbookTable; selection: DataSelection; onChange: (patch: Partial<DataSelection>) => void; disabled: boolean;
}) {
  const [removed, setRemoved] = useState<{ column: number; index: number }[]>([]);
  const [adding, setAdding] = useState('');
  const columns = sourceColumns(table, selection.header_row);
  const channels = selection.temperature_columns;
  const available = columns.filter(col => !channels.includes(col.id)
    && col.id !== selection.current_column && col.id !== selection.ambient_column);
  function move(index: number, direction: number) {
    const next = [...channels];
    [next[index], next[index + direction]] = [next[index + direction], next[index]];
    onChange({ temperature_columns: next });
  }
  return <details className="temperature-detail" open>
    <summary>Sample &amp; Channel Mapping <span>{channels.length} Channels / {selection.thermocouples_per_sample} Per Sample</span></summary>
    <p className="temperature-hint">Choose the source channel for each position. A spare channel can replace a failed thermocouple.</p>
    <div className="temperature-channel-grid">
      {channels.map((column, index) => {
        const label = `Sample ${Math.floor(index / Math.max(1, selection.thermocouples_per_sample)) + 1} / TC ${index % Math.max(1, selection.thermocouples_per_sample) + 1}`;
        return <div className="temperature-channel" key={index}>
          <label>{label}<select aria-label={label} value={column} disabled={disabled} onChange={event => {
            const next = [...channels]; next[index] = Number(event.target.value); onChange({ temperature_columns: next });
          }}>{columns.filter(col => col.id !== selection.ambient_column && col.id !== selection.current_column).map(col =>
            <option key={col.id} value={col.id}>{col.label}</option>)}</select></label>
          <div className="temperature-channel-actions">
            <button type="button" aria-label={`Move ${label} Earlier`} disabled={disabled || index === 0} onClick={() => move(index, -1)}>Earlier</button>
            <button type="button" aria-label={`Move ${label} Later`} disabled={disabled || index === channels.length - 1} onClick={() => move(index, 1)}>Later</button>
            <button type="button" aria-label={`Exclude ${label}`} disabled={disabled} onClick={() => {
              setRemoved(old => [...old.filter(item => item.column !== column), { column, index }]);
              onChange({ temperature_columns: channels.filter((_, i) => i !== index) });
            }}>Exclude</button>
          </div>
        </div>;
      })}
    </div>
    <div className="temperature-actions">
      <label className="temperature-add-channel">Add Source Channel<select aria-label="Add Source Channel" value={adding} disabled={disabled} onChange={event => setAdding(event.target.value)}>
        <option value="">Choose Channel</option>
        {columns.filter(col => !channels.includes(col.id) && col.id !== selection.current_column && col.id !== selection.ambient_column)
          .map(col => <option key={col.id} value={col.id}>{col.label}</option>)}
      </select></label>
      <button type="button" disabled={disabled || !available.some(col => col.id === Number(adding))} onClick={() => {
        onChange({ temperature_columns: [...channels, Number(adding)] }); setAdding('');
      }}>Add Channel</button>
      {removed.filter(item => available.some(col => col.id === item.column)).map(item => <button key={item.column} type="button" disabled={disabled} onClick={() => {
        const next = [...channels]; next.splice(Math.min(item.index, next.length), 0, item.column);
        onChange({ temperature_columns: next }); setRemoved(old => old.filter(value => value.column !== item.column));
      }}>Restore Column {columnLetter(item.column)}</button>)}
    </div>
  </details>;
}
