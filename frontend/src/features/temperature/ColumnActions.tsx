import { useId, useLayoutEffect, useRef, useState, type KeyboardEvent as ReactKeyboardEvent, type RefObject } from 'react';
import { createPortal } from 'react-dom';
import { useContextMenuFocus } from './useContextMenuFocus';

export type ColumnMenuAnchor = { column: number; left: number; top: number; trigger: HTMLElement };

export function ColumnActions({ anchor, root, columns, selectedCount, disabled, canExclude, canRestore, onExclude, onRestore, onMove, onClose }: {
  root: RefObject<HTMLDivElement | null>;
  anchor: ColumnMenuAnchor; columns: { id: number; label: string }[]; selectedCount: number; disabled: boolean;
  canExclude: boolean; canRestore: boolean; onExclude: () => void; onRestore: () => void;
  onMove: (column: number | null) => void; onClose: () => void;
}) {
  const moveTrigger = useRef<HTMLButtonElement>(null);
  const destinations = useRef<HTMLDivElement>(null);
  const destinationsId = useId();
  const [expanded, setExpanded] = useState(false);
  const [destinationTop, setDestinationTop] = useState(8);
  // Reserve room on the right instead of covering the Move Before entry at the viewport edge.
  const menuWidth = Math.min(268, (window.innerWidth - 24) / 2);
  const menuLeft = expanded ? Math.max(8, Math.min(anchor.left, window.innerWidth - menuWidth * 2 - 16)) : anchor.left;
  useLayoutEffect(() => {
    if (!expanded) return;
    const height = destinations.current?.getBoundingClientRect().height ?? 0;
    setDestinationTop(Math.max(8, Math.min(moveTrigger.current!.getBoundingClientRect().top, window.innerHeight - height - 8)));
    destinations.current?.querySelector<HTMLElement>('button:not(:disabled)')?.focus();
  }, [expanded]);
  function submenuKey(event: ReactKeyboardEvent<HTMLDivElement>) {
    if (!expanded) return;
    if (event.key === 'Escape' || event.key === 'ArrowLeft') {
      event.preventDefault(); event.stopPropagation();
      setExpanded(false); moveTrigger.current?.focus();
    } else if (destinations.current?.contains(event.target as Node) && ['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key)) {
      event.preventDefault();
      const items = Array.from(destinations.current.querySelectorAll<HTMLButtonElement>('button:not(:disabled)'));
      if (!items.length) return;
      const index = items.indexOf(document.activeElement as HTMLButtonElement);
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? items.length - 1
        : (index + (event.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
      items[next].focus();
    }
  }
  useContextMenuFocus(root, anchor, onClose);
  return createPortal(<div ref={root} role="dialog" aria-label={`Column ${anchor.column} Actions`}
    className="temperature-context-menu" onKeyDown={submenuKey}
    style={{ left: menuLeft, top: anchor.top, ...(expanded ? { width: menuWidth } : {}) }}>
    <button type="button" disabled={disabled || !canExclude} onClick={onExclude}>Exclude Column{selectedCount > 1 ? 's' : ''}</button>
    {canRestore && <button type="button" disabled={disabled} onClick={onRestore}>Restore Column{selectedCount > 1 ? 's' : ''}</button>}
    <button ref={moveTrigger} type="button" className="temperature-column-destination" disabled={disabled}
      aria-haspopup="menu" aria-expanded={expanded} aria-controls={expanded ? destinationsId : undefined}
      onClick={() => setExpanded(old => !old)} onKeyDown={event => {
        if (event.key === 'ArrowRight') {
          event.preventDefault(); setExpanded(true);
          destinations.current?.querySelector<HTMLElement>('button:not(:disabled)')?.focus();
        }
      }}>Move Before<span aria-hidden="true" /></button>
    {expanded && <div ref={destinations} id={destinationsId} role="menu" aria-label="Move Before Destinations"
      className="temperature-column-submenu" style={{ left: menuLeft + menuWidth + 4, top: destinationTop, width: menuWidth }}>
      {columns.map(column => <button type="button" role="menuitem" key={column.id} disabled={disabled}
        onClick={() => onMove(column.id)}>{column.label}</button>)}
      <button type="button" role="menuitem" disabled={disabled} onClick={() => onMove(null)}>End Of Temperature Columns</button>
    </div>}
  </div>, document.body);
}
