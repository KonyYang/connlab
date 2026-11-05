import { useEffect, useRef, useState, type KeyboardEvent } from 'react';
import { createPortal } from 'react-dom';
import { prepareTemporaryRegistration, previewTemporaryRegistration, commitTemporaryRegistration,
  type TemporaryRegistrationPreparation, type TemporaryRegistrationPreview } from '../../api/temporaryProjectRegistration';

const projectTypes = ['New Product Development', 'Product Extension', 'Innovation', 'Lab Activities (Lab Use Only)', 'Operational Support', 'Cost Reduction'];
const rowLabels = ['Month', 'Total', 'Monthly number', 'LTR Number', 'Project Type', 'Sample Description', 'Test Item', 'Test Type in sheet', 'Requested By', 'Mfg. Site', 'Project Leader', 'Test Result', 'Failed item', 'Sample deposition', 'Sub-contract', 'Test Fee', 'Remarks (PO)'];

export function TemporaryProjectRegistrationDialog({ projectId, onClose, onRegistered }: {
  projectId: string; onClose: () => void; onRegistered: () => void | Promise<void>;
}) {
  const [preparation, setPreparation] = useState<TemporaryRegistrationPreparation | null>(null);
  const [values, setValues] = useState<Record<string, string>>({});
  const [mode, setMode] = useState('auto');
  const [number, setNumber] = useState('');
  const [preview, setPreview] = useState<TemporaryRegistrationPreview | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pending = useRef(false);
  const dialog = useRef<HTMLElement>(null);
  const alive = useRef(true);
  const recovery = preview?.recovery_required === true;

  useEffect(() => {
    alive.current = true;
    const previousFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    dialog.current?.focus();
    let current = true;
    void prepareTemporaryRegistration(projectId).then(result => {
      if (!current) return;
      setPreparation(result); setValues(result.values); setPreview(result.recovery_preview);
      if (result.registered_ltr_number) setError(`This project is already registered as ${result.registered_ltr_number}. Close and refresh the project.`);
    }).catch(err => { if (current) setError(err instanceof Error ? err.message : 'Cannot load registration information.'); });
    return () => { current = false; alive.current = false; previousFocus?.isConnected && previousFocus.focus(); };
  }, [projectId]);

  function edit(key: string, value: string) {
    setValues(old => ({ ...old, [key]: value })); setPreview(null); setError(null);
  }
  async function runPreview() {
    if (pending.current) return;
    pending.current = true; setBusy(true); setError(null);
    try {
      const result = await previewTemporaryRegistration(projectId, { values, mode, specified_number: mode === 'specified' ? number : null });
      if (alive.current) { setPreview(result); setValues(result.values); }
    } catch (err) { if (alive.current) setError(err instanceof Error ? err.message : 'Cannot preview registration.'); }
    finally { pending.current = false; if (alive.current) setBusy(false); }
  }
  async function confirm() {
    if (!preview || pending.current) return;
    pending.current = true; setBusy(true); setError(null);
    try {
      await commitTemporaryRegistration(projectId, preview.preview_token);
      if (alive.current) await onRegistered();
    } catch (err) {
      if (alive.current) {
        setError(err instanceof Error ? err.message : 'Registration did not complete. Retry to check the pending write.');
        // The server retains the exact intent when Save may have happened.
        // Reload preparation instead of letting edits silently start a new number.
        try {
          const latest = await prepareTemporaryRegistration(projectId);
          if (alive.current) {
            setPreparation(latest); setValues(latest.values); setPreview(latest.recovery_preview);
            if (latest.registered_ltr_number === preview.ltr_number) {
              setError(`Registered as ${latest.registered_ltr_number}. Refresh the project to continue.`);
              await onRegistered();
            }
          }
        } catch { /* Keep the existing preview available for the same-token retry. */ }
      }
    } finally { pending.current = false; if (alive.current) setBusy(false); }
  }
  function keys(event: KeyboardEvent<HTMLElement>) {
    if (event.key === 'Escape' && !busy) { event.preventDefault(); onClose(); }
    if (event.key !== 'Tab' || !dialog.current) return;
    const elements = [...dialog.current.querySelectorAll<HTMLElement>('button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex="0"]')];
    const first = elements[0], last = elements[elements.length - 1];
    if (!first) { event.preventDefault(); return; }
    if (event.shiftKey && (document.activeElement === first || document.activeElement === dialog.current)) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  }
  const comparison = preview?.comparison;
  return createPortal(<div className="temporary-ltr-modal">
    <section role="dialog" aria-modal="true" aria-labelledby="temporary-ltr-title" aria-describedby="temporary-ltr-description"
      ref={dialog} tabIndex={-1} onKeyDown={keys} className="temporary-ltr-dialog" aria-busy={busy}>
      <h2 id="temporary-ltr-title">Apply LTR Number</h2>
      <p id="temporary-ltr-description">Register this project and keep its Matrix, fees and source materials.</p>
      {!preparation && !error ? <p role="status">Loading registration information…</p> : null}
      {preparation ? <>
        <div className="temporary-ltr-fields">
          {Object.entries(preparation.required_fields).map(([key, label]) => <label key={key}>
            <span>{label}</span>
            {key === 'project_type' || key === 'lab_performing_tests' ? <select value={values[key] ?? ''} disabled={busy || recovery}
              onChange={event => edit(key, event.target.value)}>
              <option value="">Select…</option>
              {(key === 'project_type' ? projectTypes : ['Dongguan', 'Valley Green']).map(item => <option key={item}>{item}</option>)}
            </select> : <input value={values[key] ?? ''} disabled={busy || recovery} onChange={event => edit(key, event.target.value)} />}
          </label>)}
        </div>
        <fieldset disabled={busy || recovery} className="temporary-ltr-number-mode">
          <legend>LTR number</legend>
          <label><input type="radio" name="temporary-ltr-mode" checked={mode === 'auto'} onChange={() => { setMode('auto'); setPreview(null); }} />Auto assign next LTR number</label>
          <label><input type="radio" name="temporary-ltr-mode" checked={mode === 'specified'} onChange={() => { setMode('specified'); setPreview(null); }} />Use specified LTR number</label>
          {mode === 'specified' ? <label>Specified LTR number<input value={number} onChange={event => { setNumber(event.target.value); setPreview(null); }} placeholder="DL-YYYY-MM-NNN or associated number" /></label> : null}
        </fieldset>
      </> : null}
      {preview ? <section className="temporary-ltr-preview" aria-label="Registration preview">
        <h3>{preview.ltr_number}</h3>
        <p>LTR workbook: {preview.workbook_path.split(/[\\/]/).pop()}</p>
        {recovery ? <p>Check and continue the pending registration. The saved workbook row will be verified before continuing.</p> : null}
        <p>{preview.action === 'replace_existing' ? 'The existing workbook row will be replaced after confirmation.' : preview.action === 'append_associated' ? 'A new associated row will be added. The base row stays unchanged.' : 'A new LTR row will be added after confirmation.'}</p>
        <div className="temporary-ltr-preview-scroll"><table aria-label="LTR registration comparison">
          <thead><tr><th>Field</th>{comparison ? <th>{preview.action === 'replace_existing' ? 'Existing row — will be replaced' : `Existing base — ${comparison.related_ltr_number} (reference only)`}</th> : null}<th>Proposed row</th></tr></thead>
          <tbody>{comparison ? comparison.proposed_row_values.map((field, index) => <tr key={field.field_name}>
            <th scope="row">{field.label}</th><td>{String(comparison.row_values[index]?.value ?? '')}</td><td>{String(field.value ?? '')}</td>
          </tr>) : preview.row.map((value, index) => index === 1 ? null : <tr key={index}><th scope="row">{rowLabels[index]}</th><td>{String(value ?? '')}</td></tr>)}</tbody>
        </table></div>
      </section> : null}
      {error ? <p className="temporary-ltr-error" role="alert">{error}</p> : null}
      <footer>
        <button type="button" onClick={onClose} disabled={busy}>Cancel</button>
        {preparation?.registered_ltr_number ? <button type="button" disabled={busy} onClick={() => {
          if (pending.current) return;
          pending.current = true; setBusy(true);
          void Promise.resolve().then(onRegistered).catch(err => { if (alive.current) setError(err instanceof Error ? err.message : 'Could not refresh the registered project.'); })
            .finally(() => { pending.current = false; if (alive.current) setBusy(false); });
        }}>Refresh project</button> : null}
        {preparation && !preparation.registered_ltr_number ? preview ? <button type="button" disabled={busy} onClick={() => void confirm()}>
          {busy ? 'Applying…' : recovery ? 'Continue registration' : 'Confirm registration'}
        </button> : <button type="button" disabled={busy} onClick={() => void runPreview()}>{busy ? 'Preparing…' : 'Preview registration'}</button> : null}
      </footer>
    </section>
  </div>, document.body);
}
