import {runtimeSessionStorage} from "../runtimeEnvironment";
import {refreshArchive,getArchiveJob,cancelArchiveJob,type WorkbenchCopyContext} from "../api/materialReceipts";
import { useEffect, useMemo, useRef, useState } from "react";
import { openReferenceFile, searchReferenceLibrary, type ReferenceProject, type BrowseFile } from "../api/referenceLibrary";
import { ReceiveMaterials } from "../features/material-receipts/ReceiveMaterials";
import { MaterialDetails } from "../features/material-receipts/MaterialDetails";
import { MaterialFiles } from "../features/material-receipts/MaterialFiles";
import { CopyMaterials } from "../features/material-receipts/CopyMaterials";
import { UiIcon } from "../components/common/UiIcon";
import "./reference-library.css";

const kinds: Record<string,string> = { application: "Application", plan: "Test plan", record: "Test record", report: "Report", photo: "Photo", other: "Other" };
const sources: Record<string,string> = { connlab: "ConnLab project", received: "Received materials", linked: "Linked folder" };
const saved = () => { try { return JSON.parse(runtimeSessionStorage.getItem("reference-search") ?? "{}"); } catch { return {}; } };
const initialEntry = () => new URLSearchParams(window.location.search).get("entry") ?? saved().project ?? "";
const matchesKey = (row: ReferenceProject, key: string) => row.key === key || Boolean(row.member_id && key === "member:" + row.member_id);
export function ReferenceLibraryPage({ onBack, onOpenProject, copyContext }: { onBack?: () => void; onOpenProject: (id:string) => void; copyContext?: WorkbenchCopyContext | null; onOpenMember?: (id:string) => void; onOpenLinked?: (id:string) => void }) {
 const direct = new URLSearchParams(window.location.search).has("entry");
 const [query,setQuery] = useState<string>(() => direct ? "" : saved().query ?? "");
 const [search,setSearch] = useState(query);
 const [source,setSource] = useState<string>(() => direct ? "all" : saved().source ?? "all");
 const [kind,setKind] = useState<string>(() => direct ? "all" : saved().kind ?? "all");
 const [selectedKey,setSelectedKey] = useState<string>(initialEntry);
 const [projects,setProjects] = useState<ReferenceProject[]>([]);
 const [warnings,setWarnings] = useState<string[]>([]);
 const [browseWarnings,setBrowseWarnings] = useState<string[]>([]);
 const [error,setError] = useState("");
 const [busy,setBusy] = useState(false);
 const [reload,setReload] = useState(0);
 const [receiving,setReceiving] = useState(false);
 const [resumeOperation,setResumeOperation] = useState<string|undefined>();
 const [scanning,setScanning]=useState<"idle"|"working"|"cancellation_requested">("idle");
 const [scanWarnings,setScanWarnings]=useState<string[]>([]);
 const scanJob=useRef<string|null>(null),mounted=useRef(false),initialScan=useRef(false);
 const [details,setDetails] = useState<ReferenceProject | null>(null);
 const [copy,setCopy] = useState<{project:ReferenceProject;file:BrowseFile} | null>(null);
 useEffect(() => {
  let live=true; const controller=new AbortController(); setBusy(true); setError(""); setBrowseWarnings([]);
  runtimeSessionStorage.setItem("reference-search",JSON.stringify({query:search,source,kind,project:selectedKey}));
  void searchReferenceLibrary(search,source,kind,"",0,controller.signal).then(async result => {
   let rows=result.projects;
   if (!search && source === "all" && kind === "all" && selectedKey && !rows.some(row=>matchesKey(row,selectedKey))) {
    const extra=await searchReferenceLibrary("","all","all",selectedKey,0,controller.signal);
    rows=[...rows,...extra.projects.filter(row=>!rows.some(old=>old.key===row.key))];
   }
   if (!live) return;
   setProjects(rows); setWarnings(result.warnings);
   setSelectedKey(current=>rows.find(row=>row.key===current)?.key ?? rows.find(row=>matchesKey(row,current))?.key ?? rows.find(row=>row.available)?.key ?? rows[0]?.key ?? "");
  }).catch(cause=>{if(live)setError((cause as Error).message);}).finally(()=>{if(live)setBusy(false);});
  return()=>{live=false;controller.abort();};
 },[search,source,kind,reload]);
 const visibleProjects=projects.filter(row=>row.available || Boolean(row.operation_id && row.intake_status!=="completed") || Boolean(search && !row.folder_path));
 const unavailableProjects=projects.filter(row=>!row.available && row.folder_path && !(row.operation_id && row.intake_status!=="completed"));
 const selected=projects.find(row=>row.key===selectedKey) ?? null;
 useEffect(()=>{runtimeSessionStorage.setItem("reference-search",JSON.stringify({query:search,source,kind,project:selectedKey}));},[selectedKey,search,source,kind]);
 const issues=useMemo(()=>Array.from(new Set([...(error?[error]:[]),...scanWarnings,...warnings,...browseWarnings])),[error,scanWarnings,warnings,browseWarnings]);
 async function refreshIndex(){
  setScanning("working");setScanWarnings([]);
  try{
   const {job_id}=await refreshArchive();scanJob.current=job_id;
   if(!mounted.current){await cancelArchiveJob(job_id);return;}
   for(;;){const job=await getArchiveJob(job_id);if(!mounted.current)return;
    if(job.status==="working"||job.status==="cancellation_requested"){setScanning(job.status);await new Promise(resolve=>setTimeout(resolve,200));continue;}
    if(job.status==="failed")setScanWarnings([job.error||"Materials scan failed. Refresh to retry."]);
    else if(job.result)setScanWarnings((job.result as {warnings:string[]}).warnings??[]);
    setReload(value=>value+1);break;
   }
  }catch(cause){if(mounted.current)setScanWarnings([(cause as Error).message]);}
  finally{scanJob.current=null;if(mounted.current)setScanning("idle");}
 }
 useEffect(()=>{mounted.current=true;if(!initialScan.current){initialScan.current=true;void refreshIndex();}return()=>{mounted.current=false;if(scanJob.current)void Promise.resolve(cancelArchiveJob(scanJob.current)).catch(()=>undefined);};},[]);
 async function cancelScan(){
  if(!scanJob.current)return;
  setScanning("cancellation_requested");
  try{await cancelArchiveJob(scanJob.current);}
  catch(cause){if(mounted.current){setScanWarnings([(cause as Error).message]);setScanning("working");}}
 }
 function closeReceipt(){setReceiving(false);}
 function received(key:string){closeReceipt();setSelectedKey(key);setSearch("");setQuery("");setSource("all");setKind("all");setReload(value=>value+1);}
 async function openFolder(){if(!selected)return;setError("");try{await openReferenceFile(selected.key);}catch(cause){setError((cause as Error).message);}}
 return <section className="reference-library" aria-label="Project materials library">
  <form className="library-search" onSubmit={event=>{event.preventDefault();setSearch(query);setReload(value=>value+1);}}>
   <div className="library-search-entry">
    {onBack && <button className="library-back" type="button" onClick={onBack}><span aria-hidden="true">←</span>Back</button>}
    <div className="library-search-input"><UiIcon name="search"/><input aria-label="Search project materials" placeholder="Project number, product, test item or filename…" value={query} onChange={event=>setQuery(event.target.value)}/></div>
   </div>
   <button className="library-primary" type="submit" disabled={busy}>Search</button><button className="library-primary" type="button" disabled={receiving} onClick={()=>{setResumeOperation(undefined);setReceiving(true);}}><UiIcon name="new-project"/>Receive materials</button>
  </form>
  {receiving && <ReceiveMaterials initialOperation={resumeOperation} onClose={closeReceipt} onReceived={received}/>}
  <div className="library-filters">
   <label><span className="library-sr-only">Source</span><select value={source} onChange={event=>setSource(event.target.value)}><option value="all">All sources</option>{Object.entries(sources).map(([key,label])=><option key={key} value={key}>{label}</option>)}</select></label>
   <label><span className="library-sr-only">Material type</span><select value={kind} onChange={event=>setKind(event.target.value)}><option value="all">All material types</option>{Object.entries(kinds).map(([key,label])=><option key={key} value={key}>{label}</option>)}</select></label>
   {(search || source!=="all" || kind!=="all") && <button onClick={()=>{setQuery("");setSearch("");setSource("all");setKind("all");}}>Clear filters</button>}
   <button className="library-refresh" disabled={scanning==="cancellation_requested"} onClick={()=>{if(scanning==="working")void cancelScan();else void refreshIndex();}}><UiIcon name="refresh"/>{scanning==="cancellation_requested"?"Cancelling scan…":scanning==="working"?"Cancel scan":"Refresh"}</button>
  </div>
  {(issues.length>0 || unavailableProjects.length>0) && <div className="library-issues" role={error?"alert":"status"}>{issues.length>0 && <ul>{issues.map(note=><li key={note}>{note}</li>)}</ul>}{unavailableProjects.length>0 && <details className="library-location-issues"><summary>{unavailableProjects.length} material location{unavailableProjects.length===1?"":"s"} unavailable</summary><p>Entries are retained. View a location for the next step.</p>{unavailableProjects.map(row=><div key={row.key}><span>{row.number || row.title}</span><button aria-label={`View location for ${row.number || row.title}`} onClick={()=>{setSelectedKey(row.key);setError("");}}>View location</button></div>)}</details>}{error && <button onClick={()=>setReload(value=>value+1)}>Retry</button>}</div>}
  <div className="library-workspace">
   <aside className="library-projects" aria-label="Project materials"><header><strong>Project materials</strong><span>{visibleProjects.length}</span></header>{busy && <p role="status">Searching…</p>}
    <div className="library-project-list">{visibleProjects.map(row=><div className={"library-project-card"+(row.key===selectedKey?" is-selected":"")} key={row.key}>
     <button className="library-project-choice" aria-pressed={row.key===selectedKey} onClick={()=>{setSelectedKey(row.key);setError("");}}><strong>{row.number || "No number"}</strong><span>{row.title || "Not recorded"}</span><small>{sources[row.source]}</small></button>
     {row.operation_id && row.intake_status!=="completed" && <div className="library-incomplete"><span>Receipt incomplete</span><button disabled={receiving} onClick={()=>{setResumeOperation(row.operation_id!);setReceiving(true);}}>Continue receipt</button></div>}
    </div>)}</div>
    {!busy && !visibleProjects.length && <p className="library-empty">{unavailableProjects.length ? "No available material locations. Review the location warning." : search?"No matching project materials.":"No materials to show. Receive existing files."}</p>}
   </aside>
   <section className="library-files" aria-label="Selected project materials">{selected ? <>
    <header className="library-project-heading" aria-label="Browsing materials"><small>Browsing materials</small><h2>{selected.number || "Project materials"}</h2><p>{selected.title}</p><div className="library-location"><strong>Managed location</strong><span className="library-location-path"><UiIcon name="folder"/>{selected.folder_path || "No materials linked yet"}</span><button disabled={!selected.available} title={!selected.available ? selected.folder_path ? "Restore access to the registered folder, then refresh." : "Open the project Workbench to create or link its working folder." : undefined} onClick={()=>void openFolder()}><UiIcon name="folder"/>Open folder</button></div><button className="library-text-link" onClick={()=>setDetails(selected)}>Materials information</button></header>
    <section className="library-copy-destination" aria-label="Copy destination">{copyContext ? <><strong>Copy destination (Workbench): {copyContext.target.number || "No number"} · {copyContext.target.title}</strong><span>{copyContext.target.folder_path}</span></> : <span>Open the target project's Workbench, then return here using Reference Library to copy files.</span>}</section>
    {selected.operation_id && selected.intake_status!=="completed" ? <p className="library-empty">Receipt incomplete. Continue receipt to finish copying and registration.</p> : <MaterialFiles key={selected.key} canCopy={Boolean(copyContext)} onRefresh={scanning==="idle" ? ()=>void refreshIndex() : undefined} onOpenWorkbench={selected.project_id ? ()=>onOpenProject(selected.project_id!) : undefined} project={selected} query={search} kind={kind} refresh={reload} onError={setError} onWarnings={setBrowseWarnings} onCopy={file=>setCopy({project:selected,file})}/>}
   </> : <div className="library-empty"><UiIcon name="folder"/><p>Select a project to view its materials.</p></div>}</section>
  </div>
  {details && <MaterialDetails key={details.key} project={details} onClose={()=>setDetails(null)} onBrowse={key=>{setDetails(null);setSelectedKey(key);}} onProject={onOpenProject} onChanged={()=>setReload(value=>value+1)}/>}
  {copy && <CopyMaterials source={copy.project} file={copy.file} context={copyContext} onClose={()=>setCopy(null)} onCopied={()=>setReload(value=>value+1)} onTargetMaterials={row=>{setCopy(null);setDetails(row);setSelectedKey(row.key);setSearch("");setQuery("");setSource("all");setKind("all");setReload(value=>value+1);}}/>}
 </section>;
}
