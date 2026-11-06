import { useEffect, useRef, useState } from 'react';
import { previewIntakeMaterials, saveIntakeMaterials, openMaterialsFolder, type MaterialsPreview } from '../../api/intakeMaterials';

export function SaveMaterialsDialog({packageId, onClose}: {packageId: string; onClose: () => void}) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {dialog.current?.showModal();}, []);
  const [preview, setPreview] = useState<MaterialsPreview | null>(null);
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [saved, setSaved] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  useEffect(() => { let active = true; void previewIntakeMaterials(packageId).then(value => {
    if (active) {setPreview(value); setName(value.folder_name);}
  }, reason => {if(active) setError(String(reason.message ?? reason));}); return () => {active=false;}; }, [packageId]);
  async function save() {
    if(busy) return; setBusy(true); setError('');
    try { const result = await saveIntakeMaterials(packageId, name); setSaved(result.path); }
    catch(reason) {setError(reason instanceof Error ? reason.message : 'Unable to save materials.');}
    finally {setBusy(false);}
  }
  async function open() {
    try {const result=await openMaterialsFolder(name); if(result.status!=='opened') setError(result.message);}
    catch(reason) {setError(reason instanceof Error ? reason.message : 'Unable to open folder.');}
  }
  return <dialog ref={dialog} className="temporary-ltr-dialog" aria-label="Save materials" onCancel={event => {event.preventDefault(); if(!busy) onClose();}}>
    <h2>Save materials</h2>
    {preview && <><p>{preview.root}</p><label>Folder name<input autoFocus value={name} disabled={busy || !!saved} onChange={event=>setName(event.target.value)} /></label>
      <ul>{preview.files.map(file=><li key={file}>{file}</li>)}</ul></>}
    {error && <p role="alert">{error}</p>}
    {saved && <p role="status">Saved to {saved}</p>}
    <div className="temporary-ltr-actions">{saved ? <button onClick={()=>void open()}>Open folder</button> : <button disabled={!preview || busy || !name.trim()} onClick={()=>void save()}>{busy?'Saving…':'Save'}</button>}
    <button disabled={busy} onClick={onClose}>{saved?'Close':'Cancel'}</button></div>
  </dialog>;
}
