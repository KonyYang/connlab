import { useEffect, useRef, useState } from 'react';
import { applyReportPhotos, getReportPhotoSlots, getReportPhotoImage, downloadReportArtifact,
  type ReportAuthoringState, type ReportPhotoSlot } from '../../api/reportAuthoring';

export function ReportPhotoSlots({ projectId, state, disabled, onChanged }: {
  projectId: string; state: ReportAuthoringState; disabled: boolean; onChanged: (state: ReportAuthoringState) => void;
}) {
  const [slots, setSlots] = useState<{ output_sha256: string; slots: ReportPhotoSlot[] } | null>(null);
  const [slotId, setSlotId] = useState('');
  const [sourceId, setSourceId] = useState('');
  const [crop, setCrop] = useState<'preserve' | 'centre_crop'>('preserve');
  const [transform, setTransform] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [images, setImages] = useState<string[]>([]);
  const epoch = useRef(0);
  const output = state.outputs.at(-1);
  const source = state.sources.find(item => item.source_id === sourceId);
  const slot = slots?.slots.find(item => item.slot_id === slotId);
  useEffect(() => { epoch.current++; setSlots(null); setSlotId(''); setConfirmed(false); setBusy(false); setImages([]); }, [projectId, state.revision]);
  useEffect(() => () => { epoch.current++; }, []);
  useEffect(() => () => { images.forEach(url => URL.revokeObjectURL(url)); }, [images]);
  async function inspect() {
    if (!output) return;
    const token = ++epoch.current; setBusy(true); setError('');
    try { const next = await getReportPhotoSlots(projectId, output.output_id, state.revision); if (token === epoch.current) setSlots(next); }
    catch (cause) { if (token === epoch.current) setError(cause instanceof Error ? cause.message : 'Photo inspection failed.'); }
    finally { if (token === epoch.current) setBusy(false); }
  }
  async function preview() {
    if (!output || !slot || !source) return;
    const token = ++epoch.current; setBusy(true); setError(''); setConfirmed(false);
    try { const [old, replacement] = await Promise.all([getReportPhotoImage(projectId, output.output_id, slot.slot_id), downloadReportArtifact(source.download_url)]);
      if (token === epoch.current) setImages([URL.createObjectURL(old.blob), URL.createObjectURL(replacement.blob)]);
    } catch (cause) { if (token === epoch.current) setError(cause instanceof Error ? cause.message : 'Photo preview failed.'); }
    finally { if (token === epoch.current) setBusy(false); }
  }
  async function apply() {
    if (!output || !slots || !slot || !source || !confirmed) return;
    const token = ++epoch.current; setBusy(true); setError('');
    try { const next = await applyReportPhotos(projectId, { expected_revision: state.revision, output_id: output.output_id,
      output_sha256: slots.output_sha256, assignments: [{ slot_id: slotId, source_id: sourceId, crop_mode: crop, accept_slot_transform: transform }] });
      if (token === epoch.current) onChanged(next);
    } catch (cause) { if (token === epoch.current) setError(cause instanceof Error ? cause.message : 'Photo replacement failed.'); }
    finally { if (token === epoch.current) setBusy(false); }
  }
  if (!output) return null;
  return <section aria-label="Approved report photo slots"><h4>Replace photos in approved slots</h4>
    <fieldset disabled={busy || disabled}><button type="button" onClick={() => void inspect()}>Inspect photo slots</button>
      {slots && <>
        <label>Approved photo slot <select value={slotId} onChange={event => { setSlotId(event.target.value); setImages([]); setConfirmed(false); setTransform(false); }}>
          <option value="">Choose slot</option>{slots.slots.map((item, index) => <option key={item.slot_id} value={item.slot_id} disabled={!item.supported}>
            {index + 1}: {item.caption || 'Uncaptioned photo'}{!item.supported ? ` — ${item.reason}` : ''}</option>)}
        </select></label>
        <label>Replacement photo <select value={sourceId} onChange={event => { setSourceId(event.target.value); setImages([]); setConfirmed(false); }}>
          <option value="">Choose retained photo</option>{state.sources.filter(item => item.role === 'photo').map(item => <option key={item.source_id} value={item.source_id}>{item.file_name}</option>)}
        </select></label>
        {slot && <p>Slot size: {(slot.width_emu / 360000).toFixed(1)} × {(slot.height_emu / 360000).toFixed(1)} cm; rotation {slot.rotation / 60000}°; flips {slot.flip_horizontal ? 'horizontal' : ''} {slot.flip_vertical ? 'vertical' : ''}. Captions and numbering are retained.</p>}
        <label>Photo fit <select value={crop} onChange={event => { setCrop(event.target.value as typeof crop); setConfirmed(false); }}>
          <option value="preserve">Keep approved crop (requires matching aspect ratio)</option><option value="centre_crop">Centre-crop to the approved slot; do not stretch</option>
        </select></label>
        {slot && (slot.rotation !== 0 || slot.flip_horizontal || slot.flip_vertical) && <label><input type="checkbox" checked={transform} onChange={event => { setTransform(event.target.checked); setConfirmed(false); }} />I checked and accept this slot's existing rotation/flips for the new photo</label>}
        <button type="button" disabled={!slot || !source} onClick={() => void preview()}>Compare source photos</button>
        {images.length > 0 && <div><img src={images[0]} alt="Current slot source photo" style={{ maxWidth: '40%', maxHeight: 240 }} /><img src={images[1]} alt="Replacement source photo" style={{ maxWidth: '40%', maxHeight: 240 }} />
          <p>Source previews do not show Word crop/rotation. Check the generated Word copy before delivery.</p>
          <label><input type="checkbox" checked={confirmed} onChange={event => setConfirmed(event.target.checked)} />I verified the sample, slot, crop and orientation</label>
          <button type="button" disabled={!confirmed} onClick={() => void apply()}>Replace photo in a new copy</button>
        </div>}
      </>}
    </fieldset>{error && <p role="alert">{error}</p>}
  </section>;
}
