import { useEffect, useId, useRef, useState } from "react";
import { encryptLocalFile, encryptLocalFolder, type LocalFolderEncryptionResult } from "../../api/client";
import { ToolsFeedback } from "./ToolsFeedback";

export function EncryptionTool() {
  const active = useRef(false);
  const generation = useRef(0);
  const choicesId = useId();
  const [expanded, setExpanded] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Extract<LocalFolderEncryptionResult, { cancelled: false }> | null>(null);
  const [resultMode, setResultMode] = useState<"file" | "folder" | null>(null);

  useEffect(() => () => { generation.current += 1; }, []);

  async function run(mode: "file" | "folder") {
    if (active.current) return;
    active.current = true;
    const token = ++generation.current;
    setBusy(true);
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
      if (generation.current === token) { active.current = false; setBusy(false); }
    }
  }

  const saved = result?.entries.find(entry => entry.status === "Encrypted");
  return <article className="tools-action-group" aria-label="Encrypt a Copy" aria-busy={busy}>
    <button className="primary-action tools-picker-action" type="button" aria-expanded={expanded}
      aria-controls={choicesId} disabled={busy} onClick={() => setExpanded(!expanded)}>
      {busy ? "Working..." : "Encrypt Files"}
    </button>
    <div id={choicesId} className="tools-encryption-actions" hidden={!expanded}>
      <p className="tools-card-hint">Encrypted copies are saved beside the originals. Folder selection excludes subfolders.</p>
      <button className="secondary-action" type="button" disabled={busy} onClick={() => void run("file")}>
        Choose File
      </button>
      <button className="secondary-action" type="button" disabled={busy} onClick={() => void run("folder")}>
        Choose Folder
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
