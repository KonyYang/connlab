import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { openReferenceFile, searchReferenceLibrary, type BrowseFile, type ReferenceProject } from "../../api/referenceLibrary";
import { previewMaterialCopy, confirmMaterialCopy, retryReceipt, type ReceiptBatch, type ReceiptPlan } from "../../api/materialReceipts";
import { ReceiptResults } from "./ReceiveMaterials";
import "./materials.css";
export function CopyMaterials({ source, file, currentProjectId, onClose, onCopied }: { source:ReferenceProject; file:BrowseFile; currentProjectId?:string|null; onClose:()=>void; onCopied:()=>void }) {
 const [targets,setTargets]=useState<ReferenceProject[]>([]);
 const [target,setTarget]=useState("");
 const [directory,setDirectory]=useState("Reference materials");
 const [plan,setPlan]=useState<ReceiptPlan|null>(null);
 const [batch,setBatch]=useState<ReceiptBatch|null>(null);
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState("");
 useEffect(()=>{let live=true;void searchReferenceLibrary("","all","all","",0).then(result=>{if(!live)return;const rows=result.projects.filter(row=>row.project_id && row.available);setTargets(rows);setTarget(rows.find(row=>row.project_id===currentProjectId)?.key??"");}).catch(cause=>{if(live)setError((cause as Error).message);});return()=>{live=false;};},[currentProjectId]);
 async function act(action:()=>Promise<void>){setBusy(true);setError("");try{await action();}catch(cause){setError((cause as Error).message);}finally{setBusy(false);}}
 const selected=targets.find(row=>row.key===target);
 return createPortal(<div className="materials-overlay"><section className="materials-dialog" role="dialog" aria-modal="true" aria-labelledby="copy-materials-title">
  <header><h2 id="copy-materials-title">Copy to project</h2><button disabled={busy} onClick={onClose}>Close copy</button></header>
  {error && <p role="alert">{error}</p>}
  <p>Source: {source.number || source.title} · {file.relative_path}</p>
  {!batch && <><label>Target project<select disabled={busy} value={target} onChange={event=>{setTarget(event.target.value);setPlan(null);}}><option value="">Choose a project…</option>{targets.map(row=><option key={row.key} value={row.key}>{row.number} · {row.title}</option>)}</select></label>
   {selected && <p className="materials-path">Project location: {selected.folder_path}</p>}
   <label>Target directory within project<input disabled={busy} value={directory} onChange={event=>{setDirectory(event.target.value);setPlan(null);}}/></label>
   <p className="materials-help">A separate copy will be created. Historical materials and project execution data remain unchanged.</p>
   <button disabled={busy || !target} onClick={()=>void act(async()=>{setPlan(await previewMaterialCopy({source_key:source.key,relative_path:file.relative_path,target_key:target,target_relative_directory:directory}));})}>Check destination</button>
   {plan && <section className="materials-review"><p className="materials-path">Target: {plan.target_path}</p>{plan.items?.map(row=><div key={row.relative_path}><strong>{row.action==="skip"?"Skip identical":row.action==="supplement"?"Save supplementary copy":"New copy"}</strong><p className="materials-path">{row.target_relative}</p>{row.reason && <p>{row.reason}</p>}</div>)}<button disabled={busy} onClick={()=>void act(async()=>{setBatch(await confirmMaterialCopy(plan));onCopied();})}>Confirm copy</button></section>}
  </>}
  {batch && <><ReceiptResults batch={batch}/><div className="materials-actions">{batch.status!=="completed" && <button disabled={busy} onClick={()=>void act(async()=>{setBatch(await retryReceipt(batch.batch_id));onCopied();})}>Retry copy</button>}<button disabled={busy} onClick={()=>void act(async()=>{await openReferenceFile(target);})}>Open target folder</button></div></>}
 </section></div>,document.body);
}
