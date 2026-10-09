import { useEffect, useRef, useState } from 'react';
import type { ChannelLayout, DataSelection, WorkbookTable } from '../../api/temperature';
import { isTemperatureColumn, sourceColumnKind, sourceColumns } from './sourceColumns';
import { equalSampleSize, includedSamples, moveSampleSlots, retainExcludedSlots, sampleGroups } from './sampleGroups';

type Snapshot = { order: number[]; excludedColumns: number[]; removedTemperatures: number[];
  temperatureColumns: number[]; excludedRows: number[]; slots: number[][];
  sampleGroups: number[][] | null | undefined; count: number };

export function useDataGridEditing(table: WorkbookTable, selection: DataSelection,
  layout: ChannelLayout | null | undefined, onChange: (patch: Partial<DataSelection>) => void) {
  const [order, setOrder] = useState(() => {
    let position = 0;
    // The imported logical order already includes any explicit sample-name grouping.
    return sourceColumns(table, selection.header_row).map(column => selection.temperature_columns.includes(column.id)
      ? selection.temperature_columns[position++] : column.id);
  });
  const [excludedColumns, setExcludedColumns] = useState<number[]>([]);
  const [removedTemperatures, setRemovedTemperatures] = useState<number[]>([]);
  // Keep excluded slots for restoration; only included groups go into the request.
  const [slots, setSlots] = useState(() => sampleGroups(selection, layout));
  const [history, setHistory] = useState<Snapshot[]>([]);
  const [selectedRows, setSelectedRows] = useState<number[]>([]);
  const [selectedColumns, setSelectedColumns] = useState<number[]>([]);
  const rangeAnchor = useRef<{ kind: 'row' | 'column'; id: number } | null>(null);
  const committedParameters = useRef([selection.ambient_column, selection.current_column, selection.thermocouples_per_sample]);
  // Undo never rolls back a later role/count decision from the parameter row.
  useEffect(() => {
    const parameters = [selection.ambient_column, selection.current_column, selection.thermocouples_per_sample];
    if (parameters.every((value, index) => value === committedParameters.current[index])) return;
    committedParameters.current = parameters;
    setHistory([]); setSelectedRows([]); setSelectedColumns([]);
    setSlots(previous => retainExcludedSlots(sampleGroups(selection, layout), previous,
      removedTemperatures.filter(column => column !== selection.ambient_column && column !== selection.current_column)));
    rangeAnchor.current = null;
    setExcludedColumns(old => old.filter(column => column !== selection.ambient_column && column !== selection.current_column));
    setRemovedTemperatures(old => old.filter(column => column !== selection.ambient_column && column !== selection.current_column));
  }, [selection.ambient_column, selection.current_column, selection.thermocouples_per_sample]);
  const protectedColumn = (column: number) => column <= 2 || column === selection.ambient_column || column === selection.current_column
    || sourceColumnKind(table, selection, column, layout) === 'current';
  const movable = (column: number) => isTemperatureColumn(table, selection, column, layout);
  const snapshot = (): Snapshot => ({ order, excludedColumns, removedTemperatures,
    temperatureColumns: selection.temperature_columns, excludedRows: selection.excluded_rows,
    slots, sampleGroups: selection.sample_groups, count: selection.thermocouples_per_sample });
  function commit(next: Snapshot, columnsChanged = false) {
    setHistory(old => [...old, snapshot()]);
    setOrder(next.order); setExcludedColumns(next.excludedColumns); setRemovedTemperatures(next.removedTemperatures);
    setSlots(next.slots);
    const groups = includedSamples(next.slots, next.temperatureColumns);
    const count = columnsChanged ? equalSampleSize(groups) ?? next.count : next.count;
    committedParameters.current = [selection.ambient_column, selection.current_column, count];
    onChange({ temperature_columns: columnsChanged ? groups.flat() : next.temperatureColumns, excluded_rows: next.excludedRows,
      ...(columnsChanged ? { sample_groups: groups, thermocouples_per_sample: count } : {}) });
    setSelectedRows([]); setSelectedColumns([]);
    rangeAnchor.current = null;
  }
  function selectRows(rows: number[]) { setSelectedRows(rows); setSelectedColumns([]); rangeAnchor.current = null; }
  function selectColumns(columns: number[]) {
    const selectable = columns.filter(column => !protectedColumn(column));
    setSelectedColumns(selectable); setSelectedRows([]);
    rangeAnchor.current = selectable.length ? { kind: 'column', id: selectable[0] } : null;
  }
  function selectColumn(column: number, modifiers: { shiftKey: boolean; ctrlKey: boolean; metaKey: boolean }) {
    if (protectedColumn(column)) return;
    const additive = modifiers.ctrlKey || modifiers.metaKey;
    const anchor = modifiers.shiftKey && rangeAnchor.current?.kind === 'column' ? rangeAnchor.current.id : column;
    const first = displayOrder.indexOf(anchor), last = displayOrder.indexOf(column);
    const range = displayOrder.slice(Math.min(first, last), Math.max(first, last) + 1)
      .filter(item => !protectedColumn(item));
    if (modifiers.shiftKey) {
      setSelectedColumns(additive ? [...new Set([...selectedColumns, ...range])] : range);
    } else {
      setSelectedColumns(additive ? selectedColumns.includes(column)
        ? selectedColumns.filter(item => item !== column) : [...selectedColumns, column] : [column]);
    }
    setSelectedRows([]);
    // Repeated Shift endpoints use the same anchor, in current presentation order.
    rangeAnchor.current = { kind: 'column', id: anchor };
  }
  function toggleRow(row: number, checked: boolean, extend: boolean) {
    const anchor = extend && rangeAnchor.current?.kind === 'row' ? rangeAnchor.current.id : row;
    const first = Math.max(selection.start_row, Math.min(anchor, row));
    const last = Math.min(selection.end_row, Math.max(anchor, row));
    setSelectedRows(old => {
      const next = new Set(old);
      for (let item = first; item <= last; item++) {
        if (checked) next.add(item); else next.delete(item);
      }
      return [...next].sort((a, b) => a - b);
    });
    setSelectedColumns([]);
    // Further Shift clicks extend from the same first endpoint; a plain click starts a new range.
    rangeAnchor.current = { kind: 'row', id: anchor };
  }
  function exclude() {
    if (selectedRows.length) {
      commit({ ...snapshot(), excludedRows: [...new Set([...selection.excluded_rows, ...selectedRows])].sort((a, b) => a - b) });
    } else {
      const columns = selectedColumns.filter(column => !protectedColumn(column));
      commit({ ...snapshot(), excludedColumns: [...new Set([...excludedColumns, ...columns])],
        removedTemperatures: [...new Set([...removedTemperatures, ...columns.filter(column => selection.temperature_columns.includes(column))])],
        temperatureColumns: selection.temperature_columns.filter(column => !columns.includes(column)) }, true);
    }
  }
  function restore() {
    if (selectedRows.length) {
      const restoring = new Set(selectedRows);
      commit({ ...snapshot(), excludedRows: selection.excluded_rows.filter(row => !restoring.has(row)) });
    } else {
      const restored = selectedColumns.filter(column => removedTemperatures.includes(column) && movable(column));
      const active = new Set([...selection.temperature_columns, ...restored]);
      commit({ ...snapshot(), excludedColumns: excludedColumns.filter(column => !selectedColumns.includes(column)),
        removedTemperatures: removedTemperatures.filter(column => !selectedColumns.includes(column)),
        temperatureColumns: slots.flat().filter(column => active.has(column) && movable(column)) }, true);
    }
  }
  function moveBefore(destination: number | null) {
    const moving = order.filter(column => selectedColumns.includes(column) && movable(column));
    if (!moving.length || (destination !== null && (moving.includes(destination) || !movable(destination)))) return;
    const next = order.filter(column => !moving.includes(column));
    const lastTemperature = next.reduce((last, column, index) => movable(column) ? index : last, -1);
    const index = destination === null ? lastTemperature + 1 : next.indexOf(destination);
    if (index < 0) return;
    next.splice(index, 0, ...moving);
    // Moving an unused spare into the temperature block activates the entire source column.
    const active = new Set([...selection.temperature_columns, ...moving]);
    const temperatureColumns = next.filter(column => active.has(column) && movable(column));
    commit({ ...snapshot(), order: next, excludedColumns: excludedColumns.filter(column => !moving.includes(column)),
      removedTemperatures: removedTemperatures.filter(column => !moving.includes(column)),
      slots: moveSampleSlots(slots, moving, destination, selection.temperature_columns, temperatureColumns, selection.thermocouples_per_sample),
      temperatureColumns }, true);
  }
  function undo() {
    const previous = history.at(-1);
    if (!previous) return;
    setHistory(old => old.slice(0, -1)); setOrder(previous.order); setExcludedColumns(previous.excludedColumns);
    setRemovedTemperatures(previous.removedTemperatures); setSelectedColumns([]); setSelectedRows([]);
    setSlots(previous.slots);
    rangeAnchor.current = null;
    committedParameters.current = [selection.ambient_column, selection.current_column, previous.count];
    onChange({ temperature_columns: previous.temperatureColumns, excluded_rows: previous.excludedRows,
      sample_groups: previous.sampleGroups, thermocouples_per_sample: previous.count });
  }
  const excludedRowSet = new Set(selection.excluded_rows);
  const canExclude = selectedRows.some(row => !excludedRowSet.has(row))
    || selectedColumns.some(column => !protectedColumn(column) && !excludedColumns.includes(column));
  const canRestore = selectedRows.some(row => excludedRowSet.has(row))
    || selectedColumns.some(column => excludedColumns.includes(column));
  // Presentation order never changes source positions or values used by preparation/export.
  const active = selection.temperature_columns.filter(column => !protectedColumn(column));
  const roles = [selection.ambient_column, selection.current_column,
    ...order.filter(column => column > 2 && column !== selection.ambient_column
      && column !== selection.current_column && sourceColumnKind(table, selection, column, layout) === 'current')];
  const fixed = new Set([1, 2, ...active, ...roles]);
  const remaining = order.filter(column => !fixed.has(column));
  const displayOrder = [1, 2, ...active, ...roles, ...remaining.filter(column => !excludedColumns.includes(column)),
    ...remaining.filter(column => excludedColumns.includes(column))];
  return { order: displayOrder, excludedColumns, selectedRows, selectedColumns, selectRows, selectColumns, selectColumn, toggleRow,
    exclude, restore, moveBefore, undo, protectedColumn, movable, canExclude, canRestore, canUndo: Boolean(history.length),
    restoreAllRows: () => commit({ ...snapshot(), excludedRows: [] }) };
}
