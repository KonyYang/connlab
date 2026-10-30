import { useEffect, useRef, useState, type ChangeEvent } from "react";
import { encryptStandaloneCopy, encryptStandaloneFolder, type FolderEncryptionSummary } from "../../api/client";

type FolderSelection = { name: string; files: File[]; ignored: number };

export function EncryptionTool() {
  const fileInput = useRef<HTMLInputElement>(null);
  const folderInput = useRef<HTMLInputElement>(null);
  const active = useRef(false);
  const generation = useRef(0);
  const [busy, setBusy] = useState<"file" | "folder" | null>(null);
  const [folder, setFolder] = useState<FolderSelection | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [downloaded, setDownloaded] = useState<string | null>(null);
  const [summary, setSummary] = useState<FolderEncryptionSummary | null>(null);

  useEffect(() => {
    folderInput.current?.setAttribute("webkitdirectory", "");
    return () => { generation.current += 1; };
  }, []);

  function chooseFolder(event: ChangeEvent<HTMLInputElement>) {
    if (active.current) return;
    const selected = Array.from(event.target.files ?? []);
    event.target.value = "";
    if (!selected.length) return;
    const files = selected.filter(file => /\.(docx?|xlsx?)$/i.test(file.name));
    setError(null); setDownloaded(null); setSummary(null);
    if (!files.length) { setFolder(null); setError("No supported Word or Excel files were found in this folder."); return; }
    setFolder({ name: files[0].webkitRelativePath.split("/")[0], files, ignored: selected.length - files.length });
  }

  function chooseFile(event: ChangeEvent<HTMLInputElement>) {
    if (active.current) return;
    const file = event.target.files?.[0];
    event.target.value = "";
    if (file) void run(file);
  }

  async function run(file?: File) {
    if (active.current || (!file && !folder)) return;
    active.current = true;
    const token = ++generation.current;
    setBusy(file ? "file" : "folder"); setError(null); setDownloaded(null); setSummary(null);
    if (file) setFolder(null);
    try {
      if (!file && folder) {
        if (folder.files.length > 500) throw new Error("Select at most 500 Word/Excel files in one folder.");
        if (folder.files.some(item => item.size > 100 * 1024 * 1024)
            || folder.files.reduce((total, item) => total + item.size, 0) > 500 * 1024 * 1024) {
          throw new Error("Folder uploads allow up to 100 MB per file and 500 MB in total.");
        }
      }
      const response = file ? { ...await encryptStandaloneCopy(file), summary: null } : await encryptStandaloneFolder(folder!.files);
      if (generation.current !== token) return;
      const fileName = response.fileName ?? (file ? file.name.replace(/(\.[^.]+)$/, "_Secured$1") : "Encrypted_Folder.zip");
      const url = URL.createObjectURL(response.blob);
      const anchor = document.createElement("a");
      try {
        anchor.href = url; anchor.download = fileName;
        document.body.append(anchor); anchor.click();
      } finally { anchor.remove(); URL.revokeObjectURL(url); }
      setDownloaded(fileName);
      setSummary(response.summary);
    } catch (reason) {
      if (generation.current === token) setError(reason instanceof Error ? reason.message : "Encryption failed. Select the source and retry.");
    } finally {
      if (generation.current === token) { active.current = false; setBusy(null); }
    }
  }

  return <article className="tools-card" aria-label="Encrypt a Copy">
    <div className="tools-card-heading"><h3>Select Office File or Folder</h3></div>
    <input ref={fileInput} type="file" hidden aria-label="Select Office File" accept=".doc,.docx,.xls,.xlsx,.pptx"
      disabled={Boolean(busy)} onChange={chooseFile} />
    <input ref={folderInput} type="file" multiple hidden aria-label="Select Office Folder"
      disabled={Boolean(busy)} onChange={chooseFolder} />
    <div className="tools-encryption-actions">
      <button className="primary-action tools-picker-action" type="button" disabled={Boolean(busy)} onClick={() => fileInput.current?.click()}>
        {busy === "file" ? "Starting..." : "Create Encrypted Copy"}
      </button>
      <button type="button" disabled={Boolean(busy)} onClick={() => folderInput.current?.click()}>Choose Folder</button>
    </div>
    {folder ? <div className="tools-folder-selection">
      <p><strong>{folder.name}</strong> · {folder.files.length} Word/Excel files, including subfolders.</p>
      {folder.ignored > 0 ? <p>{folder.ignored} other files ignored.</p> : null}
      <p>Downloads a ZIP with encrypted copies and a result list. Originals stay unchanged.</p>
      <div className="tools-encryption-actions">
        <button className="primary-action" type="button" disabled={Boolean(busy)} onClick={() => void run()}>
          {busy === "folder" ? "Encrypting Folder..." : "Encrypt Selected Folder"}
        </button>
        <button type="button" disabled={Boolean(busy)} aria-label="Cancel Folder Selection" onClick={() => setFolder(null)}>Cancel</button>
      </div>
    </div> : <p className="tools-card-hint">Folders: .doc, .docx, .xls, .xlsx, including subfolders.</p>}
    {error ? <p role="alert" className="tools-feedback tools-feedback-error">{error}</p> : null}
    {summary ? <p className={summary.failed ? "tools-feedback tools-feedback-warning" : "tools-feedback tools-feedback-success"}>
      {summary.succeeded === 0 ? "No files were encrypted. " : ""}
      {summary.succeeded} encrypted · {summary.failed} failed · {summary.skipped} skipped. See EncryptionSummary.csv in the ZIP.
    </p> : null}
    {downloaded ? <p role="status" aria-label="Downloaded File" className={summary?.succeeded === 0
      ? "tools-feedback tools-feedback-warning" : "tools-feedback tools-feedback-success"}>{downloaded}</p> : null}
  </article>;
}
