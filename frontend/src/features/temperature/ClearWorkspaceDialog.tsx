import { useEffect, useRef } from 'react';

export function ClearWorkspaceDialog({ busy, onCancel, onConfirm }: {
  busy: boolean; onCancel: () => void; onConfirm: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const cancel = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    const node = dialog.current;
    const previous = document.activeElement as HTMLElement | null;
    node?.showModal();
    cancel.current?.focus();
    return () => { node?.close(); if (previous?.isConnected) previous.focus(); };
  }, []);
  return <dialog ref={dialog} className="temperature-exit-dialog" aria-labelledby="temperature-exit-title"
    aria-describedby="temperature-exit-help" onCancel={event => { event.preventDefault(); if (!busy) onCancel(); }}>
    <h2 id="temperature-exit-title">Clear workspace?</h2>
    <p id="temperature-exit-help">Clear the current data, results and Undo history and return to Tools?
      {' '}Original files and downloaded Excel files will not be deleted.</p>
    <div><button ref={cancel} type="button" disabled={busy} onClick={onCancel}>Cancel</button>
      <button type="button" className="primary-action" disabled={busy} onClick={onConfirm}>{busy ? 'Clearing…' : 'Clear and Return'}</button></div>
  </dialog>;
}
