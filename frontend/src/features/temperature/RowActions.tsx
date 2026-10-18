import type { RefObject } from 'react';
import { createPortal } from 'react-dom';
import { useContextMenuFocus } from './useContextMenuFocus';

export type RowMenuAnchor = { row: number; left: number; top: number; trigger: HTMLElement };

export function RowActions({ anchor, root, selectedCount, disabled, canExclude, onExclude, onClose }: {
  anchor: RowMenuAnchor; root: RefObject<HTMLDivElement | null>; selectedCount: number;
  disabled: boolean; canExclude: boolean; onExclude: () => void; onClose: () => void;
}) {
  useContextMenuFocus(root, anchor, onClose);
  return createPortal(<div ref={root} role="dialog" aria-label="Row Actions" tabIndex={-1} className="temperature-context-menu"
    style={{ left: anchor.left, top: anchor.top }}>
    <button type="button" disabled={disabled || !canExclude} onClick={onExclude}>Exclude Selected Rows ({selectedCount})</button>
  </div>, document.body);
}
