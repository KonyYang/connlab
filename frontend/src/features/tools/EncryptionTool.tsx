import { useCallback, useEffect, useId, useLayoutEffect, useRef, useState, type KeyboardEvent } from "react";
import { createPortal } from "react-dom";
import { encryptLocalFile, encryptLocalFolder, type LocalFolderEncryptionResult } from "../../api/client";
import { UiIcon } from "../../components/common/UiIcon";
import { runtimeLocalStorage } from "../../runtimeEnvironment";
import { ToolsFeedback } from "./ToolsFeedback";

type EncryptionMode = "file" | "folder";
const recentModeKey = "tools.encryption.recent-mode";

function readRecentMode(): EncryptionMode {
  try {
    return runtimeLocalStorage.getItem(recentModeKey) === "folder" ? "folder" : "file";
  } catch {
    return "file";
  }
}

function EncryptionOptions({ id, anchor, trigger, onClose, onChoose }: {
  id: string;
  anchor: HTMLDivElement;
  trigger: HTMLButtonElement;
  onClose: () => void;
  onChoose: (mode: EncryptionMode) => void;
}) {
  const menuRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const menu = menuRef.current;
    if (!menu) return;

    function position() {
      if (!menu) return;
      const anchorBounds = anchor.getBoundingClientRect();
      const gutter = 8;
      const gap = 4;
      const width = Math.min(Math.max(anchorBounds.width, 210), window.innerWidth - 2 * gutter);
      menu.style.width = `${width}px`;
      const left = Math.max(gutter, Math.min(anchorBounds.right, window.innerWidth - gutter) - width);
      const below = window.innerHeight - anchorBounds.bottom - gutter - gap;
      const above = anchorBounds.top - gutter - gap;
      const height = menu.offsetHeight;
      const y = height > below && above > below ? anchorBounds.top - gap - height : anchorBounds.bottom + gap;
      menu.style.left = `${left}px`;
      menu.style.top = `${Math.max(gutter, Math.min(y, window.innerHeight - height - gutter))}px`;
    }

    function dismissOutside(event: PointerEvent) {
      if (event.target instanceof Node && !anchor.contains(event.target) && !menu?.contains(event.target)) onClose();
    }

    position();
    menu.querySelector<HTMLButtonElement>("button")?.focus();
    window.addEventListener("resize", position);
    window.addEventListener("scroll", position, true);
    document.addEventListener("pointerdown", dismissOutside);
    return () => {
      window.removeEventListener("resize", position);
      window.removeEventListener("scroll", position, true);
      document.removeEventListener("pointerdown", dismissOutside);
    };
  }, [anchor, onClose]);

  function handleMenuKey(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Escape" || event.key === "Tab") {
      if (event.key === "Escape") event.preventDefault();
      trigger.focus();
      onClose();
      return;
    }
    if (!["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) return;
    const items = Array.from(event.currentTarget.querySelectorAll("button"));
    const current = items.indexOf(document.activeElement as HTMLButtonElement);
    const last = items.length - 1;
    const next = event.key === "Home" ? 0 : event.key === "End" ? last : current === 0 ? last : 0;
    event.preventDefault();
    items[next]?.focus();
  }

  return createPortal(<div id={id} ref={menuRef} role="menu" aria-label="Encryption options"
    className="tools-encryption-menu" onKeyDown={handleMenuKey}>
    <button type="button" role="menuitem" tabIndex={-1} onClick={() => onChoose("file")}>
      <UiIcon name="file" /><span>Encrypt one file…</span>
    </button>
    <button type="button" role="menuitem" tabIndex={-1} onClick={() => onChoose("folder")}>
      <UiIcon name="folder" /><span>Encrypt a folder…<small>Excludes subfolders</small></span>
    </button>
  </div>, document.body);
}

