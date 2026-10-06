import { useState } from 'react';
import type { ChannelLayout, DataSelection, WorkbookTable } from '../../api/temperature';

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

export function ChannelMapping({ table, selection, layout, onChange, disabled }: {
  table: WorkbookTable; selection: DataSelection; layout?: ChannelLayout | null;
  onChange: (patch: Partial<DataSelection>) => void; disabled: boolean;
}) {
  const [original] = useState(() => ({ channels: [...selection.temperature_columns], count: selection.thermocouples_per_sample }));
  const [editing, setEditing] = useState(false);
  const [target, setTarget] = useState(0);
  const [source, setSource] = useState('');
  const [destination, setDestination] = useState(0);
  const [removed, setRemoved] = useState<{ column: number; index: number }[]>([]);
  const columns = sourceColumns(table, selection.header_row);
  const channels = selection.temperature_columns;
  const count = Math.max(1, selection.thermocouples_per_sample);
  const position = Math.min(target, Math.max(0, channels.length - 1));
  const sampleCount = Math.ceil(channels.length / count);
  const changed = channels.join(',') !== original.channels.join(',') || count !== original.count;
  const available = columns.filter(col => !channels.includes(col.id) && col.id !== selection.current_column
    && col.id !== selection.ambient_column && !layout?.current_columns.includes(col.id)
    && !/scan|time|date|序号|扫描|时间/i.test(String(table.rows[selection.header_row - 1]?.[col.id - 1] ?? '')));
  const usableSource = available.some(col => col.id === Number(source));
  const incomplete = !channels.length || channels.length % count !== 0;
  const sourceIssues = changed ? [] : layout?.issues ?? [];
  const slotLabel = (index: number) => {
    const sampleIndex = Math.floor(index / count);
    const sample = count === layout?.thermocouples_per_sample ? layout.sample_groups[sampleIndex]?.sample_id : undefined;
    return `Sample ${sample ?? sampleIndex + 1} / TC ${index % count + 1}`;
  };
  return <section className="temperature-mapping" aria-label="Sample & Channel Mapping">
    <div className="temperature-section-heading">
      <span>{`${sampleCount} ${sampleCount === 1 ? 'Sample' : 'Samples'} / ${count} Thermocouples Per Sample / ${channels.length} Channels`}</span>
      <button type="button" aria-expanded={editing} disabled={disabled} onClick={() => setEditing(!editing)}>{editing ? 'Close Adjustments' : 'Adjust Channels'}</button>
    </div>
    {incomplete && <p role="alert" className="temperature-error">Incomplete sample group. Adjust channels or Thermocouples/Sample before confirming.</p>}
    {sourceIssues.map(message => <p className="temperature-hint" key={message}>{message}</p>)}
    <details className="temperature-detail"><summary>View Channels</summary>
      <div className="temperature-table-scroll"><table><thead><tr><th>Sample</th><th>Assigned Channels</th></tr></thead>
        <tbody>{Array.from({ length: sampleCount }, (_, sample) => <tr key={sample}>
          <th>{slotLabel(sample * count).split(' / ')[0]}</th>
          <td className="temperature-channel-names">{channels.slice(sample * count, (sample + 1) * count).map(column => columns[column - 1]?.label).join(' · ')}</td>
        </tr>)}</tbody></table></div>
    </details>
    {editing && <div className="temperature-adjustments">
      <div className="temperature-actions">
        <label>Target Position<select value={position} disabled={disabled || !channels.length} onChange={event => setTarget(Number(event.target.value))}>
          {channels.map((column, index) => <option key={index} value={index}>{slotLabel(index)} — {columnLetter(column)}</option>)}
        </select></label>
        <label>Replacement Channel<select value={source} disabled={disabled} onChange={event => setSource(event.target.value)}>
          <option value="">Choose Channel</option>{available.map(col => <option key={col.id} value={col.id}>{col.label}</option>)}
        </select></label>
        <button type="button" disabled={disabled || !channels.length || !usableSource} onClick={() => {
          const next = [...channels]; next[position] = Number(source); onChange({ temperature_columns: next }); setSource('');
        }}>Replace Channel</button>
        <button type="button" disabled={disabled || !channels.length} onClick={() => {
          setRemoved(old => [...old.filter(item => item.column !== channels[position]), { column: channels[position], index: position }]);
          onChange({ temperature_columns: channels.filter((_, index) => index !== position) });
        }}>Exclude Channel</button>
      </div>
      <div className="temperature-actions">
        <label>Move To Position<select value={Math.min(destination, Math.max(0, channels.length - 1))} disabled={disabled || !channels.length} onChange={event => setDestination(Number(event.target.value))}>
          {channels.map((_, index) => <option key={index} value={index}>{slotLabel(index)}</option>)}
        </select></label>
        <button type="button" disabled={disabled || !channels.length || position === Math.min(destination, channels.length - 1)} onClick={() => {
          const next = [...channels]; const [column] = next.splice(position, 1); next.splice(Math.min(destination, next.length), 0, column);
          onChange({ temperature_columns: next }); setTarget(Math.min(destination, next.length - 1));
        }}>Move Channel</button>
        <button type="button" disabled={disabled || !usableSource} onClick={() => { onChange({ temperature_columns: [...channels, Number(source)] }); setSource(''); }}>Add Channel</button>
        <button type="button" disabled={disabled || !changed} onClick={() => {
          onChange({ temperature_columns: original.channels, thermocouples_per_sample: original.count }); setRemoved([]); setTarget(0); setSource('');
        }}>Reset Mapping</button>
        {removed.filter(item => available.some(col => col.id === item.column)).map(item => <button key={item.column} type="button" disabled={disabled} onClick={() => {
          const next = [...channels]; next.splice(Math.min(item.index, next.length), 0, item.column);
          onChange({ temperature_columns: next }); setRemoved(old => old.filter(value => value.column !== item.column));
        }}>Restore Column {columnLetter(item.column)}</button>)}
      </div>
    </div>}
    {changed && <div className="temperature-mapping-changes" aria-label="Channel Adjustments">
      {channels.length === original.channels.length
        ? channels.map((column, index) => column !== original.channels[index] && <p key={index} className="temperature-hint">
          {slotLabel(index)}: {columnLetter(original.channels[index])} → {columnLetter(column)}
        </p>)
        : <>
          {original.channels.filter(column => !channels.includes(column)).map(column => <p key={`excluded-${column}`} className="temperature-hint">Excluded: {columns[column - 1]?.label}</p>)}
          {channels.filter(column => !original.channels.includes(column)).map(column => <p key={`added-${column}`} className="temperature-hint">Added: {columns[column - 1]?.label}</p>)}
        </>}
    </div>}
    {changed && <p className="temperature-hint" role="status">Channel Mapping Adjusted — confirm data to use these assignments.</p>}
  </section>;
}
