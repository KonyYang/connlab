import { useEffect, useRef, useState } from "react";
import { listExistingFiles, listExistingLocations, previewExistingRelocation, relocateExistingLocation, existingFileDownloadUrl,
  type ExistingFiles, type ExistingLocation, type RelocationPreview } from "../../api/existingProjects";

export function ProjectExistingFiles({projectId}:{projectId:string}) {
  const [locations,setLocations]=useState<ExistingLocation[]>([]);const [selected,setSelected]=useState<ExistingLocation|null>(null);
  const [error,setError]=useState(false);const [retry,setRetry]=useState(0);
  useEffect(()=>{let live=true;setLocations([]);setSelected(null);setError(false);void listExistingLocations(projectId).then(xs=>{if(live)setLocations(xs);}).catch(()=>{if(live)setError(true);});return()=>{live=false;};},[projectId,retry]);
  if(error)return <section className="existing-project-files" aria-label="Linked existing folders"><p role="alert">Could not read existing folder associations. <button type="button" onClick={()=>setRetry(x=>x+1)}>Retry folder associations</button></p></section>;
  if(!locations.length)return null;
  return <section className="existing-project-files" aria-label="Linked existing folders"><h2>Linked existing folders</h2>
    <p>Files are managed in place. Missing Matrix and other confirmed data can be completed separately.</p>
    {locations.map(item=><p key={item.location_id}><strong>{item.management_number}</strong> · Source DL: {item.source_number||"Not recorded"} <button type="button" onClick={()=>setSelected(item)}>Browse files / review location</button></p>)}
    {selected&&<ExistingProjectFilesPanel location={selected} onClose={()=>setSelected(null)} onChanged={updated=>{setSelected(updated);setLocations(xs=>xs.map(x=>x.location_id===updated.location_id?updated:x));}}/>}
  </section>;
}

type ExistingFilesPanelProps={location:ExistingLocation;locationCurrent?:boolean;onClose:()=>void;onChanged:(location:ExistingLocation)=>void};
export function ExistingProjectFilesPanel(props:ExistingFilesPanelProps) {
  return <ExistingProjectFilesSession key={props.location.location_id} {...props}/>;
}

function ExistingProjectFilesSession({location,locationCurrent=true,onClose,onChanged}:ExistingFilesPanelProps) {
  const [relative,setRelative]=useState("");const [files,setFiles]=useState<ExistingFiles|null>(null);const [error,setError]=useState<string|null>(null);
  const [retry,setRetry]=useState(0);const [newPath,setNewPath]=useState("");const [preview,setPreview]=useState<RelocationPreview|null>(null);
  const [busy,setBusy]=useState(false);const [moveError,setMoveError]=useState<string|null>(null);const busyRef=useRef(false);const live=useRef(true);
  const previewEpoch=useRef(0);
  useEffect(()=>{live.current=true;return()=>{live.current=false;};},[]);
  useEffect(()=>{previewEpoch.current+=1;setPreview(null);},[locationCurrent,location.registry_state,location.revision]);
  useEffect(()=>{let current=true;setFiles(null);setError(null);void listExistingFiles(location.location_id,relative).then(x=>{if(current)setFiles(x);}).catch(e=>{if(current)setError((e as Error).message);});return()=>{current=false;};},[location.location_id,location.revision,relative,retry]);
  async function run(task:()=>Promise<void>) {if(busyRef.current)return;busyRef.current=true;setBusy(true);setMoveError(null);
    try{await task();}catch(e){if(live.current){setMoveError((e as Error).message);setPreview(null);}}finally{busyRef.current=false;if(live.current)setBusy(false);}}
  return <section className="existing-project-files" aria-label={`Files for ${location.management_number}`}><h3>Files for {location.management_number}</h3><p>{location.path}</p>
    <button type="button" disabled={busy} onClick={onClose}>Close files</button>
    <p>Folder: {relative||"Project root"}</p>{relative&&<button type="button" onClick={()=>setRelative(relative.split("/").slice(0,-1).join("/"))}>Parent folder</button>}
    {error?<div role="alert">{error} <button type="button" onClick={()=>setRetry(x=>x+1)}>Retry files</button></div>:!files?<p role="status">Loading files…</p>:<>
      {!files.entries.length&&<p>No visible files in this folder.</p>}<ul>{files.entries.map(item=><li key={item.relative_path}>{item.is_directory?<button type="button" onClick={()=>setRelative(item.relative_path)}>{item.name}/</button>:<a href={existingFileDownloadUrl(location.location_id,item.relative_path)} download>{item.name}</a>}</li>)}</ul>
      {files.diagnostics.map((x,i)=><p key={i}>{x}</p>)}
    </>}
    {!locationCurrent&&<p>Folder status is not current. File browsing remains available; refresh the registered folder status before relocating.</p>}
    {location.registry_state==="active"?<details><summary>Moved or replaced folder? Review its location</summary>
      <label>New folder location<input aria-label="New folder location" value={newPath} disabled={busy||!locationCurrent} onChange={e=>{setNewPath(e.target.value);setPreview(null);}}/></label>
      <button type="button" disabled={busy||!locationCurrent||!newPath.trim()} onClick={()=>void run(async()=>{const request=++previewEpoch.current;const result=await previewExistingRelocation(location.location_id,newPath);if(live.current&&request===previewEpoch.current)setPreview(result);})}>Review relocation</button>
      {preview&&<div className="existing-relocation-review"><p>Only this local folder association changes. Original files, project identity and confirmed data remain intact.</p><p>From {preview.location.path} to {preview.source.path}</p>
        {preview.blockers.map((x,i)=><p role="alert" key={i}>{x}</p>)}
        <button type="button" disabled={busy||!locationCurrent||preview.blockers.length>0} onClick={()=>void run(async()=>{const updated=await relocateExistingLocation(location.location_id,newPath,preview.token);if(!live.current)return;setPreview(null);setRelative("");onChanged(updated);})}>Confirm relocation</button>
        <button type="button" disabled={busy} onClick={()=>setPreview(null)}>Cancel relocation</button></div>}
      {moveError&&<p role="alert">{moveError} Review again to retry; your folder choice is retained.</p>}
    </details>:<p>This is a retained project. Restore it before changing its folder association.</p>}
  </section>;
}
