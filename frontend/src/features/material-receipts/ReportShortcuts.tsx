import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { getReportShortcuts, setReportShortcut, clearReportShortcut, type ReportRole, type ReportShortcuts } from "../../api/reportShortcuts";
import { openReferenceFile } from "../../api/referenceLibrary";
import "./materials.css";
export const reportLabels: Record<ReportRole,string>={internal:"Internal report",customer:"Customer report"};

export function useReportShortcuts(key:string, refresh:number, onError:(message:string)=>void, rootAvailable:boolean) {
 const [data,setData]=useState<ReportShortcuts>({key,items:[]});
 const [busy,setBusy]=useState(false);
 const [loaded,setLoaded]=useState(false);
 const [replacement,setReplacement]=useState<{role:ReportRole;oldPath:string;newPath:string}|null>(null);
 const [reselectRole,setReselectRole]=useState<ReportRole|null>(null);
 const generation=useRef(0);
 useEffect(()=>{
  const run=++generation.current;const controller=new AbortController();setLoaded(false);setData({key,items:[]});setReplacement(null);setReselectRole(null);setBusy(false);
  void getReportShortcuts(key,controller.signal).then(value=>{if(run===generation.current){setData(value);setLoaded(true);}}).catch(cause=>{if(run===generation.current)onError((cause as Error).message);});
  return()=>{generation.current++;controller.abort();};
 },[key,refresh]);
 async function act(action:()=>Promise<ReportShortcuts>){
  const run=++generation.current;setBusy(true);onError("");
  try{const value=await action();if(run===generation.current){setData(value);setReplacement(null);}}
  catch(cause){if(run===generation.current)onError((cause as Error).message);}
  finally{if(run===generation.current)setBusy(false);}
 }
 function choose(role:ReportRole,path:string){
  setReselectRole(null);
  const current=data.items.find(row=>row.role===role)?.relative_path??null;
  if(current && current!==path)setReplacement({role,oldPath:current,newPath:path});
  else void act(()=>setReportShortcut(data.key,role,path,current,false));
 }
 const remove=(role:ReportRole)=>{const current=data.items.find(row=>row.role===role);if(current)void act(()=>clearReportShortcut(data.key,role,current.relative_path));};
 async function open(path:string){try{await openReferenceFile(data.key,path);}catch(cause){onError((cause as Error).message);}}
 const links=data.items.length ? <div className="library-report-shortcuts" role="group" aria-label="Common reports"><strong>Common reports</strong>{data.items.map(row=><div key={row.role}><span><button disabled={!row.available} onClick={()=>void open(row.relative_path)} title={`${row.relative_path}${row.modified_at ? " · Modified " + new Date(row.modified_at).toLocaleString() : ""}`}>{reportLabels[row.role]} · {row.relative_path.split("/").at(-1)}</button><button className="library-remove-shortcut" disabled={busy} aria-label={`Remove ${reportLabels[row.role]} shortcut`} title="Remove shortcut only" onClick={()=>remove(row.role)}>×</button></span>{!row.available && <><small>File unavailable; shortcut retained.</small>{rootAvailable && <button disabled={busy} onClick={()=>setReselectRole(row.role)}>Choose replacement for {reportLabels[row.role]}</button>}</>}</div>)}</div> : null;
 const dialog=replacement ? createPortal(<div className="materials-overlay"><section className="materials-dialog" role="dialog" aria-modal="true" aria-label={`Replace ${reportLabels[replacement.role]} shortcut`}><h2>Replace {reportLabels[replacement.role]}</h2><p className="materials-path">Current: {replacement.oldPath}</p><p className="materials-path">Selected: {replacement.newPath}</p><div className="materials-actions"><button disabled={busy} onClick={()=>void act(()=>setReportShortcut(data.key,replacement.role,replacement.newPath,replacement.oldPath,true))}>Confirm replacement</button><button disabled={busy} onClick={()=>setReplacement(null)}>Keep current shortcut</button></div></section></div>,document.body) : null;
 return {data,busy:busy||!loaded,choose,remove,links,dialog,reselectRole,cancelReselect:()=>setReselectRole(null)};
}
