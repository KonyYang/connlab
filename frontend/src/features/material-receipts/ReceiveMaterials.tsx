import {runtimeSessionStorage} from "../../runtimeEnvironment";
import {useEffect,useRef,useState} from "react";
import {createPortal} from "react-dom";
import * as api from "../../api/materialReceipts";
import type {ReceiptBatch,ArchivePlan} from "../../api/materialReceipts";
import "./materials.css";
const labels:Record<string,string>={copied:"Copied",skipped:"Skipped",supplemented:"Saved supplementary copy",failed:"Failed",retained_changed:"Changed after receipt — retained"};
const pendingKey="materials-archive-pending";
const readPending=():ArchivePlan|null=>{try{return JSON.parse(runtimeSessionStorage.getItem(pendingKey)??"null");}catch{return null;}};
export function ReceiptResults({ batch }: { batch: ReceiptBatch }) {
 return <section aria-label="Receipt result">
  <p role="status">{batch.status === "completed" ? "Materials received and verified." : "Receipt incomplete. Review the items below; existing files are retained."}</p>
  {batch.message && <p role="alert">{batch.message}</p>}
  <p>New {batch.counts.copied ?? 0} · Skipped {batch.counts.skipped ?? 0} · Supplementary {batch.counts.supplemented ?? 0} · Failed {batch.counts.failed ?? 0} · Changed after receipt {batch.counts.retained_changed ?? 0}</p>
  {Object.values(batch.directory_counts ?? {}).some(Boolean) && <p>Directories: {Object.entries(batch.directory_counts).map(([key, count]) => labels[key] + " " + count).join(" · ")}</p>}
  <p className="materials-path">Managed location: {batch.target_path}</p>
  <details><summary>Receipt details</summary><ul className="materials-items">{batch.items.map(row => <li key={row.relative_path}><strong>{row.relative_path}{row.directory ? " (folder)" : ""}</strong><span>{labels[row.status ?? ""] ?? row.status}</span><span>{row.target_relative}</span>{row.message && <span>{row.message}</span>}</li>)}</ul></details>
 </section>;
}
export function ReceiveMaterials({onClose,onReceived,initialOperation}:{onClose:()=>void;onReceived:(key:string)=>void;initialOperation?:string}) {
 const [plan,setPlan]=useState<ArchivePlan|null>(readPending);
 const [operation,setOperation]=useState<ReceiptBatch|null>(null);
 const [attempted,setAttempted]=useState(()=>Boolean(readPending()));
 const [busy,setBusy]=useState(false),[cancelling,setCancelling]=useState(false),[error,setError]=useState("");
 const live=useRef(false),started=useRef(false),job=useRef<string|null>(null);
 const finish=(value:ReceiptBatch)=>{setOperation(value);if(value.status==="completed"){runtimeSessionStorage.removeItem(pendingKey);onReceived(value.target_key);}};
 async function run(start:Promise<{job_id:string}>,kind:"preview"|"copy") {
  setBusy(true);setError("");setCancelling(false);
  try {
   const {job_id}=await start;job.current=job_id;
   if(!live.current){await api.cancelArchiveJob(job_id);return;}
   for(;;){
    const result=await api.getArchiveJob(job_id);
    if(!live.current)return;
    if(result.status==="working" || result.status==="cancellation_requested"){
     setCancelling(result.status==="cancellation_requested");await new Promise(resolve=>setTimeout(resolve,200));continue;
    }
    if(result.status==="failed")throw new Error(result.error||"Materials processing failed. Retry the original operation.");
    if(result.result){
     if(kind==="copy")finish(result.result as ReceiptBatch);
     else {
      const next=result.result as ArchivePlan;
      if(next.status==="existing")onReceived(next.target_key!);
      else if(next.status==="pending"){setOperation(next.operation!);setAttempted(true);}
      else setPlan(next);
     }
    } else if(result.status==="cancelled")onClose();
    break;
   }
  }catch(cause){if(live.current)setError((cause as Error).message);}
  finally{job.current=null;if(live.current){setBusy(false);setCancelling(false);}}
 }
 useEffect(()=>{
  live.current=true;
  if(!started.current){started.current=true;
   const saved=readPending();
   if(initialOperation || saved?.batch_id){
    void api.getArchiveOperation(initialOperation||saved!.batch_id!).then(value=>{if(live.current)finish(value);}).catch(cause=>{if(live.current)setError((cause as Error).message);});
   }else void api.pickReceiptFolder().then(source=>{if(!live.current)return;if(!source)onClose();else void run(api.startArchivePreview(source),"preview");}).catch(cause=>{if(live.current)setError((cause as Error).message);});
  }
  return()=>{live.current=false;if(job.current)void Promise.resolve(api.cancelArchiveJob(job.current)).catch(()=>undefined);};
 },[]);
 async function cancel(){
  if(job.current){setCancelling(true);try{await api.cancelArchiveJob(job.current);}catch(cause){setError((cause as Error).message);}return;}
  onClose();
 }
 function leave(){
  live.current=false;
  const current=job.current;job.current=null;
  if(current)void Promise.resolve(api.cancelArchiveJob(current)).catch(()=>undefined);
  // Closing never claims that OS work stopped; the original receipt remains recoverable.
  onClose();
 }
 function confirm(){if(!plan)return;runtimeSessionStorage.setItem(pendingKey,JSON.stringify(plan));setAttempted(true);void run(api.confirmArchive(plan),"copy");}
 function retry(){if(operation)void run(api.retryArchive(operation.batch_id),"copy");else if(plan)void run(api.confirmArchive(plan),"copy");}
 if(!error && !operation && !attempted && (!plan || busy)){
  if(!busy)return null;
  return <div className="materials-preparing" role="status"><span>Preparing materials…</span><button type="button" onClick={leave}>Cancel</button></div>;
 }
 return createPortal(<div className="materials-overlay"><section className="materials-dialog materials-receive-dialog" role="dialog" aria-modal="true" aria-label="Receive project materials">
  <header><h2>Receive project materials</h2></header>
  {error && <p role="alert">{error} <a href="/settings">Settings</a></p>}
  {busy && <p role="status">{cancelling?"Cancelling…":"Processing materials…"}</p>}
  {plan && !operation && <><p className="materials-path">Source: {plan.source_path}</p><p className="materials-path">Target: {plan.target_path}</p></>}
  {plan?.status==="conflict" && !busy && <><p>A folder with this name already exists. Existing files will not be changed.</p><div className="materials-actions"><button onClick={onClose}>Skip</button><button className="materials-primary" onClick={()=>void run(api.startArchivePreview(plan.source_path,true),"preview")}>Keep independent copy</button></div></>}
  {operation && operation.status!=="completed" && <><p role="alert">Receipt incomplete. {operation.message}</p><p>Received {operation.counts.copied??0} · Failed {operation.counts.failed??0}</p>{operation.items.some(item=>item.status==="failed"||item.status==="retained_changed") && <details><summary>Failed items</summary><ul className="materials-items">{operation.items.filter(item=>item.status==="failed"||item.status==="retained_changed").map(item=><li key={item.relative_path}>{item.relative_path}: {item.message}</li>)}</ul></details>}{!busy && <button className="materials-primary" onClick={retry}>Continue receipt</button>}</>}
  {attempted && !operation && !busy && <><p>The receipt result is not confirmed. Continue or check the original operation before receiving another copy.</p><button className="materials-primary" onClick={retry}>Continue receipt</button>{plan?.batch_id && <button onClick={()=>void api.getArchiveOperation(plan.batch_id!).then(finish).catch(cause=>setError((cause as Error).message))}>Check receipt result</button>}</>}
  <div className="materials-actions">{busy && <button onClick={leave}>Back to library</button>}{plan?.status==="ready" && !attempted && !busy && <button className="materials-primary" onClick={confirm}>Receive</button>}{!(plan?.status==="conflict"&&!busy) && <button disabled={cancelling} onClick={()=>void cancel()}>{busy?"Cancel processing":operation?"Close":"Cancel"}</button>}</div>
 </section></div>,document.body);
}
