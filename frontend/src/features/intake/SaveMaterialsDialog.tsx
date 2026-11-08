import { useEffect, useRef, useState } from 'react';
import { previewIntakeMaterials, saveIntakeMaterials, openMaterialsFolder, type MaterialsPreview } from '../../api/intakeMaterials';
import './SaveMaterialsDialog.css';

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
  return <dialog ref={dialog} className="save-materials-dialog" aria-label="Save materials" onCancel={event => {event.preventDefault(); if(!busy) onClose();}}>
    <header className="save-materials-header"><h2>Save materials</h2></header>
    <div className="save-materials-body">
      {preview && <>
        <div className="save-materials-location"><span className="ui-field-label">Save location</span><p>{preview.root}</p></div>
        <label className="save-materials-name"><span className="ui-field-label">Folder name</span><input autoFocus value={name} disabled={busy || !!saved} onChange={event=>setName(event.target.value)} /></label>
        <section className="save-materials-files" aria-label="Files to save">
          <div className="save-materials-files-heading"><h3>Files to save</h3><span>{preview.files.length}</span></div>
          <ul>{preview.files.map(file=><li key={file}><span className="save-materials-file-type" aria-hidden="true">{file.split('.').pop()?.slice(0, 4).toUpperCase()}</span><span>{file}</span></li>)}</ul>
        </section>
      </>}
      {!preview && !error && <p className="save-materials-loading" role="status">Loading materials…</p>}
      {error && <p className="save-materials-error" role="alert">{error}</p>}
      {saved && <p className="save-materials-success" role="status">Saved to {saved}</p>}
    </div>
    <footer className="save-materials-actions">
      <button className="ui-secondary-action" disabled={busy} onClick={onClose}>{saved?'Close':'Cancel'}</button>
      {saved ? <button className="ui-primary-action" onClick={()=>void open()}>Open folder</button> : <button className="ui-primary-action" disabled={!preview || busy || !name.trim()} onClick={()=>void save()}>{busy?'Saving…':'Save'}</button>}
    </footer>
  </dialog>;
}
