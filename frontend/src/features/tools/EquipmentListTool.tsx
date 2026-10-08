import { useEffect, useRef, useState, type ReactElement } from "react";
import { updateStandaloneEquipmentList, type EquipmentReview } from "../../api/client";
import { EquipmentSourceDialog, type EquipmentSourceSelection } from "./EquipmentSourceDialog";

export function EquipmentListTool(): ReactElement {
  const [report, setReport] = useState<File | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [name, setName] = useState<string | null>(null);
  const [review, setReview] = useState<EquipmentReview | null>(null);
  const token = useRef(0);
  const running = useRef(false);
  const reportInput = useRef<HTMLInputElement>(null);
  const openButton = useRef<HTMLButtonElement>(null);
  useEffect(() => () => { token.current += 1; }, []);

  function clearFeedback(): void {
    setError(null);
    setName(null);
    setReview(null);
  }

  async function run(source: EquipmentSourceSelection): Promise<void> {
    if (running.current) return;
    clearFeedback();
    if (!report) { setError("Select an Internal Report .docx first."); return; }
    const current = ++token.current;
    running.current = true;
    setBusy(true);
    try {
      const result = await updateStandaloneEquipmentList(report, source);
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
      setDialogOpen(false);
    } catch (caught) {
      if (current === token.current) setError(caught instanceof Error ? caught.message : "The report could not be updated.");
    } finally {
      if (current === token.current) { running.current = false; setBusy(false); }
    }
  }

  return <article className="tools-card tools-equipment-card" aria-label="Update Equipment List">
    <div className="tools-card-heading">
      <h3>Select Internal Report</h3>
    </div>
    <input ref={reportInput} type="file" hidden aria-label="Internal Report for Equipment Update" accept=".docx" disabled={busy}
      onChange={(event) => {
        const file = event.target.files?.[0] ?? null;
        event.target.value = "";
        if (running.current || !file) return;
        setReport(file); clearFeedback(); setDialogOpen(true);
      }} />
    <button ref={openButton} className="primary-action tools-picker-action" type="button" disabled={busy || dialogOpen}
      onClick={() => reportInput.current?.click()}>
      Update Equipment List
    </button>
    {dialogOpen && report && <EquipmentSourceDialog reportName={report.name} busy={busy} error={error}
      returnFocus={openButton} onCancel={() => { if (!running.current) setDialogOpen(false); }} onUpdate={run}
      onSourceChange={() => setError(null)} />}
    {name && <p className="tools-feedback tools-feedback-success" role="status" aria-label="Downloaded File">{name}</p>}
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
