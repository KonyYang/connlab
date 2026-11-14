import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import type { ReferenceProject } from "../../api/referenceLibrary";
import { openReferenceFile } from "../../api/referenceLibrary";
import * as api from "../../api/materialReceipts";
import type { ReceiptBatch, ReceiptDetail, ReceiptHistory, ReceiptLocationPlan, WorkbenchCopyContext } from "../../api/materialReceipts";
import { changeLegacyProjectLocation, getLegacyProject, type LegacyProjectRecord } from "../../api/legacyProjects";
import { ReceiptResults } from "./ReceiveMaterials";
import "./materials.css";

export function MaterialDetails({ copyContext, project, onClose, onBrowse, onProject, onChanged, onSupplement }: { copyContext?: WorkbenchCopyContext | null; project: ReferenceProject; onClose: () => void; onBrowse: (key: string) => void; onProject: (id: string) => void; onChanged: () => void; onSupplement?: (project: ReferenceProject) => void }) {
 const [catalogHistory, setCatalogHistory] = useState<ReceiptHistory[]>([]);
 const [historyBatch, setHistoryBatch] = useState<ReceiptBatch | null>(null);
 const [detail, setDetail] = useState<ReceiptDetail | null>(null);
 const [reconnected, setReconnected] = useState(false);
 const [legacy, setLegacy] = useState<LegacyProjectRecord | null>(null);
 const [editing, setEditing] = useState(false);
 const [product, setProduct] = useState("");
 const [tests, setTests] = useState("");
 const [state, setState] = useState("completed");
 const [location, setLocation] = useState("");
 const [locating, setLocating] = useState(false);
 const [locationPlan, setLocationPlan] = useState<ReceiptLocationPlan | null>(null);
 const [legacyPlan, setLegacyPlan] = useState(false);
 const [busy, setBusy] = useState(false);
 const [error, setError] = useState("");
 const shownBatch=historyBatch ?? detail?.batch;
 const copyRetryAllowed=shownBatch?.operation !== "copy_file" || Boolean(copyContext && shownBatch.copy_context?.session_id===copyContext.session_id && shownBatch.copy_context.intent===copyContext.intent && shownBatch.target_key===copyContext.target.key);
 const id = project.receipt_id ?? (project.key.startsWith("receipt:") ? project.key.slice(8) : null);
 const [memberPath, setMemberPath] = useState<string | null>(null);
 const memberOnly = project.key.startsWith("member:") && !project.project_id;
 const linkedId = project.key.startsWith("linked:") ? project.key.slice(7) : null;
 useEffect(() => { let live = true;
  if (id) void api.getReceiptDetail(id).then(value => { if (live) setDetail(value); }).catch(cause => { if (live) setError((cause as Error).message); });
  if (!id && !linkedId) void api.getCatalogReceiptHistory(project.key).then(value => { if (live) setCatalogHistory(value.items); }).catch(cause => { if (live) setError((cause as Error).message); });
  if (linkedId) void getLegacyProject(linkedId, new AbortController().signal).then(value => { if (live) setLegacy(value); }).catch(cause => { if (live) setError((cause as Error).message); });
  return () => { live = false; };
 }, [id, linkedId]);
 async function act(action: () => Promise<void>) { setBusy(true); setError(""); try { await action(); } catch (cause) { setError((cause as Error).message); } finally { setBusy(false); } }
 const path = detail?.folder_path ?? legacy?.folder_path ?? memberPath ?? project.folder_path;
 const available = detail?.available ?? (reconnected ? true : project.available);
 function edit() { if (!detail) return; setProduct(detail.product_name); setTests(detail.test_keywords); setState(detail.material_state); setEditing(true); }
 async function reloadDetail() { if (id) setDetail(await api.getReceiptDetail(id)); else if (!linkedId) setCatalogHistory((await api.getCatalogReceiptHistory(project.key)).items); onChanged(); }
 return createPortal(<div className="materials-overlay"><section className="materials-dialog" role="dialog" aria-modal="true" aria-labelledby="materials-detail-title">
  <header><h2 id="materials-detail-title">{project.number || "Project materials"}</h2><button disabled={busy} onClick={onClose}>Close details</button></header>
  {error && <p role="alert">{error}</p>}
  <strong>{detail?.product_name ?? project.title}</strong>
  {(detail?.description || project.description) && <p>{detail?.description ?? project.description}</p>}
  <p>Test items: {detail?.test_keywords || project.test_item || "Not recorded"}</p>
  {detail && <p>Declared project state: {detail.material_state === "ongoing" ? "On-going" : "Completed"}</p>}
  <p className="materials-path">Managed location: {path}</p>
  {!available && <p role="status">{path ? "Material location unavailable. The entry is retained; locate its managed folder." : "No materials linked yet. Link a project directory in the project workspace."}</p>}
  <div className="materials-actions"><button disabled={busy || !available} onClick={() => void act(async () => { await openReferenceFile(project.key); })}>Open folder</button><button disabled={busy} onClick={() => onBrowse(project.key)}>Browse files</button>
   {project.source !== "linked" && <button disabled={busy || !available} onClick={() => onSupplement?.(project)}>Supplement materials</button>}
   {id && <button disabled={busy || !detail} onClick={edit}>Edit materials information</button>}
   {(id || linkedId || memberOnly) && <button disabled={busy} onClick={() => { setLocation(path); setLocationPlan(null); setLegacyPlan(false); setLocating(true); }}>Locate folder</button>}
   {project.project_id && <button disabled={busy} onClick={() => onProject(project.project_id!)}>Project workspace</button>}
  </div>
  {!id && <p className="materials-help">{project.project_id ? "Project information is maintained in the project workspace. This page does not change execution data." : "Existing registration is retained. Receive a managed copy to add editable product and test information."}</p>}
  {editing && detail && <form className="materials-review" onSubmit={event => { event.preventDefault(); void act(async () => { await api.editReceiptMetadata(id!, { revision: detail.revision, product_name: product, test_keywords: tests, material_state: state }); await reloadDetail(); setEditing(false); }); }}>
   <label>Product name<input disabled={busy} value={product} onChange={event => setProduct(event.target.value)} /></label><label>Test items<input disabled={busy} value={tests} onChange={event => setTests(event.target.value)} /></label>
   <label>Declared project state<select disabled={busy} value={state} onChange={event => setState(event.target.value)}><option value="completed">Completed</option><option value="ongoing">On-going</option></select></label>
   <p className="materials-help">Only search information changes. Files, filenames and directories are retained.</p>
   <div className="materials-actions"><button disabled={busy} type="submit">Save information</button><button disabled={busy} type="button" onClick={() => setEditing(false)}>Cancel edit</button></div>
  </form>}
  {locating && <section className="materials-review"><label>Managed folder<input disabled={busy} value={location} onChange={event => { setLocation(event.target.value); setLocationPlan(null); setLegacyPlan(false); }} /></label>
   <div className="materials-actions"><button disabled={busy} onClick={() => void act(async () => { const value = await api.pickReceiptFolder(); if (value) { setLocation(value); setLocationPlan(null); setLegacyPlan(false); } })}>Choose managed folder</button><button disabled={busy || !location || Boolean(linkedId && !legacy)} onClick={() => void act(async () => { if (id) setLocationPlan(await api.previewReceiptLocation(id, location)); else if (memberOnly) setLocationPlan(await api.previewCatalogLocation(project.key, location)); else setLegacyPlan(true); })}>Review location</button><button disabled={busy} onClick={() => setLocating(false)}>Cancel location</button></div>
   {(locationPlan || legacyPlan) && <><p className="materials-path">Current: {path}</p><p className="materials-path">After confirmation: {locationPlan?.folder_path ?? location}</p><p>Only the registered location changes. No files are moved or restored.</p><button disabled={busy} onClick={() => void act(async () => { if (id && locationPlan) { await api.confirmReceiptLocation(id, locationPlan); await reloadDetail(); } else if (memberOnly && locationPlan) { const value = await api.confirmCatalogLocation(project.key, locationPlan); setMemberPath(value.folder_path); setReconnected(true); onChanged(); } else if (linkedId && legacy) { setLegacy(await changeLegacyProjectLocation(linkedId, location, legacy.revision)); setReconnected(true); onChanged(); } setLocating(false); setLocationPlan(null); setLegacyPlan(false); })}>Confirm location</button></>}
  </section>}
  {(detail || !linkedId) && <details><summary>Receipt history and source</summary>
   {detail && <><p className="materials-path">Original source (traceability only): {detail.source_path}</p><p>Received: {detail.created_at}</p></>}
   <button disabled={busy} onClick={() => void act(reloadDetail)}>Refresh receipt history</button>
   <ul className="materials-items">{(detail?.history ?? catalogHistory).map(row => <li key={row.batch_id}><span>{row.created_at} · {row.status}</span><span>{row.source_path}</span><button disabled={busy} onClick={() => void act(async () => { setHistoryBatch(await api.getReceiptBatch(row.batch_id)); })}>View receipt {row.batch_id.slice(0, 8)}</button></li>)}</ul>
   {(historyBatch || detail?.batch) && <><ReceiptResults batch={(historyBatch ?? detail?.batch)!} />{(historyBatch ?? detail?.batch)!.status !== "completed" && <button disabled={busy || !copyRetryAllowed} onClick={() => void act(async () => { const value=(historyBatch ?? detail?.batch)!; const result = value.operation === "copy_file" && copyContext ? await api.retryReceipt(value.batch_id,{session_id:copyContext.session_id,token:copyContext.token}) : await api.retryReceipt(value.batch_id); setHistoryBatch(result); await reloadDetail(); })}>Retry receipt</button>}{shownBatch?.operation === "copy_file" && shownBatch.status !== "completed" && !copyRetryAllowed && <p>Read-only copy history. Return through the target Workbench to review a new copy.</p>}</>}
  </details>}
 </section></div>, document.body);
}
