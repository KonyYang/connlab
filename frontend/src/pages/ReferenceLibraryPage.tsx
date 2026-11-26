import {runtimeSessionStorage} from "../runtimeEnvironment";
import {refreshArchive,getArchiveJob,cancelArchiveJob} from "../api/materialReceipts";
import { useEffect, useMemo, useRef, useState } from "react";
import { openReferenceFile, searchReferenceLibrary, type ReferenceProject } from "../api/referenceLibrary";
import { ReceiveMaterials } from "../features/material-receipts/ReceiveMaterials";
import { MaterialFiles } from "../features/material-receipts/MaterialFiles";
import { UiIcon } from "../components/common/UiIcon";
import "./reference-library.css";
import { LibraryProjectTable } from "../features/material-receipts/LibraryProjectTable";

const kinds: Record<string,string> = { application: "Application", plan: "Test plan", record: "Test record", report: "Report", photo: "Photo", other: "Other" };
const sources: Record<string,string> = { materials: "Materials library folder", projects: "Project default save location" };
const saved = () => { try { return JSON.parse(runtimeSessionStorage.getItem("reference-search") ?? "{}"); } catch { return {}; } };
const initialEntry = () => new URLSearchParams(window.location.search).get("entry") ?? saved().project ?? "";
const receiptIncomplete = (row: ReferenceProject) => Boolean(row.operation_id && row.intake_status !== "completed");
const listed = (row: ReferenceProject) => row.available || receiptIncomplete(row);
export function ReferenceLibraryPage({ onOpenSettings }: { onOpenSettings?: () => void }) {
 const [direct,setDirect] = useState(() => new URLSearchParams(window.location.search).get("entry") ?? "");
 const [query,setQuery] = useState<string>(() => direct ? "" : saved().query ?? "");
 const [search,setSearch] = useState(query);
 const [source,setSource] = useState<string>(() => direct || !(saved().source in sources) ? "all" : saved().source);
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
 const pendingSelection = useRef("");
 const scanActive = useRef(false), scanRequested = useRef(false);
 const [scanWarnings,setScanWarnings]=useState<string[]>([]);
 const [offlineRoot,setOfflineRoot]=useState<string|null>(null);
 const scanJob=useRef<string|null>(null),mounted=useRef(false),initialScan=useRef(false);
 useEffect(() => {
  let live=true; const controller=new AbortController(); setBusy(true); setError(""); setBrowseWarnings([]);
  runtimeSessionStorage.setItem("reference-search",JSON.stringify({query:search,source,kind,project:selectedKey}));
  void searchReferenceLibrary(search,source,kind,"",0,controller.signal).then(async result => {
   let rows=result.projects;
   let directKey=direct;
   if (direct && !rows.some(row=>row.key===direct)) {
    const extra=await searchReferenceLibrary("","all","all",direct,0,controller.signal);
    directKey=extra.projects[0]?.key ?? direct;
    rows=[...rows,...extra.projects.filter(row=>!rows.some(old=>old.key===row.key))];
   }
   if (!live) return;
   setProjects(rows); setWarnings(result.warnings);
   const candidates=rows.filter(listed);
   setSelectedKey(current=>{
    if(direct) return directKey;
    const receivedRow=candidates.find(row=>row.folder_path===pendingSelection.current);
    if(receivedRow) return receivedRow.key;
    return candidates.find(row=>row.key===current)?.key ?? candidates[0]?.key ?? "";
   });
  }).catch(cause=>{if(live){setProjects([]);setError((cause as Error).message);}}).finally(()=>{if(live)setBusy(false);});
  return()=>{live=false;controller.abort();};
 },[search,source,kind,reload,direct]);
 const visibleProjects=projects.filter(listed);
 const selected=projects.find(row=>row.key===selectedKey) ?? null;
 const unavailableLink=Boolean(direct && (!selected || (!selected.available && selected.folder_path && !receiptIncomplete(selected))));
 useEffect(()=>{runtimeSessionStorage.setItem("reference-search",JSON.stringify({query:search,source,kind,project:selectedKey}));},[selectedKey,search,source,kind]);
 const issues=useMemo(()=>Array.from(new Set([...(error?[error]:[]),...scanWarnings,...warnings,...browseWarnings])),[error,scanWarnings,warnings,browseWarnings]);
 async function refreshIndex(){
  if(scanActive.current){scanRequested.current=true;return;}
  scanActive.current=true;
  setScanning("working");
  try{
   const {job_id}=await refreshArchive();scanJob.current=job_id;
   if(!mounted.current){await cancelArchiveJob(job_id);return;}
   for(;;){const job=await getArchiveJob(job_id);if(!mounted.current)return;
    if(job.status==="working"||job.status==="cancellation_requested"){setScanning(job.status);await new Promise(resolve=>setTimeout(resolve,200));continue;}
    if(job.status==="failed")setScanWarnings([job.error||"Materials scan failed. Refresh to retry."]);
    else if(job.result){
     const result=job.result as {available?:boolean;root_path?:string;warnings?:string[]};
     setOfflineRoot(result.available===false ? result.root_path ?? "" : null);
     setScanWarnings(result.warnings??[]);
    }
    setReload(value=>value+1);break;
   }
  }catch(cause){if(mounted.current)setScanWarnings([(cause as Error).message]);}
  finally{
   scanJob.current=null;scanActive.current=false;
   if(mounted.current){
    if(scanRequested.current){scanRequested.current=false;void refreshIndex();}
    else setScanning("idle");
   }
  }
 }
 useEffect(()=>{mounted.current=true;if(!initialScan.current){initialScan.current=true;void refreshIndex();}return()=>{mounted.current=false;if(scanJob.current)void Promise.resolve(cancelArchiveJob(scanJob.current)).catch(()=>undefined);};},[]);
 async function cancelScan(){
  if(!scanJob.current)return;
  scanRequested.current=false;
  setScanning("cancellation_requested");
  try{await cancelArchiveJob(scanJob.current);}
  catch(cause){if(mounted.current){setScanWarnings([(cause as Error).message]);setScanning("working");}}
 }
 function closeReceipt(){setReceiving(false);}
 function received(path:string){pendingSelection.current=path;closeReceipt();setDirect("");setSearch("");setQuery("");setSource("all");setKind("all");void refreshIndex();}
 async function openFolder(){if(!selected)return;setError("");try{await openReferenceFile(selected.key);}catch(cause){setError((cause as Error).message);}}
 return <section className="reference-library" aria-label="Project materials library">
  <form className="library-search" onSubmit={event=>{event.preventDefault();setDirect("");pendingSelection.current="";setSearch(query);setReload(value=>value+1);void refreshIndex();}}>
   <div className="library-search-input"><UiIcon name="search"/><input aria-label="Search project materials" placeholder="Project ID, description or filename…" value={query} onChange={event => {
    const value = event.target.value;
    setQuery(value);
    if (!value.trim()) setSearch("");
   }}/></div>
   <button className="library-primary" type="submit">Search</button><button className="library-primary" type="button" disabled={receiving} onClick={()=>{setResumeOperation(undefined);setReceiving(true);}}><UiIcon name="new-project"/>Receive materials</button>
  </form>
  {receiving && <ReceiveMaterials initialOperation={resumeOperation} onClose={closeReceipt} onReceived={received}/>}
  <div className="library-filters">
   <label><span className="library-sr-only">Source</span><select value={source} onChange={event=>{setDirect("");setSource(event.target.value);}}><option value="all">All sources</option>{Object.entries(sources).map(([key,label])=><option key={key} value={key}>{label}</option>)}</select></label>
   <label><span className="library-sr-only">Material type</span><select value={kind} onChange={event=>{setDirect("");setKind(event.target.value);}}><option value="all">All material types</option>{Object.entries(kinds).map(([key,label])=><option key={key} value={key}>{label}</option>)}</select></label>
   {(search || source!=="all" || kind!=="all") && <button onClick={()=>{setQuery("");setSearch("");setSource("all");setKind("all");}}>Clear filters</button>}
   <button className="library-refresh" disabled={scanning==="cancellation_requested"} onClick={()=>{if(scanning==="working")void cancelScan();else void refreshIndex();}}><UiIcon name="refresh"/>{scanning==="cancellation_requested"?"Cancelling scan…":scanning==="working"?"Cancel scan":"Refresh"}</button>
  </div>
  {(issues.length>0 || offlineRoot!==null) && <div className="library-issues" role={error || offlineRoot!==null?"alert":"status"}>
   {issues.length>0 && <ul>{issues.map(note=><li key={note}>{note}</li>)}</ul>}
   {offlineRoot && <p>{offlineRoot}</p>}
   {offlineRoot!==null ? <><button disabled={scanning!=="idle"} onClick={()=>void refreshIndex()}>Retry</button>{onOpenSettings && <button onClick={onOpenSettings}>Open Settings</button>}</> : error && <button onClick={()=>setReload(value=>value+1)}>Retry</button>}
  </div>}
  <div className="library-workspace">
   <aside className="library-projects" aria-label="Project materials">
    {busy && <p role="status">Searching…</p>}
    <LibraryProjectTable projects={visibleProjects} selectedKey={selectedKey} receiving={receiving}
     onSelect={key=>{pendingSelection.current="";setDirect("");setSelectedKey(key);setError("");}}
     onResume={id=>{setResumeOperation(id);setReceiving(true);}} />
    {!busy && !visibleProjects.length && <p className="library-empty">{search?"No matching project materials.":"No materials to show."}</p>}
   </aside>
   <section className="library-files" aria-label="Selected project materials">{unavailableLink ? (!busy && !error && offlineRoot===null && <div className="library-empty"><p>This material location is unavailable.</p>{selected?.folder_path && <p>{selected.folder_path}</p>}<button disabled={scanning!=="idle"} onClick={()=>void refreshIndex()}>Refresh materials</button></div>) : selected ? <>
    <header className="library-project-heading" aria-label="Browsing materials">
     <div className="library-location">
      <span className="library-location-path" style={{flexBasis: 0}}>{selected.folder_path}</span>
      <button type="button" aria-label="Open folder" disabled={!selected.available}
       title={selected.available ? "Open folder" : selected.folder_path ? "Restore access to the registered folder, then refresh." : "No folder linked."}
       onClick={() => void openFolder()}><UiIcon name="folder" /></button>
     </div>
    </header>
    {receiptIncomplete(selected) ? <p className="library-empty">Receipt incomplete. Continue receipt to finish copying and registration.</p> : <MaterialFiles key={selected.key} onRefresh={scanning==="idle" ? ()=>void refreshIndex() : undefined} project={selected} query={search} kind={kind} refresh={reload} onError={setError} onWarnings={setBrowseWarnings}/>}
   </> : <div className="library-empty"><UiIcon name="folder"/><p>Select a project to view its materials.</p></div>}</section>
  </div>
 </section>;
}
