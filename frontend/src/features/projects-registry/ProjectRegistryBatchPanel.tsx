import { useEffect, useRef, useState } from "react";
import { previewRegistryBatch, moveRegistryBatch, type RegistryBatchPreview } from "../../api/projectRegistryManagement";

export type RegistryBatchRow={project_id:string;label:string;temporary?:boolean};
type BatchPanelProps={location:"active"|"trash"|"history";rows:RegistryBatchRow[];onChanged:()=>void};
export function ProjectRegistryBatchPanel(props:BatchPanelProps) {
  return <RegistryBatchSession key={props.location} {...props}/>;
}

function RegistryBatchSession({location,rows,onChanged}:BatchPanelProps) {
  const [open,setOpen]=useState(false);const [selected,setSelected]=useState<string[]>([]);const [onlyTemporary,setOnlyTemporary]=useState(false);
  const [reason,setReason]=useState("");const [destination,setDestination]=useState<"active"|"history">("active");
  const [preview,setPreview]=useState<RegistryBatchPreview|null>(null);const [error,setError]=useState<string|null>(null);
  const [busy,setBusy]=useState(false);const [message,setMessage]=useState("");const guard=useRef(false);const live=useRef(true);
  const [historyAction,setHistoryAction]=useState<"trash"|"restore">("restore");
  useEffect(()=>{live.current=true;return()=>{live.current=false;};},[]);
  useEffect(()=>{setSelected([]);setPreview(null);setMessage("");setError(null);},[location]);
  const action=location==="history"?historyAction:location==="active"?"trash":"restore";
  const visible=rows.filter(x=>!onlyTemporary||x.temporary);
  async function run(task:()=>Promise<void>) {if(guard.current)return;guard.current=true;setBusy(true);setError(null);
    try{await task();}catch(e){if(live.current){setError((e as Error).message);setPreview(null);}}finally{guard.current=false;if(live.current)setBusy(false);}}
  return <section className="project-registry-batch" aria-label="Batch project record management">
    <button type="button" className="ui-secondary-action" aria-expanded={open} disabled={busy} onClick={()=>setOpen(x=>!x)}>Batch record management</button>
    {open&&<><p>Only registry location changes. All source files, confirmed data, outputs, LTR records and folder associations are retained. Folder names do not determine whether a project is disposable.</p>
      {location==="history"&&<label>Action for retained history<select aria-label="Batch history action" value={historyAction} disabled={busy} onChange={e=>{setHistoryAction(e.target.value as typeof historyAction);setPreview(null);}}><option value="restore">Restore records</option><option value="trash">Move records to recycle bin</option></select></label>}
      {location==="active"&&<label><input type="checkbox" checked={onlyTemporary} disabled={busy} onChange={e=>{setOnlyTemporary(e.target.checked);setPreview(null);}}/>Show records without a registered LTR only</label>}
      <p>{selected.length} selected (maximum 100). Review retained records before confirming.</p>
      <div className="registry-batch-selection">{visible.map(row=><label key={row.project_id}><input type="checkbox" disabled={busy||(!selected.includes(row.project_id)&&selected.length>=100)} aria-label={`Select ${row.label}`} checked={selected.includes(row.project_id)}
        onChange={e=>{setSelected(xs=>e.target.checked?[...xs,row.project_id]:xs.filter(x=>x!==row.project_id));setPreview(null);}}/>{row.label} <small>{row.project_id}</small></label>)}</div>
      {action==="trash"?<label>Removal reason<input aria-label="Removal reason" value={reason} maxLength={2000} disabled={busy} onChange={e=>setReason(e.target.value)}/></label>
        :<label>Restore destination<select aria-label="Batch restore destination" disabled={busy} value={destination} onChange={e=>{setDestination(e.target.value as typeof destination);setPreview(null);}}><option value="active">Active; conflicts must be resolved separately</option><option value="history">Retained history; preserve active records</option></select></label>}
      <button type="button" disabled={busy||!selected.length||(action==="trash"&&!reason.trim())} onClick={()=>void run(async()=>{const result=await previewRegistryBatch({project_ids:selected,action,destination});if(live.current)setPreview(result);})}>Preview selected records</button>
      {preview&&<section aria-label="Batch move review" className="registry-batch-review"><h3>{action==="trash"?"Move selected records to recycle bin":"Restore selected records"}</h3>
        {preview.items.map(item=><details key={item.project.project_id}><summary>{item.project.display_project_id} · {item.project.sample_description||item.project.requestor} · {item.project.project_id}</summary><ul>{item.retained_data.map((text,index)=><li key={index}>{text}</li>)}</ul>{item.warnings.map((text,index)=><p key={index}>{text}</p>)}</details>)}
        {preview.blockers.map((text,index)=><p role="alert" key={index}>{text}</p>)}
        <button type="button" disabled={busy||!!preview.blockers.length} onClick={()=>void run(async()=>{await moveRegistryBatch({project_ids:selected,action,destination,token:preview.token,reason});if(!live.current)return;setPreview(null);setSelected([]);setMessage("Selected registry records moved. Original files are unchanged.");onChanged();})}>Confirm batch move</button>
        <button type="button" disabled={busy} onClick={()=>setPreview(null)}>Cancel batch review</button>
      </section>}
      {busy&&<p role="status">Processing selected records…</p>}{error&&<p role="alert">{error} Preview again to continue; your selection is retained.</p>}{message&&<p role="status">{message}</p>}
    </>}
  </section>;
}
