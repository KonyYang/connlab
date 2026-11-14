import { useEffect, useMemo, useState } from "react";
import { openReferenceFile, searchReferenceLibrary, type ReferenceProject, type BrowseFile } from "../api/referenceLibrary";
import { ReceiveMaterials } from "../features/material-receipts/ReceiveMaterials";
import { MaterialDetails } from "../features/material-receipts/MaterialDetails";
import { MaterialFiles } from "../features/material-receipts/MaterialFiles";
import { CopyMaterials } from "../features/material-receipts/CopyMaterials";
import { UiIcon } from "../components/common/UiIcon";
import "./reference-library.css";

const kinds: Record<string,string> = { application: "Application", plan: "Test plan", record: "Test record", report: "Report", photo: "Photo", other: "Other" };
const sources: Record<string,string> = { connlab: "ConnLab project", received: "Received materials", linked: "Linked folder" };
const saved = () => { try { return JSON.parse(sessionStorage.getItem("reference-search") ?? "{}"); } catch { return {}; } };
const initialEntry = () => new URLSearchParams(window.location.search).get("entry") ?? saved().project ?? "";
const matchesKey = (row: ReferenceProject, key: string) => row.key === key || Boolean(row.member_id && key === "member:" + row.member_id);
export function ReferenceLibraryPage({ onOpenProject, currentProjectId }: { onOpenProject: (id:string) => void; currentProjectId?: string | null; onOpenMember?: (id:string) => void; onOpenLinked?: (id:string) => void }) {
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
 const [receiving,setReceiving] = useState(() => new URLSearchParams(window.location.search).get("receive") === "1");
 const [receiveTarget,setReceiveTarget] = useState<ReferenceProject | null>(null);
 const [details,setDetails] = useState<ReferenceProject | null>(null);
 const [copy,setCopy] = useState<{project:ReferenceProject;file:BrowseFile} | null>(null);
 useEffect(() => {
  let live=true; const controller=new AbortController(); setBusy(true); setError(""); setBrowseWarnings([]);
  sessionStorage.setItem("reference-search",JSON.stringify({query:search,source,kind,project:selectedKey}));
  void searchReferenceLibrary(search,source,kind,"",0,controller.signal).then(async result => {
   let rows=result.projects;
   if (!search && source === "all" && kind === "all" && selectedKey && !rows.some(row=>matchesKey(row,selectedKey))) {
    const extra=await searchReferenceLibrary("","all","all",selectedKey,0,controller.signal);
    rows=[...rows,...extra.projects.filter(row=>!rows.some(old=>old.key===row.key))];
   }
   if (!live) return;
   setProjects(rows); setWarnings(result.warnings);
   setSelectedKey(current=>rows.find(row=>matchesKey(row,current))?.key ?? rows[0]?.key ?? "");
  }).catch(cause=>{if(live)setError((cause as Error).message);}).finally(()=>{if(live)setBusy(false);});
  return()=>{live=false;controller.abort();};
 },[search,source,kind,reload]);
 const selected=projects.find(row=>row.key===selectedKey) ?? null;
 useEffect(()=>{sessionStorage.setItem("reference-search",JSON.stringify({query:search,source,kind,project:selectedKey}));},[selectedKey,search,source,kind]);
 const issues=useMemo(()=>Array.from(new Set([...(error?[error]:[]),...warnings,...browseWarnings])),[error,warnings,browseWarnings]);
 const lost=projects.filter(row=>!row.available && row.folder_path);
 function closeReceipt(){setReceiving(false);const url=new URL(window.location.href);url.searchParams.delete("receive");window.history.replaceState(null,"",url);}
 function received(key:string){closeReceipt();setSelectedKey(key);setSearch("");setQuery("");setSource("all");setKind("all");setReload(value=>value+1);}
 async function openFolder(){if(!selected)return;setError("");try{await openReferenceFile(selected.key);}catch(cause){setError((cause as Error).message);}}
 return <section className="reference-library" aria-label="Project materials library">
  <form className="library-search" onSubmit={event=>{event.preventDefault();setSearch(query);setReload(value=>value+1);}}>
   <div className="library-search-input"><UiIcon name="search"/><input aria-label="Search project materials" placeholder="Project number, product, test item or filename…" value={query} onChange={event=>setQuery(event.target.value)}/></div>
   <button className="library-primary" type="submit" disabled={busy}>Search</button><button className="library-primary" type="button" onClick={()=>{setReceiveTarget(null);setReceiving(true);}}><UiIcon name="new-project"/>Receive materials</button>
  </form>
  <div className="library-filters">
   <label><span className="library-sr-only">Source</span><select value={source} onChange={event=>setSource(event.target.value)}><option value="all">All sources</option>{Object.entries(sources).map(([key,label])=><option key={key} value={key}>{label}</option>)}</select></label>
   <label><span className="library-sr-only">Material type</span><select value={kind} onChange={event=>setKind(event.target.value)}><option value="all">All material types</option>{Object.entries(kinds).map(([key,label])=><option key={key} value={key}>{label}</option>)}</select></label>
   {(search || source!=="all" || kind!=="all") && <button onClick={()=>{setQuery("");setSearch("");setSource("all");setKind("all");}}>Clear filters</button>}
   <button className="library-refresh" disabled={busy} onClick={()=>setReload(value=>value+1)}><UiIcon name="refresh"/>Refresh</button>
  </div>
  {issues.length>0 && <div className="library-issues" role={error?"alert":"status"}><details><summary>{lost.length ? lost.length+" material location(s) unavailable" : "Materials need attention"}<span>View issues and locate</span></summary><ul>{issues.map(note=><li key={note}>{note}</li>)}</ul>{lost.map(row=><button key={row.key} onClick={()=>{setSelectedKey(row.key);setDetails(row);}}>Locate {row.number || row.title}</button>)}{error && <button onClick={()=>setReload(value=>value+1)}>Retry</button>}</details></div>}
  <div className="library-workspace">
   <aside className="library-projects" aria-label="Project materials"><header><strong>Project materials</strong><span>{projects.length}</span></header>{busy && <p role="status">Searching…</p>}
    <div className="library-project-list">{projects.map(row=><div className={"library-project-card"+(row.key===selectedKey?" is-selected":"")} key={row.key}>
     <button className="library-project-choice" aria-pressed={row.key===selectedKey} onClick={()=>{setSelectedKey(row.key);setError("");}}><strong>{row.number || "No number"}</strong><span>{row.title || "Not recorded"}</span><small>{sources[row.source]}</small>{!row.available && <em>{row.folder_path?"Original location unavailable":"No materials linked yet"}</em>}</button>
     {!row.available && row.folder_path && <button className="library-locate-link" onClick={()=>setDetails(row)}>Locate folder</button>}
    </div>)}</div>
    {!busy && !projects.length && <p className="library-empty">{search?"No matching project materials.":"No linked materials to show. Search to find unlinked projects, or receive existing files."}</p>}
   </aside>
   <section className="library-files" aria-label="Selected project materials">{selected ? <>
    <header className="library-project-heading"><h2>{selected.number || "Project materials"}</h2><p>{selected.title}</p><div className="library-location"><strong>Managed location</strong><span className="library-location-path"><UiIcon name="folder"/>{selected.folder_path || "No materials linked yet"}</span><button disabled={!selected.available} onClick={()=>void openFolder()}><UiIcon name="folder"/>Open folder</button></div><button className="library-text-link" onClick={()=>setDetails(selected)}>Materials information</button></header>
    <MaterialFiles key={selected.key} project={selected} query={search} kind={kind} refresh={reload} onError={setError} onWarnings={setBrowseWarnings} onCopy={file=>setCopy({project:selected,file})}/>
   </> : <div className="library-empty"><UiIcon name="folder"/><p>Select a project to view its materials.</p></div>}</section>
  </div>
  {receiving && <ReceiveMaterials initialTarget={receiveTarget} onClose={closeReceipt} onReceived={received}/>}
  {details && <MaterialDetails project={details} onClose={()=>setDetails(null)} onBrowse={key=>{setDetails(null);setSelectedKey(key);}} onProject={onOpenProject} onChanged={()=>setReload(value=>value+1)} onSupplement={row=>{setDetails(null);setReceiveTarget(row);setReceiving(true);}}/>}
  {copy && <CopyMaterials source={copy.project} file={copy.file} currentProjectId={currentProjectId} onClose={()=>setCopy(null)} onCopied={()=>setReload(value=>value+1)}/>}
 </section>;
}
