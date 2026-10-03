import { useEffect, useRef } from "react";

type Props = {
  fileName: string;
  busy: boolean;
  returnFocusTarget: HTMLButtonElement;
  onCancel: () => void;
  onConfirm: () => void;
};

export function CustomerReportRegenerationDialog({ fileName, busy, returnFocusTarget, onCancel, onConfirm }: Props) {
  const dialog = useRef<HTMLElement>(null);
  useEffect(() => {
    dialog.current?.querySelector<HTMLButtonElement>("button")?.focus();
    return () => { if (returnFocusTarget.isConnected && !returnFocusTarget.disabled) returnFocusTarget.focus(); };
  }, [returnFocusTarget]);

  return <div className="report-workspace-dialog-backdrop">
    <section ref={dialog} className="report-workspace-dialog report-workspace-regeneration-dialog"
      role="dialog" aria-modal="true" aria-labelledby="customer-regeneration-title"
      onKeyDown={(event) => {
        if (event.key === "Escape" && !busy) onCancel();
        if (event.key !== "Tab") return;
        const controls = Array.from(event.currentTarget.querySelectorAll<HTMLButtonElement>("button:not(:disabled)"));
        const first = controls[0], last = controls.at(-1);
        if (!first) { event.preventDefault(); return; }
        if (event.shiftKey && document.activeElement === first && last) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      }}>
      <h2 id="customer-regeneration-title">Archive and regenerate Customer Report</h2>
      <p>{fileName}</p>
      <p>The existing customer report will be kept in History/Report before the new report replaces it. The new report uses the current Internal Report; manual edits in the old customer report are not copied.</p>
      <div className="report-workspace-action-row">
        <button type="button" disabled={busy} onClick={onCancel}>Cancel</button>
        <button type="button" className="primary-action" disabled={busy} onClick={onConfirm}>
          {busy ? "Generating customer report..." : "Archive and regenerate"}
        </button>
      </div>
    </section>
  </div>;
}
