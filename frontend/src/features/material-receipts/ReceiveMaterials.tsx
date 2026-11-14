import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import * as api from "../../api/materialReceipts";
import { ApiRequestError } from "../../api/client";
import type { ReferenceProject } from "../../api/referenceLibrary";
import type { ReceiptBatch, ReceiptCandidate, ReceiptInput, ReceiptPlan, ReceiptRuntime } from "../../api/materialReceipts";
import "./materials.css";

const pendingKey = "materials-pending-receipt";
const labels: Record<string, string> = { copy: "New", skip: "Skip identical", supplement: "Save supplementary copy", copied: "Copied", skipped: "Skipped", supplemented: "Saved supplementary copy", failed: "Failed", retained_changed: "Changed after receipt — retained" };
const readPending = (): ReceiptPlan | null => { try { return JSON.parse(sessionStorage.getItem(pendingKey) ?? "null"); } catch { return null; } };
export function ReceiptResults({ batch }: { batch: ReceiptBatch }) {
 return <section aria-label="Receipt result">
  <p role="status">{batch.status === "completed" ? "Materials received and verified." : "Receipt incomplete. Review the items below; existing files are retained."}</p>
  {batch.message && <p role="alert">{batch.message}</p>}
  <p>New {batch.counts.copied ?? 0} · Skipped {batch.counts.skipped ?? 0} · Supplementary {batch.counts.supplemented ?? 0} · Failed {batch.counts.failed ?? 0} · Changed after receipt {batch.counts.retained_changed ?? 0}</p>
  {Object.values(batch.directory_counts ?? {}).some(Boolean) && <p>Directories: {Object.entries(batch.directory_counts).map(([key, count]) => labels[key] + " " + count).join(" · ")}</p>}
  <p className="materials-path">Managed location: {batch.target_path}</p>
  <details><summary>Receipt details</summary><ul className="materials-items">{batch.items.map(row => <li key={row.relative_path}><strong>{row.relative_path}{row.directory ? " (folder)" : ""}</strong><span>{labels[row.status ?? ""] ?? row.status}</span><span>{row.target_relative}</span>{row.message && <span>{row.message}</span>}</li>)}</ul></details>
 </section>;
}
export function ReceiveMaterials({ onClose, onReceived, initialTarget }: { onClose: () => void; onReceived: (key: string) => void; initialTarget?: ReferenceProject | null }) {
 const [runtime, setRuntime] = useState<ReceiptRuntime | null>(null);
 const [root, setRoot] = useState("");
 const [form, setForm] = useState<ReceiptInput>({ source: "", number: initialTarget?.number ?? "", product_name: initialTarget?.title ?? "", test_keywords: initialTarget?.test_item ?? "", target_key: initialTarget?.key ?? "", separate_description: "", material_state: initialTarget?.material_state ?? null });
 const [plan, setPlan] = useState<ReceiptPlan | null>(null);
 const [candidates, setCandidates] = useState<ReceiptCandidate[]>([]);
 const [batch, setBatch] = useState<ReceiptBatch | null>(null);
 const [pending, setPending] = useState<ReceiptPlan | null>(null);
 const [missingBatch, setMissingBatch] = useState(false);
 const [busy, setBusy] = useState(false);
 const [error, setError] = useState("");
 const live = useRef(true);
 const title = useRef<HTMLHeadingElement>(null);
 useEffect(() => {
  live.current = true; const previous = document.activeElement as HTMLElement | null; title.current?.focus();
  void api.getReceiptRuntime().then(value => { if (live.current) { setRuntime(value); setRoot(value.root_path); } }).catch(cause => { if (live.current) setError((cause as Error).message); });
  const unfinished = readPending();
  if (unfinished?.batch_id) { setPending(unfinished); void api.getReceiptBatch(unfinished.batch_id).then(value => { if (live.current) finish(value); }).catch(() => { if (live.current) setError("A previous receipt has no confirmed result. Retry that receipt before starting another."); }); }
  return () => { live.current = false; previous?.focus(); };
 }, []);
 function finish(value: ReceiptBatch) { setBatch(value); if (value.status === "completed") { sessionStorage.removeItem(pendingKey); setPending(null); } }
 async function act(action: () => Promise<void>) { setBusy(true); setError(""); try { await action(); } catch (cause) { if (live.current) setError((cause as Error).message); } finally { if (live.current) setBusy(false); } }
 function update<K extends keyof ReceiptInput>(key: K, value: ReceiptInput[K]) {
  setForm(current => ({ ...current, [key]: value, ...(["source", "number"].includes(key) ? { target_key: initialTarget?.key ?? "", separate_description: "" } : {}) }));
  if (key === "source" || key === "number") setCandidates([]);
  setPlan(null);
 }
 async function chooseSource() {
  const source = await api.pickReceiptFolder(); if (!source || !live.current) return;
  const name = source.replaceAll("\\", "/").split("/").filter(Boolean).at(-1) ?? "";
  setForm(current => ({ ...current, source, number: initialTarget ? current.number : current.number || name.match(/DL-\d{4}-\d{2}-\d{3}[A-Z0-9]*/i)?.[0] || "", product_name: current.product_name || name, target_key: initialTarget?.key ?? "", separate_description: "" }));
  setPlan(null); setCandidates([]);
 }
 async function review() { const next = await api.previewReceipt(form); if (!live.current) return; setPlan(next); setCandidates(next.candidates ?? []); }
 async function confirm(value: ReceiptPlan) {
  setMissingBatch(false);
  sessionStorage.setItem(pendingKey, JSON.stringify(value)); setPending(value);
  const result = await api.confirmReceipt(value); if (live.current) finish(result);
 }
 const locked = busy || Boolean(pending || batch);
 const counts = (plan?.items ?? []).filter(row => !row.directory).reduce<Record<string, number>>((value, row) => ({ ...value, [row.action]: (value[row.action] ?? 0) + 1 }), {});
 return createPortal(<div className="materials-overlay"><section className="materials-dialog" role="dialog" aria-modal="true" aria-labelledby="receive-materials-title">
  <header><h2 id="receive-materials-title" ref={title} tabIndex={-1}>Receive project materials</h2><button disabled={busy} onClick={onClose}>Close</button></header>
  {error && <p role="alert">{error}</p>}
  {busy && <p role="status">Working…</p>}
  {!batch && !pending && <>
   <fieldset disabled={locked}><legend>Receive save location</legend>
    <div className="materials-inline"><input aria-label="Receive save location" value={root} onChange={event => { setRoot(event.target.value); setPlan(null); }} /><button onClick={() => void act(async () => { const value = await api.pickReceiptFolder(); if (value && live.current) { setRoot(value); setPlan(null); } })}>Choose save location</button><button disabled={!root} onClick={() => void act(async () => { const value = await api.setReceiptDestination(root); if (live.current) { setRuntime(value); setRoot(value.root_path); setPlan(null); } })}>Use save location</button></div>
    {runtime && !runtime.available && <p>Choose an available location for received copies. The Projects save setting is separate.</p>}
   </fieldset>
   {initialTarget && <p className="materials-path">Supplementing: {initialTarget.number || "No number"} · {initialTarget.title} — {initialTarget.folder_path}</p>}
   <fieldset disabled={locked}><legend>Source and materials information</legend>
    <label>Source folder<div className="materials-inline"><input aria-label="Source folder" value={form.source} onChange={event => update("source", event.target.value)} /><button onClick={() => void act(chooseSource)}>Choose source folder</button></div></label>
    <div className="materials-fields"><label>Project number<input readOnly={Boolean(initialTarget)} value={form.number} onChange={event => update("number", event.target.value)} /></label><label>Product name<input value={form.product_name} onChange={event => update("product_name", event.target.value)} /></label><label>Test items<input value={form.test_keywords} onChange={event => update("test_keywords", event.target.value)} /></label><label>Declared project state<select value={form.material_state ?? ""} onChange={event => update("material_state", event.target.value || null)}><option value="">Manual project: default Completed</option><option value="completed">Completed</option><option value="ongoing">On-going</option></select></label></div>
    <label>Distinguishing description<input value={form.separate_description} onChange={event => update("separate_description", event.target.value)} /></label>
    <p className="materials-help">The number is retained as entered. LTR availability does not block receipt. Product and test items are search information; no execution data is restored.</p>
   </fieldset>
   {candidates.length > 0 && <fieldset disabled={locked}><legend>Same-number materials — choose the destination</legend>
    <label className="materials-radio"><input type="radio" name="target" checked={form.target_key === "new"} onChange={() => update("target_key", "new")} />Keep an independent materials entry</label>
    {candidates.map(row => <label className="materials-candidate" key={row.key}><input type="radio" name="target" checked={form.target_key === row.key} disabled={!row.can_supplement} onChange={() => update("target_key", row.key)} /><span><strong>{row.number} · {row.title}</strong><span className="materials-path">{row.folder_path}</span>{row.reason && <span>{row.reason}</span>}</span></label>)}
   </fieldset>}
   {plan?.message && <p role="status">{plan.message}</p>}
   {plan?.status === "choose_target" && <p role="status">Choose an existing managed project to supplement, or keep a clearly distinguished independent entry.</p>}
   {plan?.status === "choose_state" && <p role="status">Choose Completed or On-going explicitly, then review again.</p>}
   <div className="materials-actions"><button disabled={locked || !form.source || !runtime?.available || root !== runtime.root_path} onClick={() => void act(review)}>Review receipt</button></div>
   {plan?.status === "ready" && <section className="materials-review" aria-label="Receipt confirmation"><h3>Confirm receipt</h3><p>Not received yet. Your source folder will remain unchanged.</p><p className="materials-path">Planned location: {plan.target_path}</p>{plan.supplement && <p>Only files will be added. Existing project information, Matrix and progress remain unchanged.</p>}<p>New {counts.copy ?? 0} · Skip identical {counts.skip ?? 0} · Supplementary {counts.supplement ?? 0}</p>
    {(counts.supplement ?? 0) > 0 && <p className="materials-path">Incoming conflict copy: {plan.items?.find(row => row.action === "supplement" && !row.directory)?.target_relative}. Existing files are retained.</p>}
    <details><summary>File differences</summary><ul className="materials-items">{plan.items?.map(row => <li key={row.relative_path}><strong>{row.relative_path}{row.directory ? " (folder)" : ""}</strong><span>{labels[row.action] ?? row.action}</span><span>{row.target_relative}</span>{row.reason && <span>{row.reason}</span>}</li>)}</ul></details>
    <button disabled={busy} onClick={() => void act(() => confirm(plan))}>Confirm receipt</button>
   </section>}
  </>}
  {pending && !batch && <section><p>A receipt is awaiting a confirmed result. Retrying uses the same operation.</p><div className="materials-actions"><button disabled={busy} onClick={() => void act(() => confirm(pending))}>Retry confirmed receipt</button><button disabled={busy || !pending.batch_id} onClick={() => void act(async () => { try { finish(await api.getReceiptBatch(pending.batch_id!)); } catch (cause) { if (cause instanceof ApiRequestError && cause.status === 404) { setMissingBatch(true); } else throw cause; } })}>Check receipt result</button>{missingBatch && <button disabled={busy} onClick={() => { sessionStorage.removeItem(pendingKey); setPending(null); setPlan(null); setMissingBatch(false); }}>Review source again</button>}</div></section>}
  {batch && <><ReceiptResults batch={batch} /><div className="materials-actions">{batch.status !== "completed" && <button disabled={busy} onClick={() => void act(async () => { const value = await api.retryReceipt(batch.batch_id); if (live.current) finish(value); })}>Retry incomplete receipt</button>}<button disabled={busy || batch.status === "running" || (batch.target_key.startsWith("receipt:") && !batch.receipt_id)} onClick={() => { sessionStorage.removeItem(pendingKey); setPending(null); onReceived(batch.target_key); }}>Open project materials</button>{batch.status === "incomplete" && <button disabled={busy} onClick={() => { sessionStorage.removeItem(pendingKey); setPending(null); setBatch(null); setPlan(null); }}>Keep result and review again</button>}</div></>}
 </section></div>, document.body);
}
