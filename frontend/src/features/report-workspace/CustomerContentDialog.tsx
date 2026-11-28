import {useEffect, useId, useRef, useState} from 'react';
import type {CustomerDecisionField, CustomerDecisions, CustomerInspection} from '../../api/customerContent';
import './customerContentDialog.css';

function applies(field: CustomerDecisionField, choices: CustomerDecisions) {
  return !field.depends_on || choices[field.depends_on] !== 'omit';
}
export function confirmedChoices(inspection: CustomerInspection, choices: CustomerDecisions): CustomerDecisions | null {
  const result: CustomerDecisions = {};
  for (const field of inspection.fields.filter(f => applies(f, choices))) {
    const value = choices[field.id]?.trim();
    if (!value || value.length > 180 || /[\u0000-\u001f\u007f]/.test(value) || (field.kind === 'sample' && !['keep','omit'].includes(value)) ||
      (field.kind === 'temperature' && !field.options?.some(o => o.value === value))) return null;
    result[field.id] = value;
  }
  return result;
}

export function CustomerContentDialog({inspection, name, onGenerate, onCancel}: {
  inspection: CustomerInspection; name: string; onGenerate: (decisions: CustomerDecisions) => void; onCancel: () => void;
}) {
  const [choices, setChoices] = useState<CustomerDecisions>({...inspection.decisions});
  const update = (id: string, value: string) => setChoices(previous => ({...previous, [id]: value}));
  const samples = inspection.fields.filter(f => f.kind === 'sample');
  const valid = confirmedChoices(inspection, choices);
  const dialog = useRef<HTMLDivElement>(null);
  const title = useId();
  useEffect(() => {
    const previous = document.activeElement;
    dialog.current?.focus();
    return () => { if (previous instanceof HTMLElement && previous.isConnected) previous.focus(); };
  }, []);
  return <div className="customer-content-backdrop"><div className="customer-content-dialog" role="dialog" aria-modal="true" aria-labelledby={title} tabIndex={-1} ref={dialog}
    onKeyDown={e => {
      if (e.key === 'Escape') onCancel();
      if (e.key !== 'Tab') return;
      const items = Array.from(e.currentTarget.querySelectorAll<HTMLElement>('input:not(:disabled), select, button:not(:disabled), summary'));
      if (e.shiftKey && (document.activeElement === items[0] || document.activeElement === dialog.current)) { e.preventDefault(); items.at(-1)?.focus(); }
      if (!e.shiftKey && document.activeElement === items.at(-1)) { e.preventDefault(); items[0]?.focus(); }
    }}>
    <h2 id={title}>Customer report content</h2><p className="customer-content-source">{name}</p>
    {samples.length > 0 && <section><h3>Samples in the customer report</h3><p>Keep tested samples. Omit items used only for setup.</p>
      {samples.map(row => <fieldset key={row.id} className="customer-sample-choice"><legend>{row.label}{row.part_number && <small> · {row.part_number}</small>}</legend>
        {(['keep','omit'] as const).map(value => <label key={value}><input type="radio" name={title + row.id}
          checked={choices[row.id] === value} onChange={() => update(row.id,value)} />{value === 'keep' ? 'Keep' : 'Omit'}</label>)}
      </fieldset>)}</section>}
    {inspection.fields.filter(f => f.kind !== 'sample' && applies(f,choices)).map(f => <label key={f.id} className="customer-detail-choice">
      <strong>{f.label}</strong>{f.part_number && <span>{f.part_number}</span>}
      {f.kind === 'material' ? <>{f.value && <span>Internal material: {f.value}</span>}
        <input maxLength={180} value={choices[f.id] ?? ''} placeholder="Customer-facing material name" onChange={e => update(f.id,e.target.value)} /></>
        : <select value={choices[f.id] ?? ''} onChange={e => update(f.id,e.target.value)}>
          <option value="">Select the measured maximum</option>{f.options?.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}</select>}
    </label>)}
    <details className="customer-content-preview"><summary>Preview customer content</summary><section aria-label="Customer content preview">
      {inspection.samples.length > 0 && <table><caption>Sample description</caption><thead><tr>{['Description','Part number','Base material','Housing material'].map(h => <th key={h}>{h}</th>)}</tr></thead>
        <tbody>{inspection.samples.filter(r => !r.decision_id || choices[r.decision_id] === 'keep').map((r,i) => <tr key={i}><td>{r.description}</td><td>{r.part_number}</td>
          <td>{r.base_decision_id ? choices[r.base_decision_id] || 'Pending' : r.base_material}</td>
          <td>{r.housing_decision_id ? choices[r.housing_decision_id] || 'Pending' : r.housing_material}</td></tr>)}</tbody></table>}
      {inspection.temperatures.map((t,i) => {
        const selected = t.options?.find(o => o.value === choices[t.decision_id || '']);
        const rows = t.decision_id ? (selected ? selected.rows ?? [selected.cells] : []) : t.rows;
        return <table key={i}><caption>{t.label}</caption><thead><tr>{t.headers.map((h,j) => <th key={j}>{h}</th>)}</tr></thead>
          <tbody>{rows.map((row,k) => <tr key={k}>{row.map((v,j) => <td key={j}>{v}</td>)}</tr>)}</tbody></table>;
      })}</section></details>
    <footer><button type="button" className="ui-secondary-action" onClick={onCancel}>Cancel</button>
      <button type="button" className="ui-primary-action" disabled={!valid} onClick={() => valid && onGenerate(valid)}>Generate Word copy</button></footer>
  </div></div>;
}
