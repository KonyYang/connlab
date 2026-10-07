import { useEffect, useRef, useState } from 'react';
import type { ChannelLayout, DataSelection, WorkbookTable } from '../../api/temperature';
import { isTemperatureColumn, sourceColumnKind, sourceColumns } from './sourceColumns';

type Snapshot = { order: number[]; excludedColumns: number[]; removedTemperatures: number[];
  temperatureColumns: number[]; excludedRows: number[] };

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
  const [history, setHistory] = useState<Snapshot[]>([]);
  const [selectedRows, setSelectedRows] = useState<number[]>([]);
  const [selectedColumns, setSelectedColumns] = useState<number[]>([]);
  const rowAnchor = useRef<number | null>(null);
  // Undo never rolls back a later role/count decision from the parameter row.
  useEffect(() => {
    setHistory([]); setSelectedRows([]); setSelectedColumns([]);
    rowAnchor.current = null;
    setExcludedColumns(old => old.filter(column => column !== selection.ambient_column && column !== selection.current_column));
    setRemovedTemperatures(old => old.filter(column => column !== selection.ambient_column && column !== selection.current_column));
  }, [selection.ambient_column, selection.current_column, selection.thermocouples_per_sample]);
  const protectedColumn = (column: number) => column <= 2 || column === selection.ambient_column || column === selection.current_column
    || sourceColumnKind(table, selection, column, layout) === 'current';
  const movable = (column: number) => isTemperatureColumn(table, selection, column, layout);
  const snapshot = (): Snapshot => ({ order, excludedColumns, removedTemperatures,
    temperatureColumns: selection.temperature_columns, excludedRows: selection.excluded_rows });
  function commit(next: Snapshot) {
    setHistory(old => [...old, snapshot()]);
    setOrder(next.order); setExcludedColumns(next.excludedColumns); setRemovedTemperatures(next.removedTemperatures);
    onChange({ temperature_columns: next.temperatureColumns, excluded_rows: next.excludedRows });
    setSelectedRows([]); setSelectedColumns([]);
    rowAnchor.current = null;
  }
  function selectRows(rows: number[]) { setSelectedRows(rows); setSelectedColumns([]); rowAnchor.current = null; }
  function selectColumns(columns: number[]) {
    setSelectedColumns(columns.filter(column => !protectedColumn(column))); setSelectedRows([]); rowAnchor.current = null;
  }
  function toggleRow(row: number, checked: boolean, extend: boolean) {
    const anchor = extend && rowAnchor.current !== null ? rowAnchor.current : row;
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
    rowAnchor.current = anchor;
  }
  function exclude() {
    if (selectedRows.length) {
      commit({ ...snapshot(), excludedRows: [...new Set([...selection.excluded_rows, ...selectedRows])].sort((a, b) => a - b) });
    } else {
      const columns = selectedColumns.filter(column => !protectedColumn(column));
      commit({ ...snapshot(), excludedColumns: [...new Set([...excludedColumns, ...columns])],
        removedTemperatures: [...new Set([...removedTemperatures, ...columns.filter(column => selection.temperature_columns.includes(column))])],
        temperatureColumns: selection.temperature_columns.filter(column => !columns.includes(column)) });
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
        temperatureColumns: order.filter(column => active.has(column) && movable(column)) });
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
    commit({ ...snapshot(), order: next, excludedColumns: excludedColumns.filter(column => !moving.includes(column)),
      removedTemperatures: removedTemperatures.filter(column => !moving.includes(column)),
      temperatureColumns: next.filter(column => active.has(column) && movable(column)) });
  }
  function undo() {
    const previous = history.at(-1);
    if (!previous) return;
    setHistory(old => old.slice(0, -1)); setOrder(previous.order); setExcludedColumns(previous.excludedColumns);
    setRemovedTemperatures(previous.removedTemperatures); setSelectedColumns([]); setSelectedRows([]);
    rowAnchor.current = null;
    onChange({ temperature_columns: previous.temperatureColumns, excluded_rows: previous.excludedRows });
  }
  const excludedRowSet = new Set(selection.excluded_rows);
  const canExclude = selectedRows.some(row => !excludedRowSet.has(row))
    || selectedColumns.some(column => !protectedColumn(column) && !excludedColumns.includes(column));
  const canRestore = selectedRows.some(row => excludedRowSet.has(row))
    || selectedColumns.some(column => excludedColumns.includes(column));
  return { order, excludedColumns, selectedRows, selectedColumns, selectRows, selectColumns, toggleRow,
    exclude, restore, moveBefore, undo, protectedColumn, movable, canExclude, canRestore, canUndo: Boolean(history.length),
    restoreAllRows: () => commit({ ...snapshot(), excludedRows: [] }) };
}
