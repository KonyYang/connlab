import { useEffect, useMemo, useRef, useState } from "react";
import { inspectFeeForm, type FeeFormImportRow } from "../../api/client";
import type { FeeEvaluationPreviewRow } from "./feeEvaluationPreviewModel";
import { planFeeImport, type FeeImportChange, type FeeImportMode } from "./feeFormImportModel";
import "./feeFormImport.css";

const fieldLabels: Record<string, string> = {unitPrice: "Unit Price", unitType: "Unit Type", baseFee: "Base Fee",
  spendTime: "Man-hour", units: "Units", discount: "Discount (%)", notes: "Notes"};

export function FeeFormImportControl({projectId, rows, disabled, onApply}: {
  projectId: string; rows: FeeEvaluationPreviewRow[]; disabled: boolean; onApply: (changes: FeeImportChange[]) => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const request = useRef(0);
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState<FeeImportMode>("matrix");
  const [file, setFile] = useState<File | null>(null);
  const [source, setSource] = useState<FeeFormImportRow[] | null>(null);
  const [baseline, setBaseline] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [selections, setSelections] = useState<Record<string, number>>({});
  const signature = JSON.stringify(rows);
  const stale = source !== null && baseline !== signature;
  const plan = useMemo(() => planFeeImport(source ?? [], rows, mode, selections), [source, rows, mode, selections]);
  useEffect(() => () => { request.current += 1; }, []);
  useEffect(() => {
    if (open) dialog.current?.showModal();
    else if (dialog.current?.open) dialog.current.close();
  }, [open]);
  function close() {
    request.current += 1;
    setBusy(false);
    setOpen(false);
    setSource(null);
    setError("");
  }
  async function inspect() {
    if (!file || disabled) return;
    const generation = ++request.current;
    setBusy(true);
    setSource(null);
    setError("");
    setSelections({});
    try {
      const result = await inspectFeeForm(projectId, file);
      if (generation !== request.current) return;
      setSource(result.rows);
      setBaseline(signature);
    } catch (failure) {
      if (generation === request.current) setError(failure instanceof Error ? failure.message : "Unable to read Fee Form.");
    } finally {
      if (generation === request.current) setBusy(false);
    }
  }
  return <>
    <button type="button" className="fee-evaluation-file-button" disabled={disabled}
      onClick={() => { setMessage(""); setOpen(true); }}>Import Fee Form</button>
    {message && <span role="status">{message}</span>}
    <dialog ref={dialog} className="fee-form-import-dialog" aria-labelledby="fee-import-title"
      onCancel={close} onClose={() => { if (open) close(); }}>
      <h3 id="fee-import-title">Import Fee Form</h3>
      <p>Review before applying. Only the current draft changes; Confirm is still required for Fee authority.</p>
      <label>Import mode<select aria-label="Import mode" value={mode}
        onChange={event => { setMode(event.target.value as FeeImportMode); setSelections({}); }}>
        <option value="matrix">Same Matrix — restore fee rows</option>
        <option value="prices">Other project — reuse prices only</option>
      </select></label>
      <p>{mode === "matrix" ? "Groups must have the same ordered test descriptions. Unmatched groups stay unchanged. Empty numeric cells do not erase current values."
        : "Imports Unit Price, Unit Type and Base Fee only. Current quantities, hours, discounts and notes stay unchanged."}</p>
      <label>Fee Form file<input type="file" accept=".xls,.xlsx" aria-label="Fee Form file"
        onChange={event => { request.current += 1; setBusy(false); setSource(null); setError(""); setFile(event.target.files?.[0] ?? null); }} /></label>
      <button type="button" disabled={!file || busy || disabled} onClick={() => void inspect()}>{busy ? "Reading..." : "Inspect file"}</button>
      {error && <p role="alert">{error}</p>}
      {stale && <p role="alert">Current fee rows changed. Inspect the file again before applying.</p>}
      {source && <>
        <p>{plan.changes.length} matching rows. Existing values shown below will be replaced.</p>
        {plan.conflicts.map(conflict => <label key={conflict.key}>{conflict.description} — choose a price
          <select aria-label={`Price for ${conflict.description}`} value={selections[conflict.key] ?? -1}
            onChange={event => setSelections(current => ({...current, [conflict.key]: Number(event.target.value)}))}>
            <option value={-1}>Skip this test item</option>
            {conflict.candidates.map((candidate, index) => <option key={index} value={index}>
              {candidate.unitPrice} / {candidate.unitType} / Base Fee {candidate.baseFee}
            </option>)}
          </select></label>)}
        {plan.skipped.length > 0 && <details><summary>{plan.skipped.length} unmatched groups / test items remain unchanged</summary>
          <ul>{plan.skipped.map((text, index) => <li key={index}>{text}</li>)}</ul></details>}
        <div className="fee-form-import-preview"><table><thead><tr><th>Group / Step</th><th>Description</th><th>Current → Imported</th></tr></thead>
          <tbody>{plan.changes.map(change => <tr key={change.row.lineId}>
            <td>{change.row.groupLabel} / {change.row.stepToken}</td><td>{change.row.description}</td>
            <td>{Object.entries(change.values).map(([field, value]) => <div key={field}>
              {fieldLabels[field]}: {String(change.row[field as keyof FeeEvaluationPreviewRow] ?? "")} → {value || "(empty)"}
            </div>)}</td>
          </tr>)}</tbody></table></div>
        <button type="button" className="is-primary" disabled={disabled || stale || busy || !plan.changes.length}
          onClick={() => { if (disabled || stale) return; onApply(plan.changes); setMessage(`${plan.changes.length} rows imported into draft. Review and use Confirm for Fee authority.`); close(); }}>
          Apply {plan.changes.length} rows to draft
        </button>
      </>}
      <button type="button" onClick={close}>Cancel import</button>
    </dialog>
  </>;
}
