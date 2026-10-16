import { useEffect, useRef, useState } from "react";
import { scanExistingProjects, previewExistingProject, registerExistingProject, listExistingLocations,
  type ExistingSource, type ExistingPreview, type ExistingLocation, type ExistingDecision } from "../../api/existingProjects";
import { ExistingProjectFilesPanel } from "./ExistingProjectFilesPanel";
import { ProjectManagementDialog } from "./ProjectRegistryManagementDialog";

export function ExistingProjectsPanel({onOpenProject,onChanged}: {onOpenProject:(id:string)=>void;onChanged:()=>void}) {
  const [open,setOpen]=useState(false);
  const [roots,setRoots]=useState(""); const [depth,setDepth]=useState(1);
  const [candidates,setCandidates]=useState<ExistingSource[]>([]); const [diagnostics,setDiagnostics]=useState<string[]>([]);
  const [locations,setLocations]=useState<ExistingLocation[]>([]); const [search,setSearch]=useState("");
  const [review,setReview]=useState<ExistingPreview|null>(null);
  const [action,setAction]=useState<ExistingDecision["action"]|"">("");const [number,setNumber]=useState("");
  const [target,setTarget]=useState("");const [ignore,setIgnore]=useState(false);
  const [busy,setBusy]=useState(false); const [error,setError]=useState<string|null>(null); const [stale,setStale]=useState(false);
  const [message,setMessage]=useState("");const [files,setFiles]=useState<ExistingLocation|null>(null);
  const busyRef=useRef(false);const epoch=useRef(0);const locationsEpoch=useRef(0); const mounted=useRef(true);
  useEffect(()=>{mounted.current=true;return()=>{mounted.current=false;epoch.current+=1;};},[]);
  useEffect(()=>{if(!open)return;let live=true;const request=++locationsEpoch.current;void listExistingLocations().then(x=>{if(live&&request===locationsEpoch.current)setLocations(x);}).catch(()=>{if(live&&request===locationsEpoch.current)setError("Could not load registered folders. Reopen this panel to retry.");});return()=>{live=false;};},[open]);

  async function run(task:()=>Promise<void>) {
    if(busyRef.current)return;busyRef.current=true;setBusy(true);setError(null);
    try {await task();}catch(e){if(mounted.current)setError((e as Error).message || "Operation failed. Review and retry.");}
    finally {busyRef.current=false;if(mounted.current)setBusy(false);}
  }
  async function scan() {await run(async()=>{const result=await scanExistingProjects(roots.split(/\r?\n/).map(x=>x.trim()).filter(Boolean),depth);
    if(!mounted.current)return;setCandidates(result.candidates);setDiagnostics(result.diagnostics);setReview(null);setMessage("Scan is read-only. Review each candidate before associating it.");});}
  async function loadReview(path:string,preserve=false) {
    if(preserve)setStale(true);
    await run(async()=>{const request=++epoch.current;const next=await previewExistingProject(path);
      if(!mounted.current||request!==epoch.current)return;setReview(next);setStale(false);
      if(!preserve){setNumber(next.suggested_number);setAction(next.conflicts.length||next.manifest_error?"":"register");setTarget("");setIgnore(false);}
    });
  }
  async function confirm() {
    if(!review||!action||stale)return;
    await run(async()=>{try {const saved=await registerExistingProject({path:review.path,token:review.token,action,management_number:number,
      target_project_id:target||null,ignore_manifest:ignore});if(!mounted.current)return;
      locationsEpoch.current+=1;setLocations(current=>[...current.filter(x=>x.location_id!==saved.location_id),saved]);setReview(null);setMessage(`${saved.management_number} is now managed. Original files are unchanged.`);onChanged();
    }catch(e){if(mounted.current)setStale(true);throw e;}});
  }
  const visible=locations.filter(x=>[x.management_number,x.source_number,x.product_name,x.path].some(v=>v?.toLocaleLowerCase().includes(search.toLocaleLowerCase())));
  return <section className="existing-projects-panel" aria-label="Existing projects and folders">
    <button type="button" className="ui-secondary-action" disabled={busy} aria-expanded={open} onClick={()=>{setOpen(x=>!x);setError(null);}}>Manage existing folders</button>
    {open&&<>
      <h2>Existing projects and folders</h2><p>Associate folders in place. No files are moved or rewritten, and no LTR or confirmed Matrix is created. Full database merging is not included.</p>
      <label>Scan roots<textarea aria-label="Scan roots" value={roots} disabled={busy} onChange={e=>setRoots(e.target.value)} placeholder="One absolute folder path per line" rows={3}/></label>
      <label>Scan depth<select aria-label="Scan depth" value={depth} disabled={busy} onChange={e=>setDepth(Number(e.target.value))}>
        <option value={0}>Selected folders only</option><option value={1}>One level</option><option value={2}>Two levels</option><option value={3}>Three levels</option></select></label>
      <button type="button" disabled={busy||!roots.trim()} onClick={()=>void scan()}>Scan folders</button>
      {busy&&<p role="status">Reading or saving reviewed associations…</p>}
      {error&&!review&&<p role="alert">{error}</p>}{message&&<p role="status">{message}</p>}
      {!!diagnostics.length&&<ul>{diagnostics.map((x,i)=><li key={i}>{x}</li>)}</ul>}
      {!!candidates.length&&<div className="existing-project-table"><table><thead><tr><th>Candidate folder</th><th>Identity evidence</th><th>Action</th></tr></thead><tbody>{candidates.map(item=><tr key={item.path}>
        <td>{item.name}<small>{item.path}</small></td><td>{item.source_project_id?"ConnLab manifest (files only)":"Manual / unverified folder"}<small>{item.source_number||"No source number"}{item.source_number_origin==="folder_hint"?" — folder name suggestion, unconfirmed":""}</small>{item.manifest_error&&<small>{item.manifest_error}</small>}</td>
        <td><button type="button" disabled={busy} aria-label={`Review ${item.name}`} onClick={()=>void loadReview(item.path)}>Review</button><button type="button" disabled={busy} onClick={()=>setCandidates(xs=>xs.filter(x=>x.path!==item.path))}>Skip</button></td></tr>)}</tbody></table></div>}
      {review&&<ProjectManagementDialog title="Review existing folder" busy={busy} onCancel={()=>{epoch.current+=1;setReview(null);setError(null);}}>
        <p>{review.path}</p><p>{review.notice}</p><p>Source number: {review.source_number||"Not recorded"}{review.source_number_origin==="folder_hint"?" (folder name suggestion only)":""}</p>
        {review.source_project_id&&<p>Source project ID: {review.source_project_id}. An ID match alone does not prove these are the same project.</p>}
        {!!review.conflicts.length&&<><h3>Local matching records</h3><ul>{review.conflicts.map(x=><li key={x.project_id}>{x.display_project_id} · Management number: {x.number||"Not recorded"} · {x.name} · {x.state} · {x.project_id}</li>)}</ul><p>Matching numbers never authorize replacement. Retained records must be restored before linking.</p></>}
        {review.existing?<><p>This directory is already managed as {review.existing.management_number} ({review.existing.registry_state}).</p><button type="button" onClick={()=>onOpenProject(review.existing!.project_id)}>Open managed project</button></>:<>
          <label>Decision<select aria-label="Intake decision" disabled={busy} value={action} onChange={e=>setAction(e.target.value as typeof action)}><option value="">Choose a decision</option>
            <option value="register">Register; preserve supported unused source ID</option><option value="independent">Import as an independent project with a new ID</option><option value="link">Associate with the same local project after review</option></select></label>
          {action==="link"?<label>Local project<select aria-label="Local project to associate" value={target} disabled={busy} onChange={e=>setTarget(e.target.value)}><option value="">Choose a local project</option>{review.targets.map(x=><option key={x.project_id} value={x.project_id} disabled={x.state!=="active"}>{x.display_project_id} · Management: {x.number||"Not recorded"} · {x.name} · {x.state} · {x.project_id}</option>)}</select></label>
            :<label>Local management number<input aria-label="Local management number" value={number} maxLength={128} disabled={busy} onChange={e=>setNumber(e.target.value)}/></label>}
          <p>The local management number identifies this intake entry; it does not register an LTR workbook number.</p>
          {review.manifest_error&&<><p>{review.manifest_error}</p><label><input type="checkbox" disabled={busy||action!=="independent"} checked={ignore} onChange={e=>setIgnore(e.target.checked)}/>I reviewed the unsupported identity and will create an independent files-only project.</label></>}
          {stale&&<p>Refresh the review before retrying. Your choices are retained.</p>}
          <button type="button" disabled={busy} onClick={()=>void loadReview(review.path,true)}>Refresh review</button>
          <button type="button" disabled={busy||stale||!action||(action==="link"?!target:!number.trim())||Boolean(review.manifest_error&&(action!=="independent"||!ignore))} onClick={()=>void confirm()}>Confirm association</button>
        </>}
        <button type="button" disabled={busy} onClick={()=>{epoch.current+=1;setReview(null);setError(null);}}>Cancel review</button>
        {error&&<p role="alert">{error}</p>}
      </ProjectManagementDialog>}
      <h3>Registered folders</h3><label>Search managed folders<input aria-label="Search managed folders" value={search} onChange={e=>setSearch(e.target.value)} placeholder="Management number, source DL, folder or sample"/></label>
      <p>Missing confirmation data does not prevent browsing these files.</p>
      {!visible.length?<p>No registered folders match.</p>:<ul className="existing-location-list">{visible.map(item=><li key={item.location_id}><strong>{item.management_number}</strong> · {item.product_name} · {item.registry_state}<small>Source DL: {item.source_number||"Not recorded"} · {item.path}</small>
        <button type="button" onClick={()=>onOpenProject(item.project_id)}>Open project</button><button type="button" onClick={()=>setFiles(item)}>Browse files / review location</button></li>)}</ul>}
      {files&&<ExistingProjectFilesPanel location={files} onClose={()=>setFiles(null)} onChanged={updated=>{locationsEpoch.current+=1;setFiles(updated);setLocations(xs=>xs.map(x=>x.location_id===updated.location_id?updated:x));}}/>}
    </>}
  </section>;
}
