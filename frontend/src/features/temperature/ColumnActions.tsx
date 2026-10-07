import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { columnLetter } from './sourceColumns';

export type ColumnMenuAnchor = { column: number; left: number; top: number; trigger: HTMLElement };

export function ColumnActions({ anchor, columnLabel, columns, selectedCount, disabled, canExclude, canRestore, onExclude, onRestore, onMove, onClose }: {
  columnLabel: string;
  anchor: ColumnMenuAnchor; columns: { id: number; label: string }[]; selectedCount: number; disabled: boolean;
  canExclude: boolean; canRestore: boolean; onExclude: () => void; onRestore: () => void;
  onMove: (column: number | null) => void; onClose: () => void;
}) {
  const root = useRef<HTMLDivElement>(null);
  const [destination, setDestination] = useState(columns[0]?.id.toString() ?? 'end');
  useEffect(() => {
    const close = () => { onClose(); anchor.trigger.focus(); };
    const key = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { event.preventDefault(); close(); }
      if (event.key === 'Tab') {
        const controls = Array.from(root.current?.querySelectorAll<HTMLElement>('button:not(:disabled), select:not(:disabled)') ?? []);
        const first = controls[0], last = controls.at(-1);
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
      }
    };
    const outside = (event: PointerEvent) => {
      if (!root.current?.contains(event.target as Node) && !anchor.trigger.contains(event.target as Node)) onClose();
    };
    const scroll = (event: Event) => { if (!root.current?.contains(event.target as Node)) onClose(); };
    root.current?.querySelector<HTMLElement>('button:not(:disabled),select:not(:disabled)')?.focus();
    document.addEventListener('keydown', key); document.addEventListener('pointerdown', outside);
    window.addEventListener('resize', close); window.addEventListener('scroll', scroll, true);
    return () => {
      document.removeEventListener('keydown', key); document.removeEventListener('pointerdown', outside);
      window.removeEventListener('resize', close); window.removeEventListener('scroll', scroll, true);
    };
  }, [anchor, onClose]);
  return createPortal(<div ref={root} role="dialog" aria-label={`Column ${columnLetter(anchor.column)} Actions`}
    className="temperature-column-menu" style={{ left: anchor.left, top: anchor.top }}>
    <div className="temperature-column-menu-heading"><span title={columnLabel}>{selectedCount === 1 ? columnLabel : `${selectedCount} Columns Selected`}</span>
      <button type="button" onClick={() => { onClose(); anchor.trigger.focus(); }} aria-label="Close Column Actions">Close</button></div>
    <button type="button" disabled={disabled || !canExclude} onClick={onExclude}>Exclude Column{selectedCount > 1 ? 's' : ''}</button>
    {canRestore && <button type="button" disabled={disabled} onClick={onRestore}>Restore Column{selectedCount > 1 ? 's' : ''}</button>}
    <label>Move Before<select value={destination} disabled={disabled} onChange={event => setDestination(event.target.value)}>
      {columns.map(column => <option key={column.id} value={column.id}>{column.label}</option>)}
      <option value="end">End Of Temperature Columns</option>
    </select></label>
    <button type="button" className="temperature-column-move" disabled={disabled} onClick={() => onMove(destination === 'end' ? null : Number(destination))}>Move</button>
  </div>, document.body);
}
