import { useEffect, useId, useRef, useState, type ReactElement, type RefObject } from "react";

export type EquipmentSourceSelection = { equipmentFile: File } | { referencesText: string };

export function EquipmentSourceDialog({ reportName, busy, error: requestError, returnFocus, onCancel, onUpdate, onSourceChange }: {
  reportName: string;
  busy: boolean;
  error: string | null;
  returnFocus: RefObject<HTMLButtonElement | null>;
  onCancel: () => void;
  onUpdate: (source: EquipmentSourceSelection) => Promise<void>;
  onSourceChange: () => void;
}): ReactElement {
  const [mode, setMode] = useState<"file" | "text">("file");
  const [equipment, setEquipment] = useState<File | null>(null);
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const dialog = useRef<HTMLDialogElement>(null);
  const titleId = useId();
  useEffect(() => {
    const element = dialog.current!;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    element.showModal();
    element.querySelector<HTMLInputElement>("input:checked")?.focus();
    return () => {
      element.close();
      document.body.style.overflow = previousOverflow;
      if (returnFocus.current?.isConnected) returnFocus.current.focus();
    };
  }, [returnFocus]);

  function clearError(): void { setError(null); onSourceChange(); }

  function confirm(): void {
    if (busy) return;
    if (mode === "file") {
      if (!equipment) { setError("Select EquipmentID.docx or enter equipment IDs."); return; }
      setError(null);
      void onUpdate({ equipmentFile: equipment });
    } else {
      if (!text.trim()) { setError("Select EquipmentID.docx or enter equipment IDs."); return; }
      setError(null);
      void onUpdate({ referencesText: text.trim() });
    }
  }

  return <dialog ref={dialog} className="tools-equipment-dialog" aria-labelledby={titleId} aria-busy={busy}
    onCancel={(event) => { event.preventDefault(); if (!busy) onCancel(); }}>
    <h2 id={titleId}>Equipment Source</h2>
    <p className="tools-dialog-report">{reportName}</p>
    <fieldset className="tools-equipment-source" disabled={busy}>
      <legend>Use equipment IDs from</legend>
      <div className="tools-equipment-modes">
        <label><input type="radio" name="equipment-source" checked={mode === "file"} onChange={() => {
          setMode("file"); setText(""); clearError();
        }} /> EquipmentID.docx</label>
        <label><input type="radio" name="equipment-source" checked={mode === "text"} onChange={() => {
          setMode("text"); setEquipment(null); clearError();
        }} /> Enter Equipment IDs</label>
      </div>
      {mode === "file" ? <label className="tools-file-picker">
        <span>Select EquipmentID.docx</span>
        <input type="file" accept=".docx" onChange={(event) => {
          const file = event.target.files?.[0] ?? null;
          if (file) { setEquipment(file); clearError(); }
        }} />
      </label> : <label className="tools-file-picker">
        <span>Equipment IDs</span>
        <textarea rows={3} placeholder="DG-Q-0033, DG-L-0002" value={text} onChange={(event) => {
          setText(event.target.value); clearError();
        }} />
      </label>}
    </fieldset>
    <p className="tools-card-hint">Downloads an updated copy. The source report is unchanged.</p>
    {(error || requestError) && <p className="tools-feedback tools-feedback-error" role="alert">{error || requestError}</p>}
    <div className="tools-dialog-actions">
      <button className="primary-action" type="button" disabled={busy} onClick={confirm}>
        {busy ? "Updating..." : "Update"}
      </button>
      <button className="secondary-action" type="button" disabled={busy} onClick={onCancel}>Cancel</button>
    </div>
  </dialog>;
}
