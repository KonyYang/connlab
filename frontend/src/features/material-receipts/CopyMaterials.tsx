import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { openReferenceFile, type BrowseFile, type ReferenceProject } from "../../api/referenceLibrary";
import { previewMaterialCopy, confirmMaterialCopy, getReceiptBatch, retryReceipt, copyContextProof, type WorkbenchCopyContext, type ReceiptBatch, type ReceiptPlan } from "../../api/materialReceipts";
import { ApiRequestError } from "../../api/client";
import { ReceiptResults } from "./ReceiveMaterials";
import "./materials.css";

export function CopyMaterials({ source, file, context, onClose, onCopied, onTargetHistory }: {
 source:ReferenceProject; file:BrowseFile; context?:WorkbenchCopyContext|null; onClose:()=>void;
 onCopied:()=>void; onTargetHistory?:(project:ReferenceProject)=>void;
}) {
 const [directory,setDirectory]=useState("Reference materials");
 const [plan,setPlan]=useState<ReceiptPlan|null>(null);
 const [batch,setBatch]=useState<ReceiptBatch|null>(null);
 const [attempted,setAttempted]=useState(false);
 const [noBatch,setNoBatch]=useState(false);
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState("");
 const identity = `${context?.session_id}:${context?.token}:${source.key}:${file.relative_path}`;
 const live = useRef(identity); live.current=identity;
 const generation=useRef(0);
 const [reviewIdentity,setReviewIdentity]=useState(identity);
 useEffect(()=>{
  generation.current++;setPlan(null);setBatch(null);setAttempted(false);setNoBatch(false);setError("");setBusy(false);setReviewIdentity(identity);
 },[identity]);
 useEffect(()=>()=>{generation.current++;live.current="";},[]);
 async function act(action:(current:()=>boolean)=>Promise<void>){
  const run=++generation.current;const bound=identity;
  const current=()=>generation.current===run && live.current===bound;
  setBusy(true);setError("");
  try{await action(current);}catch(cause){if(current())setError((cause as Error).message);}finally{if(current())setBusy(false);}
 }
 const selected=context?.target;
 const valid=Boolean(context && reviewIdentity===identity);
 const proof=context ? copyContextProof(context) : null;
 async function confirm(current:()=>boolean){
  if(!plan || !proof)return;
  setAttempted(true);setNoBatch(false);
  const result=await confirmMaterialCopy(plan,proof);
  if(current()){setBatch(result);onCopied();}
 }
 return createPortal(<div className="materials-overlay"><section className="materials-dialog" role="dialog" aria-modal="true" aria-labelledby="copy-materials-title">
  <header><h2 id="copy-materials-title">Copy to current project</h2><button disabled={busy} onClick={onClose}>Close copy</button></header>
  {error && <p role="alert">{error}</p>}
  <p>Source: {source.number || source.title} · {file.relative_path}</p>
  {!context && <p>Open the target Project Workbench, then return to Library to copy files.</p>}
  {context && selected && <><p><strong>Current Workbench: {selected.number || "No number"} · {selected.title}</strong></p><p className="materials-path">Project location: {selected.folder_path}</p>
   {valid && !batch && <><label>Target directory within project<input disabled={busy || attempted} value={directory} onChange={event=>{setDirectory(event.target.value);setPlan(null);}}/></label>
    <p className="materials-help">A separate file copy will be created. Existing project execution data remains unchanged.</p>
    <button disabled={busy || attempted} onClick={()=>void act(async current=>{const result=await previewMaterialCopy({source_key:source.key,relative_path:file.relative_path,context:proof!,target_relative_directory:directory});if(current())setPlan(result);})}>Check destination</button>
    {plan && <section className="materials-review"><p className="materials-path">Target: {plan.target_path}</p>{plan.items?.map(row=><div key={row.relative_path}><strong>{row.action==="skip"?"Skip identical":row.action==="supplement"?"Save supplementary copy":"New copy"}</strong><p className="materials-path">{row.target_relative}</p>{row.reason && <p>{row.reason}</p>}</div>)}{!attempted && <button disabled={busy} onClick={()=>void act(confirm)}>Confirm copy</button>}</section>}
   </>}
   {valid && attempted && !batch && plan && <section className="materials-review"><p>The copy result is not confirmed. Check this operation or the target receipt history before starting another.</p><div className="materials-actions"><button disabled={busy} onClick={()=>void act(confirm)}>Retry confirmed copy</button><button disabled={busy || !plan.batch_id} onClick={()=>void act(async current=>{setNoBatch(false);try{const result=await getReceiptBatch(plan.batch_id!);if(current())setBatch(result);}catch(cause){if(current() && cause instanceof ApiRequestError && cause.status===404)setNoBatch(true);else throw cause;}})}>Check copy result</button><button disabled={busy} onClick={()=>onTargetHistory?.(selected)}>View target receipt history</button>{noBatch && <button disabled={busy} onClick={()=>{setAttempted(false);setPlan(null);setNoBatch(false);}}>Review copy again</button>}</div></section>}
   {valid && batch && <><ReceiptResults batch={batch}/><div className="materials-actions">{batch.status!=="completed" && <button disabled={busy} onClick={()=>void act(async current=>{const result=await retryReceipt(batch.batch_id,proof!);if(current()){setBatch(result);onCopied();}})}>Retry copy</button>}<button disabled={busy} onClick={()=>void act(async()=>{await openReferenceFile(selected.key);})}>Open target folder</button><button disabled={busy} onClick={()=>onTargetHistory?.(selected)}>View target receipt history</button></div></>}
  </>}
 </section></div>,document.body);
}
