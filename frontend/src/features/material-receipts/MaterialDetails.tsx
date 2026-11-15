import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import type { ReferenceProject } from "../../api/referenceLibrary";
import { openReferenceFile } from "../../api/referenceLibrary";
import { editReceiptMetadata, getReceiptDetail, type ReceiptDetail } from "../../api/materialReceipts";
import "./materials.css";

export function MaterialDetails({ project, onClose, onBrowse, onProject, onChanged, onSupplement }: {
 project: ReferenceProject; onClose: () => void; onBrowse: (key: string) => void;
 onProject: (id: string) => void; onChanged: () => void; onSupplement?: (project: ReferenceProject) => void;
}) {
 const [detail, setDetail] = useState<ReceiptDetail | null>(null);
 const [editing, setEditing] = useState(false);
 const [product, setProduct] = useState("");
 const [tests, setTests] = useState("");
 const [state, setState] = useState("completed");
 const [busy, setBusy] = useState(false);
 const [error, setError] = useState("");
 const id = project.receipt_id ?? (project.key.startsWith("receipt:") ? project.key.slice(8) : null);
 useEffect(() => {
  let live = true;
  if (id) void getReceiptDetail(id).then(value => { if (live) setDetail(value); })
   .catch(cause => { if (live) setError((cause as Error).message); });
  return () => { live = false; };
 }, [id]);
 async function act(action: () => Promise<void>) {
  setBusy(true); setError("");
  try { await action(); } catch (cause) { setError((cause as Error).message); } finally { setBusy(false); }
 }
 const path = detail?.folder_path ?? project.folder_path;
 const available = detail?.available ?? project.available;
 function edit() {
  if (!detail) return;
  setProduct(detail.product_name); setTests(detail.test_keywords); setState(detail.material_state); setEditing(true);
 }
 return createPortal(<div className="materials-overlay"><section className="materials-dialog" role="dialog" aria-modal="true" aria-labelledby="materials-detail-title">
  <header><h2 id="materials-detail-title">{project.number || "Project materials"}</h2><button disabled={busy} onClick={onClose}>Close details</button></header>
  {error && <p role="alert">{error}</p>}
  <strong>{detail?.product_name ?? project.title}</strong>
  {(detail?.description || project.description) && <p>{detail?.description ?? project.description}</p>}
  <p>Test items: {detail?.test_keywords || project.test_item || "Not recorded"}</p>
  {detail && <p>Declared project state: {detail.material_state === "ongoing" ? "On-going" : "Completed"}</p>}
  <p className="materials-path">Managed location: {path}</p>
  {!available && <p role="status">The material folder is unavailable. Refresh the library.</p>}
  <div className="materials-actions">
   <button disabled={busy || !available} onClick={() => void act(async () => { await openReferenceFile(project.key); })}>Open folder</button>
   <button disabled={busy || !available} onClick={() => onBrowse(project.key)}>Browse files</button>
   {project.source !== "linked" && <button disabled={busy || !available} onClick={() => onSupplement?.(project)}>Supplement materials</button>}
   {id && <button disabled={busy || !detail} onClick={edit}>Edit materials information</button>}
   {project.project_id && <button disabled={busy} onClick={() => onProject(project.project_id!)}>Project workspace</button>}
  </div>
  {editing && detail && <form className="materials-review" onSubmit={event => {
   event.preventDefault(); void act(async () => {
    await editReceiptMetadata(id!, { revision: detail.revision, product_name: product, test_keywords: tests, material_state: state });
    setDetail(await getReceiptDetail(id!)); onChanged(); setEditing(false);
   });
  }}>
   <label>Product name<input disabled={busy} value={product} onChange={event => setProduct(event.target.value)} /></label>
   <label>Test items<input disabled={busy} value={tests} onChange={event => setTests(event.target.value)} /></label>
   <label>Declared project state<select disabled={busy} value={state} onChange={event => setState(event.target.value)}><option value="completed">Completed</option><option value="ongoing">On-going</option></select></label>
   <div className="materials-actions"><button disabled={busy} type="submit">Save information</button><button disabled={busy} type="button" onClick={() => setEditing(false)}>Cancel edit</button></div>
  </form>}
 </section></div>, document.body);
}
