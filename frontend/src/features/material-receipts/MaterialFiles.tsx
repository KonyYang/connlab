import { useEffect, useState } from "react";
import { browseReferenceFiles, openReferenceFile, searchReferenceLibrary, type ReferenceProject, type BrowseFile } from "../../api/referenceLibrary";
import { useReportShortcuts, reportLabels } from "./ReportShortcuts";
import type { ReportRole } from "../../api/reportShortcuts";
import { UiIcon } from "../../components/common/UiIcon";
export function MaterialFiles({ project, query, kind, refresh, onError, onWarnings, onCopy }: { project: ReferenceProject; query: string; kind: string; refresh: number; onError: (message: string) => void; onWarnings: (notes: string[]) => void; onCopy: (file: BrowseFile) => void }) {
 const shortcuts=useReportShortcuts(project.key,refresh,onError,project.available);
 const [directory, setDirectory] = useState("");
 const [rows, setRows] = useState<BrowseFile[]>([]);
 const [selected, setSelected] = useState<BrowseFile | null>(null);
 const [busy, setBusy] = useState(false);
 const [offset, setOffset] = useState(0);
 const [total, setTotal] = useState(0);
 const filtered = Boolean(query || kind !== "all");
 useEffect(() => { setDirectory(""); setOffset(0); setSelected(null); }, [project.key, query, kind]);
 useEffect(() => {
  let live = true; const controller = new AbortController(); setSelected(null); setRows([]); onWarnings([]);
  if (!project.available) return;
  setBusy(true);
  const request = filtered
   ? searchReferenceLibrary(query, "all", kind, project.key, offset, controller.signal).then(result => ({ items: result.files.map(row => ({ ...row, is_directory: false, modified_at: null, extension: row.name.split(".").at(-1) ?? "" })), warnings: result.warnings, total: result.total }))
   : browseReferenceFiles(project.key, directory, controller.signal).then(result => ({ ...result, total: result.items.length }));
  void request.then(result => { if (live) { setRows(result.items); setTotal(result.total); onWarnings(result.warnings); } }).catch(cause => { if (live) onError((cause as Error).message); }).finally(() => { if (live) setBusy(false); });
  return () => { live = false; controller.abort(); };
 }, [project.key, project.available, query, kind, directory, offset, refresh]);
 async function open(file: BrowseFile, containing = false) { onError(""); try { await openReferenceFile(project.key, file.relative_path, containing); } catch (cause) { onError((cause as Error).message); } }
 if (!project.available) return <>{shortcuts.links}<div className="library-empty"><UiIcon name="folder" /><p>{project.folder_path ? "Original material location is unavailable. The entry is retained." : "No materials linked yet."}</p></div></>;
 const up = directory.split("/").slice(0,-1).join("/");
 return <>
  {shortcuts.links}{shortcuts.dialog}{shortcuts.reselectRole && <p className="library-reselect-report">Select the replacement file below for {reportLabels[shortcuts.reselectRole]}. <button onClick={shortcuts.cancelReselect}>Cancel report selection</button></p>}
  <div className="library-breadcrumb"><button disabled={!directory || busy} onClick={() => setDirectory("")}>All materials</button>{directory && <><span>/ {directory}</span><button disabled={busy} onClick={() => setDirectory(up)}>Up one folder</button></>}{filtered && <span>Search results</span>}</div>
  <div className="library-file-scroll"><table aria-label="Project material files"><thead><tr><th>Name</th><th>Modified</th><th>Type</th></tr></thead><tbody>{rows.map(row => {
   const extension = (row.extension || row.name.split(".").at(-1) || "").replace(/^\./, "").toLowerCase();
   const format = row.is_directory ? "Folder" : ["doc","docx"].includes(extension) ? "Word" : ["xls","xlsx","xlsm"].includes(extension) ? "Excel" : extension.toUpperCase() || "File";
   return <tr key={row.relative_path} className={selected?.relative_path === row.relative_path ? "file-selected" : ""} aria-selected={selected?.relative_path === row.relative_path}>
    <td><button className="library-file-name" onClick={() => {if(row.is_directory)setDirectory(row.relative_path);else{setSelected(row);if(shortcuts.reselectRole)shortcuts.choose(shortcuts.reselectRole,row.relative_path);}}} onDoubleClick={() => { if (!row.is_directory) void open(row); }}><span className={row.is_directory ? "file-symbol file-folder" : "file-symbol"}><UiIcon name={row.is_directory ? "folder" : "file"} /></span><span>{row.name}{filtered && <small>{row.relative_path}</small>}</span></button></td>
    <td>{row.modified_at ? new Date(row.modified_at).toLocaleDateString() : "—"}</td><td>{format}</td>
   </tr>;
  })}</tbody></table>
  {busy && <p role="status">Loading files…</p>}{!busy && !rows.length && <p className="library-empty">{filtered ? "No matching files in this project." : "This directory contains no files or folders."}</p>}
  </div>
  {filtered && total > 100 && <div className="library-file-actions"><button disabled={!offset || busy} onClick={() => setOffset(value => Math.max(0,value-100))}>Previous</button><span>{offset + 1}–{Math.min(offset + 100,total)} of {total}</span><button disabled={offset + 100 >= total || busy} onClick={() => setOffset(value => value+100)}>Next</button></div>}
  <div className="library-file-actions"><button className="library-primary" disabled={!selected || busy} onClick={() => { if (selected) void open(selected); }}><UiIcon name="file" />Open file</button><button disabled={!selected || busy} onClick={() => { if (selected) onCopy(selected); }}><UiIcon name="copy" />Copy to current project…</button><button disabled={!selected || busy} onClick={() => { if (selected) void open(selected,true); }}>Open containing folder</button>{selected && <details className="library-file-more"><summary>More</summary><div>{(["internal","customer"] as ReportRole[]).map(role=><div key={role}><button disabled={busy || shortcuts.busy} onClick={()=>shortcuts.choose(role,selected.relative_path)}>{shortcuts.data.items.some(row=>row.role===role) ? "Replace " : "Set as "}{reportLabels[role]}</button>{shortcuts.data.items.some(row=>row.role===role) && <button disabled={busy || shortcuts.busy} onClick={()=>shortcuts.remove(role)}>Remove {reportLabels[role]} shortcut</button>}</div>)}</div></details>}</div>
 </>;
}
