import { useEffect, useRef, useState, type ChangeEvent } from "react";
import { encryptStandaloneCopy, encryptLocalFolder, type LocalFolderEncryptionResult } from "../../api/client";

export function EncryptionTool() {
  const fileInput = useRef<HTMLInputElement>(null);
  const active = useRef(false);
  const generation = useRef(0);
  const [busy, setBusy] = useState<"file" | "folder" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [downloaded, setDownloaded] = useState<string | null>(null);
  const [folder, setFolder] = useState<Extract<LocalFolderEncryptionResult, { cancelled: false }> | null>(null);

  useEffect(() => () => { generation.current += 1; }, []);

  function chooseFile(event: ChangeEvent<HTMLInputElement>) {
    if (active.current) return;
    const file = event.target.files?.[0];
    event.target.value = "";
    if (file) void run(file);
  }

  async function run(file?: File) {
    if (active.current) return;
    active.current = true;
    const token = ++generation.current;
    setBusy(file ? "file" : "folder"); setError(null);
    try {
      if (!file) {
        const result = await encryptLocalFolder();
        if (generation.current === token && !result.cancelled) {
          setFolder(result); setDownloaded(null);
        }
        return;
      }
      const response = await encryptStandaloneCopy(file);
      if (generation.current !== token) return;
      const fileName = response.fileName ?? file.name.replace(/(\.[^.]+)$/, "_Secured$1");
      const url = URL.createObjectURL(response.blob);
      const anchor = document.createElement("a");
      try {
        anchor.href = url; anchor.download = fileName;
        document.body.append(anchor); anchor.click();
      } finally { anchor.remove(); URL.revokeObjectURL(url); }
      setDownloaded(fileName); setFolder(null);
    } catch (reason) {
      if (generation.current === token) setError(reason instanceof Error ? reason.message : "Encryption failed. Select the source and retry.");
    } finally {
      if (generation.current === token) { active.current = false; setBusy(null); }
    }
  }

  const failed = folder?.entries.filter(entry => entry.status === "Failed") ?? [];
  return <article className="tools-card" aria-label="Encrypt a Copy" aria-busy={Boolean(busy)}>
    <div className="tools-card-heading"><h3>Select Office File or Folder</h3></div>
    <input ref={fileInput} type="file" hidden aria-label="Select Office File" accept=".doc,.docx,.xls,.xlsx,.pptx"
      disabled={Boolean(busy)} onChange={chooseFile} />
    <div className="tools-encryption-actions">
      <button className="primary-action tools-picker-action" type="button" disabled={Boolean(busy)} onClick={() => fileInput.current?.click()}>
        {busy === "file" ? "Starting..." : "Create Encrypted Copy"}
      </button>
      <button className="secondary-action" type="button" disabled={Boolean(busy)} onClick={() => void run()}>
        {busy === "folder" ? "Working..." : "Choose Folder"}
      </button>
    </div>
    <p className="tools-card-hint">Folders: .doc, .docx, .xls, .xlsx, including subfolders. Saves _Secured copies beside originals.</p>
    {error ? <p role="alert" className="tools-feedback tools-feedback-error">{error}</p> : null}
    {folder ? <div className="tools-folder-selection" role="status">
      <p className={folder.summary.failed ? "tools-feedback tools-feedback-warning" : "tools-feedback tools-feedback-success"}>
        {folder.summary.succeeded === 0 ? "No files were encrypted. " : ""}
        {folder.summary.succeeded} encrypted · {folder.summary.failed} failed · {folder.summary.skipped} skipped.
      </p>
      <p className="tools-feedback" title={folder.folder}>{folder.folder}</p>
      {failed.length > 0 ? <details><summary>Failed files ({failed.length})</summary>
        <ul>{failed.map(entry => <li key={entry.file}>{entry.file}: {entry.reason}</li>)}</ul>
      </details> : null}
    </div> : null}
    {downloaded ? <p role="status" aria-label="Downloaded File" className="tools-feedback tools-feedback-success">{downloaded}</p> : null}
  </article>;
}
