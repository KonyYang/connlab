import { useEffect, useRef, useState } from "react";
import { getReceiptRuntime, pickReceiptFolder, setReceiptDestination, type ReceiptRuntime } from "../../api/materialReceipts";

export function ReceiveSaveLocation() {
  const [runtime, setRuntime] = useState<ReceiptRuntime | null>(null);
  const [path, setPath] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [reload, setReload] = useState(0);
  const live = useRef(false);
  const working = useRef(false);
  useEffect(() => {
    live.current = true;
    let current = true;
    setLoading(true);
    setError("");
    void getReceiptRuntime().then(value => {
      if (current) { setRuntime(value); setPath(value.root_path); }
    }).catch(cause => { if (current) setError((cause as Error).message); })
      .finally(() => { if (current) setLoading(false); });
    return () => { current = false; live.current = false; };
  }, [reload]);

  async function save(value: string) {
    const next = value.trim();
    if (!next) { setError("Choose an existing folder for received materials."); return; }
    if (working.current || next === runtime?.root_path && runtime.available) return;
    working.current = true; setBusy(true); setError("");
    try {
      const result = await setReceiptDestination(next);
      if (live.current) { setRuntime(result); setPath(result.root_path); }
    } catch (cause) { if (live.current) setError((cause as Error).message); }
    finally { working.current = false; if (live.current) setBusy(false); }
  }
  async function browse() {
    if (working.current) return;
    working.current = true; setBusy(true); setError("");
    let chosen: string | null = null;
    try { chosen = await pickReceiptFolder(); }
    catch (cause) { if (live.current) setError((cause as Error).message); }
    finally { working.current = false; if (live.current) setBusy(false); }
    if (chosen && live.current) { setPath(chosen); await save(chosen); }
  }
  const unavailable = !loading && runtime && !runtime.available;
  const message = error || (unavailable ? "Choose an available Receive save location." : "");
  return <article className="settings-resource-row settings-receive-location">
    <div className="settings-resource-label"><strong>Receive save location</strong></div>
    <div className="settings-path-field">
      <div className="settings-path-control">
        <input aria-label="Receive save location path" className={"settings-path-input" + (message ? " is-invalid-path" : "")}
          aria-invalid={Boolean(message)} title={message || "Receive save location"} placeholder="Paste path"
          value={path} disabled={loading || busy}
          onChange={event => { setPath(event.target.value); setError(""); }}
          onBlur={() => void save(path)}
          onKeyDown={event => { if (event.key === "Enter") { event.preventDefault(); void save(path); } }} />
        <button className="ui-tertiary-action" disabled={loading || busy} onClick={() => void browse()}>Browse folder</button>
      </div>
      {message && <span role="alert">{message}</span>}
      {!runtime && !loading && <button className="ui-tertiary-action" disabled={busy} onClick={() => setReload(value => value + 1)}>Retry receive location</button>}
    </div>
  </article>;
}
