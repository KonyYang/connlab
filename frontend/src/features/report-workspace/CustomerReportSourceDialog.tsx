import { useEffect, useRef, useState } from "react";

type Props = {
  direct?: boolean;
  busy: boolean;
  error: string | null;
  onCancel: () => void;
  onGenerate: (file: File) => Promise<boolean>;
};

export function CustomerReportSourceDialog({ direct, busy, error: requestError, onCancel, onGenerate }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const dialog = useRef<HTMLElement>(null);
  useEffect(() => {
    const previous = document.activeElement;
    dialog.current?.querySelector<HTMLInputElement>("input")?.focus();
    return () => { if (previous instanceof HTMLElement && previous.isConnected) previous.focus(); };
  }, []);
  return <div className="report-workspace-dialog-backdrop">
    <section ref={dialog} className="report-workspace-dialog" role="dialog" aria-modal="true" aria-labelledby="customer-source-title"
      onKeyDown={(event) => {
        if (event.key === "Escape" && !busy) onCancel();
        if (event.key !== "Tab") return;
        const controls = Array.from(event.currentTarget.querySelectorAll<HTMLElement>("input:not(:disabled), button:not(:disabled)"));
        const first = controls[0], last = controls.at(-1);
        if (event.shiftKey && document.activeElement === first && last) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last && first) { event.preventDefault(); first.focus(); }
      }}>
      <h2 id="customer-source-title">{direct ? "Create customer copy" : "Select Internal Report"}</h2>
      <p>{direct ? "Choose the finished internal report for a separate customer review copy." : "The current Internal Report is missing. Select an existing Internal Report (.docx) to generate a customer report download. The source file is not changed."}</p>
      <label className="report-workspace-file-field">Internal Report file
        <input type="file" accept=".docx" disabled={busy} onChange={(event) => {
          const next = event.target.files?.[0] ?? null;
          setError(next && !/\.docx$/i.test(next.name) ? "Select an Internal Report in .docx format." : null);
          setFile(next && /\.docx$/i.test(next.name) ? next : null);
        }} />
      </label>
      {direct && file && <p className="report-source-name" title={file.name}>{file.name}</p>}
      {error ? <p role="alert">{error}</p> : null}
      {requestError ? <p role="alert">{requestError}</p> : null}
      <div className="report-workspace-action-row">
        <button type="button" className="primary-action" disabled={!file || busy} onClick={() => { if (file) void onGenerate(file); }}>
          {busy ? "Preparing…" : direct ? "Generate review copy" : "Generate Customer Report"}
        </button>
        <button type="button" disabled={busy} onClick={onCancel}>Cancel</button>
      </div>
    </section>
  </div>;
}