export function EncryptionTool() {
  const active = useRef(false);
  const generation = useRef(0);
  const choicesId = useId();
  const split = useRef<HTMLDivElement>(null);
  const optionsButton = useRef<HTMLButtonElement>(null);
  const mainButton = useRef<HTMLButtonElement>(null);
  const restoreFocus = useRef<HTMLButtonElement | null>(null);
  const [recentMode, setRecentMode] = useState(readRecentMode);
  const [expanded, setExpanded] = useState(false);
  const closeOptions = useCallback(() => setExpanded(false), []);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Extract<LocalFolderEncryptionResult, { cancelled: false }> | null>(null);
  const [resultMode, setResultMode] = useState<EncryptionMode | null>(null);

  useEffect(() => () => { generation.current += 1; }, []);

  useLayoutEffect(() => {
    if (busy || !restoreFocus.current) return;
    if (document.activeElement === document.body) restoreFocus.current.focus();
    restoreFocus.current = null;
  }, [busy]);

  async function run(mode: EncryptionMode, trigger: HTMLButtonElement | null) {
    if (active.current) return;
    active.current = true;
    restoreFocus.current = trigger;
    closeOptions();
    const token = ++generation.current;
    setBusy(true);
    try {
      const response = await (mode === "file" ? encryptLocalFile() : encryptLocalFolder());
      if (generation.current === token && !response.cancelled) {
        setResult(response);
        setResultMode(mode);
        setError(null);
        setRecentMode(mode);
        try {
          runtimeLocalStorage.setItem(recentModeKey, mode);
        } catch {
          // Browser storage is optional. Keep the last mode for this visit.
        }
      }
    } catch (reason) {
      if (generation.current === token) {
        setError(reason instanceof Error ? reason.message : "Encryption failed. Select the source and retry.");
        setResult(null);
      }
    } finally {
      if (generation.current === token) { active.current = false; setBusy(false); }
    }
  }

  const saved = result?.entries.find(entry => entry.status === "Encrypted");
  return <article className="tools-action-group" aria-label="Encrypt a Copy" aria-busy={busy}>
    <div className="tools-encryption-split" ref={split}>
      <button ref={mainButton} className="primary-action tools-picker-action" type="button" disabled={busy}
        title="Encrypted copies are saved beside the originals."
        onClick={() => void run(recentMode, mainButton.current)}>
        {busy ? "Working..." : recentMode === "file" ? "Encrypt File" : "Encrypt Folder"}
      </button>
      <button ref={optionsButton} className="primary-action tools-encryption-toggle" type="button" disabled={busy}
        aria-label="Encryption options" aria-haspopup="menu" aria-expanded={expanded}
        aria-controls={expanded ? choicesId : undefined} onClick={() => setExpanded(open => !open)}
        onKeyDown={event => {
          if (event.key === "ArrowDown") { event.preventDefault(); setExpanded(true); }
        }}>
        <UiIcon name="chevron-down" />
      </button>
    </div>
    {expanded && split.current && optionsButton.current && <EncryptionOptions id={choicesId}
      anchor={split.current} trigger={optionsButton.current} onClose={closeOptions}
      onChoose={mode => void run(mode, optionsButton.current)} />}
    {(error || result) && <ToolsFeedback><div className="tools-action-feedback">
      {error ? <p role="alert" className="tools-feedback tools-feedback-error">{error}</p> : null}
      {result ? <div className="tools-folder-selection" role={resultMode === "folder" ? "status" : undefined}>
        {resultMode === "file" && saved ? <p role="status" aria-label="Saved Encrypted File" className="tools-feedback tools-feedback-success">
          Saved: {saved.output}
        </p> : <p className={result.summary.failed ? "tools-feedback tools-feedback-warning" : "tools-feedback tools-feedback-success"}>
          {result.summary.succeeded === 0 ? "No files were encrypted. " : ""}
          {result.summary.succeeded} encrypted · {result.summary.failed} failed · {result.summary.skipped} skipped.
        </p>}
        <p className="tools-feedback" title={result.folder}>{result.folder}</p>
      </div> : null}
    </div></ToolsFeedback>}
  </article>;
}
