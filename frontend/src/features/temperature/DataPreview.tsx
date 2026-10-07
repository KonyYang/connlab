import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { CSSProperties } from 'react';
import type { ChannelLayout, DataIssue, DataSelection, WorkbookTable } from '../../api/temperature';
import { UiIcon } from '../../components/common/UiIcon';
import { ColumnActions, type ColumnMenuAnchor } from './ColumnActions';
import { columnLetter, incompleteSampleGroups, sourceColumns } from './sourceColumns';
import { useDataGridEditing } from './useDataGridEditing';
import { SOURCE_ROW_HEIGHT, useSourceRowWindow } from './useSourceRowWindow';

const COLUMN_WIDTH = { selector: 32, scan: 64, time: 184, channel: 104 };
const columnWidth = (column: number) => column === 1 ? COLUMN_WIDTH.scan : column === 2 ? COLUMN_WIDTH.time : COLUMN_WIDTH.channel;

export function DataPreview({ table, selection, layout, issues, disabled, onChange }: {
  table: WorkbookTable; selection: DataSelection; layout?: ChannelLayout | null; issues: DataIssue[];
  disabled: boolean; onChange: (patch: Partial<DataSelection>) => void;
}) {
  const grid = useDataGridEditing(table, selection, layout, onChange);
  const [range, setRange] = useState('');
  const [rangeError, setRangeError] = useState('');
  const [menu, setMenu] = useState<ColumnMenuAnchor | null>(null);
  const [activeRow, setActiveRow] = useState<number | null>(null);
  const closeMenu = useCallback(() => setMenu(null), []);
  const columns = useMemo(() => sourceColumns(table, selection.header_row), [table, selection.header_row]);
  const incomplete = incompleteSampleGroups(selection, layout);
  const count = Math.max(1, selection.thermocouples_per_sample || 1);
  const total = Math.max(0, selection.end_row - selection.start_row + 1);
  const rowWindow = useSourceRowWindow(selection.start_row, total);
  const { rows } = rowWindow;
  const selectedRows = useMemo(() => new Set(grid.selectedRows), [grid.selectedRows]);
  const excludedRows = useMemo(() => new Set(selection.excluded_rows), [selection.excluded_rows]);
  const flaggedRows = useMemo(() => new Set(issues.map(issue => issue.source_row)), [issues]);
  const selectAll = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (selectAll.current) selectAll.current.indeterminate = selectedRows.size > 0 && selectedRows.size < total;
  }, [selectedRows, total]);
  const selectedCount = grid.selectedRows.length + grid.selectedColumns.length;
  const activeIndex = (column: number) => selection.temperature_columns.indexOf(column);
  const groupLabel = (column: number) => !incomplete && activeIndex(column) >= 0 ? `Sample ${Math.floor(activeIndex(column) / count) + 1}` : '';
  const groups: { label: string; size: number }[] = [];
  grid.order.filter(column => column > 2).forEach(column => {
    const label = groupLabel(column);
    if (groups.at(-1)?.label === label) groups[groups.length - 1].size++;
    else groups.push({ label, size: 1 });
  });
  const role = (column: number) => {
    if (column <= 2) return '';
    if (column === selection.ambient_column) return 'Ambient';
    if (column === selection.current_column) return 'Plot Current';
    if (layout?.current_columns.includes(column)) return `Retained / Not Plotted${layout.stable_current_columns.includes(column) ? ' · Stable' : ''}`;
    if (grid.excludedColumns.includes(column)) return 'Excluded';
    if (activeIndex(column) >= 0) return incomplete ? 'Pending Grouping' : `${groupLabel(column)} / TC ${activeIndex(column) % count + 1}`;
    return grid.movable(column) ? 'Not Plotted' : 'Source';
  };
  const headerClass = (column: number) => [column === 1 ? 'temperature-index-scan' : column === 2 ? 'temperature-index-time' : '',
    grid.selectedColumns.includes(column) ? 'is-selected-column' : '',
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
    <div ref={rowWindow.viewport} className="temperature-table-scroll" role="region" aria-label="Scanner Data Preview" tabIndex={0}
      onScroll={event => { closeMenu(); rowWindow.setScrollTop(event.currentTarget.scrollTop); }}>
      <table className="temperature-source-table" aria-rowcount={total + 2}
        style={{ width: COLUMN_WIDTH.selector + grid.order.reduce((width, column) => width + columnWidth(column), 0),
          '--temperature-selector-width': `${COLUMN_WIDTH.selector}px`, '--temperature-scan-width': `${COLUMN_WIDTH.scan}px` } as CSSProperties}>
        <colgroup><col style={{ width: COLUMN_WIDTH.selector }} />
          {grid.order.map(column => <col key={column} style={{ width: columnWidth(column) }} />)}</colgroup>
        <thead ref={rowWindow.header}>
        <tr className="temperature-sample-groups"><th colSpan={1 + grid.order.filter(column => column <= 2).length} className="temperature-index-band" />{groups.map((group, index) => <th key={index} colSpan={group.size}>{group.label}</th>)}</tr>
        <tr><th className="temperature-row-selector"><input ref={selectAll} type="checkbox" aria-label="Select All Rows" disabled={disabled || !total}
          checked={Boolean(total) && selectedRows.size === total}
          onChange={event => { closeMenu(); grid.selectRows(event.target.checked ? Array.from({ length: total }, (_, index) => selection.start_row + index) : []); }} /></th>
          {grid.order.map(column => <th key={column} className={headerClass(column)}>
            <div className="temperature-source-column">{column > 2 && <input type="checkbox" aria-label={`Select Column ${columnLetter(column)}`}
              disabled={disabled || grid.protectedColumn(column)} checked={grid.selectedColumns.includes(column)}
              onChange={event => { closeMenu(); grid.selectColumns(event.target.checked ? [...grid.selectedColumns, column] : grid.selectedColumns.filter(item => item !== column)); }} />}
              {grid.movable(column) ? <button type="button" disabled={disabled} aria-label={`Column ${columnLetter(column)} Actions`}
                aria-haspopup="dialog" aria-expanded={menu?.column === column} onClick={event => openMenu(column, event.currentTarget)}>{columnLetter(column)}<UiIcon name="chevron-down" /></button>
                : <span>{columnLetter(column)}</span>}</div>
            <span className="temperature-source-title" title={String(table.rows[selection.header_row - 1]?.[column - 1] ?? '')}>
              {headerParts(column) ? <>{headerParts(column)![1]}<br />{headerParts(column)![2]} {headerParts(column)![3]}</> : String(table.rows[selection.header_row - 1]?.[column - 1] ?? '')}</span>
            {role(column) && <span className="temperature-source-role" title={role(column)}>{role(column)}</span>}</th>)}</tr></thead>
        <tbody>
          {rowWindow.topPadding > 0 && <tr aria-hidden="true" className="temperature-row-spacer"><td colSpan={grid.order.length + 1} style={{ height: rowWindow.topPadding }} /></tr>}
          {rows.map(row => <tr key={row} aria-rowindex={row - selection.start_row + 3} style={{ height: SOURCE_ROW_HEIGHT }}
            aria-selected={selectedRows.has(row)}
            aria-current={activeRow === row ? 'true' : undefined}
            aria-label={excludedRows.has(row) ? `Scan ${table.rows[row - 1]?.[0]} · Excluded` : flaggedRows.has(row) ? `Scan ${table.rows[row - 1]?.[0]} · Needs Review` : undefined}
            onClick={() => setActiveRow(row)} onFocus={() => setActiveRow(row)}
            className={excludedRows.has(row) ? 'is-excluded-row' : flaggedRows.has(row) ? 'is-flagged-row' : ''}>
          <td className="temperature-row-selector"><input type="checkbox" aria-label={`Select Row ${row}`} disabled={disabled} checked={selectedRows.has(row)}
            title={`Scan ${table.rows[row - 1]?.[0]} · Source Row ${row}${excludedRows.has(row) ? ' · Excluded' : flaggedRows.has(row) ? ' · Needs Review' : ''}`}
            onChange={event => { closeMenu(); grid.toggleRow(row, event.target.checked,
              'shiftKey' in event.nativeEvent && event.nativeEvent.shiftKey === true); }}
            onKeyDown={event => { if (event.key === ' ' && event.shiftKey) { event.preventDefault(); closeMenu(); grid.toggleRow(row, !selectedRows.has(row), true); } }} /></td>
          {grid.order.map(column => <td key={column} className={headerClass(column)} title={String(table.rows[row - 1]?.[column - 1] ?? '')}>
            {String(table.rows[row - 1]?.[column - 1] ?? '')}</td>)}</tr>)}
          {rowWindow.bottomPadding > 0 && <tr aria-hidden="true" className="temperature-row-spacer"><td colSpan={grid.order.length + 1} style={{ height: rowWindow.bottomPadding }} /></tr>}
        </tbody>
      </table></div>
    <div className="temperature-data-footer"><span>{total - selection.excluded_rows.length} Included / {selection.excluded_rows.length} Excluded Rows</span>
      <div>{issues.some(issue => issue.code === 'zero_current') && <button type="button" disabled={disabled}
        onClick={() => grid.selectRows([...new Set(issues.filter(issue => issue.code === 'zero_current').map(issue => issue.source_row))])}>Select Unpowered Rows</button>}
        {selection.excluded_rows.length > 0 && <button type="button" disabled={disabled} onClick={grid.restoreAllRows}>Restore All Rows</button>}
        </div></div>
    <details className="temperature-row-range"><summary>Select Rows By Range</summary><label>Rows To Select<input title="Original source worksheet row numbers" value={range} disabled={disabled} onChange={event => setRange(event.target.value)} placeholder="45-91, 120" /></label>
      <button type="button" disabled={disabled || !range.trim()} onClick={selectRange}>Select Rows</button>{rangeError && <p role="alert">{rangeError}</p>}</details>
    {menu && <ColumnActions anchor={menu} columnLabel={columns.find(column => column.id === menu.column)!.label}
      columns={grid.order.filter(column => grid.movable(column) && !grid.selectedColumns.includes(column)).map(column => columns.find(item => item.id === column)!)}
      selectedCount={grid.selectedColumns.length} disabled={disabled} canExclude={grid.canExclude} canRestore={grid.canRestore}
      onExclude={() => runAction(grid.exclude)} onRestore={() => runAction(grid.restore)} onMove={destination => runAction(() => grid.moveBefore(destination))} onClose={closeMenu} />}
  </section>;
}
