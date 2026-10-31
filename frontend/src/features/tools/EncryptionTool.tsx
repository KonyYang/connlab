import { useEffect, useRef, useState } from "react";
import { encryptLocalFile, encryptLocalFolder, type LocalFolderEncryptionResult } from "../../api/client";
import { ToolsFeedback } from "./ToolsFeedback";

export function EncryptionTool() {
  const active = useRef(false);
  const generation = useRef(0);
  const [busy, setBusy] = useState<"file" | "folder" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Extract<LocalFolderEncryptionResult, { cancelled: false }> | null>(null);
  const [resultMode, setResultMode] = useState<"file" | "folder" | null>(null);

  useEffect(() => () => { generation.current += 1; }, []);

  async function run(mode: "file" | "folder") {
    if (active.current) return;
    active.current = true;
    const token = ++generation.current;
    setBusy(mode);
    try {
      const response = await (mode === "file" ? encryptLocalFile() : encryptLocalFolder());
      if (generation.current === token && !response.cancelled) {
        setResult(response); setResultMode(mode); setError(null);
      }
    } catch (reason) {
      if (generation.current === token) {
        setError(reason instanceof Error ? reason.message : "Encryption failed. Select the source and retry.");
        setResult(null);
      }
    } finally {
      if (generation.current === token) { active.current = false; setBusy(null); }
    }
  }

  const saved = result?.entries.find(entry => entry.status === "Encrypted");
  return <article className="tools-action-group" aria-label="Encrypt a Copy" aria-busy={Boolean(busy)}>
    <div className="tools-encryption-actions">
      <button className="primary-action tools-picker-action" type="button" title="Select a Word, Excel or PowerPoint file. Save a _Secured copy beside the original." disabled={Boolean(busy)} onClick={() => void run("file")}>
        {busy === "file" ? "Working..." : "Encrypt File"}
      </button>
      <button className="secondary-action" type="button" title="Encrypt Word, Excel and PowerPoint files directly in the selected folder. Save _Secured copies beside originals. Subfolders are excluded." disabled={Boolean(busy)} onClick={() => void run("folder")}>
        {busy === "folder" ? "Working..." : "Batch Encrypt Files"}
      </button>
    </div>
    {(error || result) && <ToolsFeedback><div className="tools-action-feedback">
      {error ? <p role="alert" className="tools-feedback tools-feedback-error">{error}</p> : null}
      {result ? <div className="tools-folder-selection" role={resultMode === "folder" ? "status" : undefined}>
        {resultMode === "file" && saved ? <p role="status" aria-label="Saved Encrypted File" className="tools-feedback tools-feedback-success">
          Saved: {saved.output}
        </p> : <p className={result.summary.failed ? "tools-feedback tools-feedback-warning" : "tools-feedback tools-feedback-success"}>
          {result.summary.succeeded === 0 ? "No files were encrypted. " : ""}
          {result.summary.succeeded} encrypted · {result.summary.failed} failed · {result.summary.skipped} skipped.
        </p>}
        <p className="tools-feedback" title={result.folder}>{result.folder}</p>
      </div> : null}
    </div></ToolsFeedback>}
  </article>;
}
