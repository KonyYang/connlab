import { useEffect, useState } from "react";
import { browseReferenceFiles, openReferenceFile, searchReferenceLibrary, type ReferenceProject, type BrowseFile } from "../../api/referenceLibrary";
import { MaterialFileList } from "./MaterialFileList";
import { UiIcon } from "../../components/common/UiIcon";
export function MaterialFiles({ project, query, kind, refresh, onError, onWarnings, onRefresh }: { project: ReferenceProject; query: string; kind: string; refresh: number; onError: (message: string) => void; onWarnings: (notes: string[]) => void; onRefresh?: () => void }) {
 const [rows, setRows] = useState<BrowseFile[]>([]);
 const [selected, setSelected] = useState<BrowseFile | null>(null);
 const [busy, setBusy] = useState(false);
 const [offset, setOffset] = useState(0);
 const [total, setTotal] = useState(0);
 const label = [project.number, project.title, project.folder_path.split(/[\\/]/).pop()].join(" ").toLowerCase();
 const filtered = kind !== "all" || query.trim().toLowerCase().split(/\s+/).some(word => !label.includes(word));
 useEffect(() => { setOffset(0); setSelected(null); }, [project.key, query, kind]);
 useEffect(() => {
  let live = true; const controller = new AbortController(); setSelected(null); setRows([]); onWarnings([]);
  if (!project.available) return;
  setBusy(true);
  const request = filtered
   ? searchReferenceLibrary(query, "all", kind, project.key, offset, controller.signal).then(result => ({ items: result.files.map(row => ({ ...row, is_directory: false, modified_at: null, extension: row.name.split(".").at(-1) ?? "" })), warnings: result.warnings, total: result.total }))
   : browseReferenceFiles(project.key, "", controller.signal).then(result => ({ ...result, total: result.items.length }));
  void request.then(result => { if (live) { setRows(result.items); setTotal(result.total); onWarnings(result.warnings); } }).catch(cause => { if (live) onError((cause as Error).message); }).finally(() => { if (live) setBusy(false); });
  return () => { live = false; controller.abort(); };
 }, [project.key, project.available, query, kind, offset, refresh, filtered]);
 async function open(file: BrowseFile, containing = false) { onError(""); try { await openReferenceFile(project.key, file.relative_path, containing); } catch (cause) { onError((cause as Error).message); } }
 if (!project.available) return <>{project.folder_path && <div className="library-empty">
  <UiIcon name="folder" /><p>Original material location is unavailable. The entry is retained. Restore access to the registered folder, then refresh.</p>
  <button disabled={!onRefresh} onClick={onRefresh}>Refresh materials</button>
 </div>}</>;
 return <>
  <div className="library-file-scroll">
  <MaterialFileList projectKey={project.key} rows={rows} selectedPath={selected?.relative_path} showPaths={filtered}
    onOpen={file => void open(file)} onSelect={setSelected}
    onOpenContaining={file => void open(file, true)}
    onCollapse={folder => setSelected(file => file?.relative_path.startsWith(folder + "/") ? null : file)} />
  {busy && <p role="status">Loading files…</p>}{!busy && !rows.length && <p className="library-empty">{filtered ? "No matching files in this project." : "This directory contains no files or folders."}</p>}
  </div>
  {filtered && total > 100 && <div className="library-file-actions"><button disabled={!offset || busy} onClick={() => setOffset(value => Math.max(0,value-100))}>Previous</button><span>{offset + 1}–{Math.min(offset + 100,total)} of {total}</span><button disabled={offset + 100 >= total || busy} onClick={() => setOffset(value => value+100)}>Next</button></div>}
 </>;
}
