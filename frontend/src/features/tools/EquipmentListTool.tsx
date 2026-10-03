import { useEffect, useRef, useState, type ReactElement } from "react";
import { updateStandaloneEquipmentList, type EquipmentReview } from "../../api/client";
import { UiIcon } from "../../components/common/UiIcon";

export function EquipmentListTool(): ReactElement {
  const [report, setReport] = useState<File | null>(null);
  const [equipment, setEquipment] = useState<File | null>(null);
  const [mode, setMode] = useState<"file" | "text">("file");
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [name, setName] = useState<string | null>(null);
  const [review, setReview] = useState<EquipmentReview | null>(null);
  const token = useRef(0);
  const running = useRef(false);
  useEffect(() => () => { token.current += 1; }, []);

  function clearFeedback(): void {
    setError(null);
    setName(null);
    setReview(null);
  }

  async function run(): Promise<void> {
    if (running.current) return;
    clearFeedback();
    if (!report) { setError("Select an Internal Report .docx first."); return; }
    if (mode === "file" ? !equipment : !text.trim()) {
      setError("Select EquipmentID.docx or enter equipment IDs."); return;
    }
    const current = ++token.current;
    running.current = true;
    setBusy(true);
    try {
      const result = await updateStandaloneEquipmentList(report, mode === "file"
        ? { equipmentFile: equipment! } : { referencesText: text.trim() });
      if (current !== token.current) return;
      const fileName = result.fileName ?? `${report.name.replace(/\.docx$/i, "")}_EquipmentUpdated.docx`;
      const url = URL.createObjectURL(result.blob);
      const anchor = document.createElement("a");
      try {
        anchor.href = url;
        anchor.download = fileName;
        document.body.append(anchor);
        anchor.click();
      } finally {
        anchor.remove();
        URL.revokeObjectURL(url);
      }
      setName(fileName);
      setReview(result.review);
    } catch (caught) {
      if (current === token.current) setError(caught instanceof Error ? caught.message : "The report could not be updated.");
    } finally {
      if (current === token.current) { running.current = false; setBusy(false); }
    }
  }

  return <article className="tools-card tools-equipment-card">
    <div className="tools-card-heading">
      <span className="tools-card-icon" aria-hidden="true"><UiIcon name="file" /></span>
      <h3>Update Equipment List</h3>
    </div>
    <p>Update the Equipment List in any compatible Internal Report using the calibration workbook configured in Settings.</p>
    <label className="tools-file-picker">
      <span>Internal Report for Equipment Update</span>
      <input type="file" accept=".docx" disabled={busy} onChange={(event) => {
        setReport(event.target.files?.[0] ?? null); clearFeedback();
      }} />
    </label>
    <div className="tools-selected-file">{report?.name ?? "No file selected"}</div>
    <fieldset className="tools-equipment-source" disabled={busy}>
      <legend>Equipment Source</legend>
      <div className="tools-equipment-modes">
        <label><input type="radio" name="equipment-source" checked={mode === "file"} onChange={() => {
          setMode("file"); setText(""); clearFeedback();
        }} /> EquipmentID.docx</label>
        <label><input type="radio" name="equipment-source" checked={mode === "text"} onChange={() => {
          setMode("text"); setEquipment(null); clearFeedback();
        }} /> Enter Equipment IDs</label>
      </div>
      {mode === "file" ? <label className="tools-file-picker">
        <span>Select EquipmentID.docx</span>
        <input type="file" accept=".docx" onChange={(event) => {
          setEquipment(event.target.files?.[0] ?? null); clearFeedback();
        }} />
      </label> : <label className="tools-file-picker">
        <span>Equipment IDs</span>
        <textarea rows={3} placeholder="DG-Q-0033, DG-L-0002" value={text} onChange={(event) => {
          setText(event.target.value); clearFeedback();
        }} />
      </label>}
    </fieldset>
    <p className="tools-card-hint">Downloads an _EquipmentUpdated copy. The original report and project folders are not changed.</p>
    {error && <p className="tools-feedback tools-feedback-error" role="alert">{error}</p>}
    <button className="primary-action" type="button" disabled={busy} onClick={() => void run()}>
      {busy ? "Updating..." : "Update Equipment List"}
    </button>
    {name && <div className="tools-equipment-completion" role="status">
      <p>Updated report downloaded. The original file was not changed.</p>
      <span>{name}</span>
    </div>}
    {review && <EquipmentReviewFeedback review={review} />}
  </article>;
}

function EquipmentReviewFeedback({ review }: { review: EquipmentReview }): ReactElement | null {
  const categories = [
    ["unmatched", "Not Registered", "Check registration in the calibration workbook."],
    ["incomplete", "Missing Information", "Complete the equipment information in the calibration workbook."],
    ["expired", "Expired Calibration", "Confirm calibration validity before using the report."],
  ] as const;
  const issues = categories.filter(([key]) => review[key].length || review.omitted[key]);
  if (!issues.length) return null;
  return <div className="tools-equipment-review" role="alert">
    <h4>Equipment List Needs Review</h4>
    {issues.map(([key, label, guidance]) => <p key={key}>
      {label}: {review[key].join(", ")}{review.omitted[key] ? ` (+${review.omitted[key]} more)` : ""}. {guidance}
    </p>)}
  </div>;
}
