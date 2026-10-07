import { useCallback, useState } from 'react';
import type { ChannelLayout, DataIssue, DataSelection, WorkbookTable } from '../../api/temperature';
import { UiIcon } from '../../components/common/UiIcon';
import { ColumnActions, type ColumnMenuAnchor } from './ColumnActions';
import { columnLetter, incompleteSampleGroups, sourceColumns } from './sourceColumns';
import { useDataGridEditing } from './useDataGridEditing';

export function DataPreview({ table, selection, layout, issues, disabled, onChange }: {
  table: WorkbookTable; selection: DataSelection; layout?: ChannelLayout | null; issues: DataIssue[];
  disabled: boolean; onChange: (patch: Partial<DataSelection>) => void;
}) {
  const grid = useDataGridEditing(table, selection, layout, onChange);
  const [page, setPage] = useState(0);
  const [range, setRange] = useState('');
  const [rangeError, setRangeError] = useState('');
  const [menu, setMenu] = useState<ColumnMenuAnchor | null>(null);
  const closeMenu = useCallback(() => setMenu(null), []);
  const columns = sourceColumns(table, selection.header_row);
  const incomplete = incompleteSampleGroups(selection, layout);
  const count = Math.max(1, selection.thermocouples_per_sample || 1);
  const total = Math.max(0, selection.end_row - selection.start_row + 1);
  const pages = Math.max(1, Math.ceil(total / 50));
  const currentPage = Math.min(page, pages - 1);
  const rows = Array.from({ length: Math.min(50, total - currentPage * 50) }, (_, index) => selection.start_row + currentPage * 50 + index);
  const selectedCount = grid.selectedRows.length + grid.selectedColumns.length;
  const activeIndex = (column: number) => selection.temperature_columns.indexOf(column);
  const groupLabel = (column: number) => !incomplete && activeIndex(column) >= 0 ? `Sample ${Math.floor(activeIndex(column) / count) + 1}` : '';
  const groups: { label: string; size: number }[] = [];
  grid.order.forEach(column => {
    const label = groupLabel(column);
    if (groups.at(-1)?.label === label) groups[groups.length - 1].size++;
    else groups.push({ label, size: 1 });
  });
  const role = (column: number) => {
    if (column === selection.ambient_column) return 'Ambient';
    if (column === selection.current_column) return 'Plot Current';
    if (layout?.current_columns.includes(column)) return `Retained / Not Plotted${layout.stable_current_columns.includes(column) ? ' · Stable' : ''}`;
    if (grid.excludedColumns.includes(column)) return 'Excluded';
    if (activeIndex(column) >= 0) return incomplete ? 'Pending Grouping' : `${groupLabel(column)} / TC ${activeIndex(column) % count + 1}`;
    return grid.movable(column) ? 'Not Plotted' : 'Source';
  };
  const headerClass = (column: number) => [grid.selectedColumns.includes(column) ? 'is-selected-column' : '',
    grid.excludedColumns.includes(column) ? 'is-excluded-column' : ''].filter(Boolean).join(' ');
  const headerParts = (column: number) => String(table.rows[selection.header_row - 1]?.[column - 1] ?? '')
    .match(/^(\d+)\s*<([^>]+)>\s*(.*)$/);
  function selectRange() {
    const parsed = new Set<number>();
    for (const part of range.split(',')) {
      const match = part.trim().match(/^(\d+)(?:\s*-\s*(\d+))?$/);
      if (!match) { setRangeError('Enter row numbers or ranges, such as 45-91, 120.'); return; }
      const first = Number(match[1]), last = Number(match[2] ?? match[1]);
      if (first < selection.start_row || last > selection.end_row || last < first) {
        setRangeError(`Choose rows ${selection.start_row}–${selection.end_row}.`); return;
      }
      for (let row = first; row <= last; row++) parsed.add(row);
    }
    setRangeError(''); grid.selectRows([...parsed]);
  }
  function openMenu(column: number, trigger: HTMLButtonElement) {
    if (!grid.selectedColumns.includes(column) || grid.selectedColumns.some(selected => !grid.movable(selected))) grid.selectColumns([column]);
    const bounds = trigger.getBoundingClientRect();
    setMenu({ column, trigger, left: Math.max(8, Math.min(bounds.left, window.innerWidth - 276)),
      top: Math.max(8, Math.min(bounds.bottom + 6, window.innerHeight - 300)) });
  }
  function runAction(action: () => void) { action(); menu?.trigger.focus(); closeMenu(); }
  return <section className="temperature-data-editor" aria-label="Data Preview">
    <div className="temperature-data-toolbar"><div><h3>Data Preview</h3>
      <span>{Math.ceil(selection.temperature_columns.length / count)} {selection.temperature_columns.length === count ? 'Sample' : 'Samples'} · {count} TC/Sample · {selection.temperature_columns.length} Channels</span></div>
      <div className="temperature-data-actions"><span>{selectedCount ? `${selectedCount} Selected` : ''}</span>
        <button type="button" disabled={disabled || !grid.canExclude} onClick={grid.exclude}>Exclude Selected</button>
        <button type="button" disabled={disabled || !grid.canRestore} onClick={grid.restore}>Restore</button>
        <button type="button" disabled={disabled || !grid.canUndo} onClick={grid.undo}>Undo</button></div></div>
    {incomplete && <p className="temperature-warning" role="alert">Incomplete sample group. Restore columns or move a spare into position; each sample needs {count} thermocouples.</p>}
    <div className="temperature-table-scroll" role="region" aria-label="Scanner Data Preview" tabIndex={0}>
      <table className="temperature-source-table"><thead>
        <tr className="temperature-sample-groups"><th colSpan={2} />{groups.map((group, index) => <th key={index} colSpan={group.size}>{group.label}</th>)}</tr>
        <tr><th><input type="checkbox" aria-label="Select Visible Rows" disabled={disabled || !rows.length}
          checked={Boolean(rows.length) && rows.every(row => grid.selectedRows.includes(row))}
          onChange={event => { closeMenu(); grid.selectRows(event.target.checked ? [...new Set([...grid.selectedRows, ...rows])] : grid.selectedRows.filter(row => !rows.includes(row))); }} /></th>
          <th>Original Row</th>{grid.order.map(column => <th key={column} className={headerClass(column)}>
            <div className="temperature-source-column"><input type="checkbox" aria-label={`Select Column ${columnLetter(column)}`}
              disabled={disabled || grid.protectedColumn(column)} checked={grid.selectedColumns.includes(column)}
              onChange={event => { closeMenu(); grid.selectColumns(event.target.checked ? [...grid.selectedColumns, column] : grid.selectedColumns.filter(item => item !== column)); }} />
              {grid.movable(column) ? <button type="button" disabled={disabled} aria-label={`Column ${columnLetter(column)} Actions`}
                aria-haspopup="dialog" aria-expanded={menu?.column === column} onClick={event => openMenu(column, event.currentTarget)}>{columnLetter(column)}<UiIcon name="chevron-down" /></button>
                : <span>{columnLetter(column)}</span>}</div>
            <span className="temperature-source-title" title={String(table.rows[selection.header_row - 1]?.[column - 1] ?? '')}>
              {headerParts(column) ? <>{headerParts(column)![1]}<br />{headerParts(column)![2]} {headerParts(column)![3]}</> : String(table.rows[selection.header_row - 1]?.[column - 1] ?? '')}</span>
            <span className="temperature-source-role">{role(column)}</span></th>)}</tr></thead>
        <tbody>{rows.map(row => <tr key={row} className={selection.excluded_rows.includes(row) ? 'is-excluded-row' : issues.some(issue => issue.source_row === row) ? 'is-flagged-row' : ''}>
          <td><input type="checkbox" aria-label={`Select Row ${row}`} disabled={disabled} checked={grid.selectedRows.includes(row)}
            onChange={event => { closeMenu(); grid.selectRows(event.target.checked ? [...grid.selectedRows, row] : grid.selectedRows.filter(item => item !== row)); }} /></td>
          <th scope="row">{row}{selection.excluded_rows.includes(row) ? ' (Excluded)' : issues.some(issue => issue.source_row === row) ? ' (Review)' : ''}</th>
          {grid.order.map(column => <td key={column} className={headerClass(column)}>{String(table.rows[row - 1]?.[column - 1] ?? '')}</td>)}</tr>)}</tbody>
      </table></div>
    <div className="temperature-data-footer"><span>{total - selection.excluded_rows.length} Included / {selection.excluded_rows.length} Excluded Rows</span>
      <div>{issues.some(issue => issue.code === 'zero_current') && <button type="button" disabled={disabled}
        onClick={() => grid.selectRows([...new Set(issues.filter(issue => issue.code === 'zero_current').map(issue => issue.source_row))])}>Select Unpowered Rows</button>}
        {selection.excluded_rows.length > 0 && <button type="button" disabled={disabled} onClick={grid.restoreAllRows}>Restore All Rows</button>}
        <button type="button" disabled={currentPage === 0} onClick={() => { closeMenu(); setPage(currentPage - 1); }}>Previous</button>
        <span>Page {currentPage + 1} / {pages}</span><button type="button" disabled={currentPage + 1 >= pages} onClick={() => { closeMenu(); setPage(currentPage + 1); }}>Next</button></div></div>
    <details className="temperature-row-range"><summary>Select Rows By Range</summary><label>Rows To Select<input value={range} disabled={disabled} onChange={event => setRange(event.target.value)} placeholder="45-91, 120" /></label>
      <button type="button" disabled={disabled || !range.trim()} onClick={selectRange}>Select Rows</button>{rangeError && <p role="alert">{rangeError}</p>}</details>
    {menu && <ColumnActions anchor={menu} columnLabel={columns.find(column => column.id === menu.column)!.label}
      columns={grid.order.filter(column => grid.movable(column) && !grid.selectedColumns.includes(column)).map(column => columns.find(item => item.id === column)!)}
      selectedCount={grid.selectedColumns.length} disabled={disabled} canExclude={grid.canExclude} canRestore={grid.canRestore}
      onExclude={() => runAction(grid.exclude)} onRestore={() => runAction(grid.restore)} onMove={destination => runAction(() => grid.moveBefore(destination))} onClose={closeMenu} />}
  </section>;
}
