import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from 'react';
import type { TemperatureToolState } from './useTemperatureTool';
import type { GridEditingState } from './useDataGridEditing';
import type { ReportInfoFields } from './reportInfo';
import { clearTemperatureWorkspace, readTemperatureWorkspace, writeTemperatureWorkspace } from './temperatureWorkspaceStorage';
import { ClearWorkspaceDialog } from './ClearWorkspaceDialog';

export type TemperatureWorkspaceDraft = {
  version: 1;
  tool: TemperatureToolState;
  report: Partial<ReportInfoFields>;
  grid: { key: string; state: GridEditingState } | null;
  preview?: { key: string; scrollTop: number; scrollLeft: number; activeRow: number | null };
  correction?: { key: string; rows: { header_row: string; start_row: string; end_row: string }; page: number };
  stageResultsOpen?: boolean;
};
type Workspace = {
  initial: TemperatureWorkspaceDraft | null;
  update: (patch: Partial<TemperatureWorkspaceDraft>) => void;
  requestExit: (beforeClear?: () => void) => void;
  clearing: boolean;
};
const Context = createContext<Workspace | null>(null);
// Survives route unmount: a rapid return must wait for the departing page's final write.
let workspaceWrites: Promise<void> = Promise.resolve();
export const useTemperatureWorkspace = () => useContext(Context);

export function TemperatureWorkspace({ children, onBack }: { children: ReactNode; onBack: () => void }) {
  const [loaded, setLoaded] = useState<{ draft: TemperatureWorkspaceDraft | null } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [clearing, setClearing] = useState(false);
  const [exitRequested, setExitRequested] = useState(false);
  const beforeClear = useRef<(() => void) | undefined>(undefined);
  const current = useRef<TemperatureWorkspaceDraft | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const paused = useRef(false);
  const mounted = useRef(true);
  const revision = useRef(0);
  const load = useCallback(async () => {
    setError(null);
    try {
      await workspaceWrites.catch(() => undefined);
      const draft = await readTemperatureWorkspace();
      if (!mounted.current) return;
      const restored = draft ? { ...draft, tool: { ...draft.tool, busy: null,
        error: draft.tool.busy ? 'The previous operation was interrupted. Retry it to continue.' : draft.tool.error } } : null;
      current.current = restored;
      setLoaded({ draft: restored });
    } catch {
      if (mounted.current) setError('Could not restore the workspace. Retry; your saved draft has not been cleared.');
    }
  }, []);
  const flush = useCallback(() => {
    if (timer.current !== null) clearTimeout(timer.current);
    timer.current = null;
    if (paused.current || !current.current) return;
    const snapshot = current.current;
    const token = revision.current;
    // Queue writes, including final unmount/pagehide writes, before any destructive clear.
    workspaceWrites = workspaceWrites.catch(() => undefined).then(() => writeTemperatureWorkspace(snapshot));
    void workspaceWrites.then(() => {
      if (mounted.current && token === revision.current) setError(null);
    }, () => {
      if (mounted.current && token === revision.current) setError('Could not save the workspace on this computer. Retry before closing the software.');
    });
  }, []);
  const update = useCallback((patch: Partial<TemperatureWorkspaceDraft>) => {
    if (paused.current) return;
    current.current = { version: 1, report: {}, grid: null, ...current.current, ...patch } as TemperatureWorkspaceDraft;
    revision.current += 1;
    if (timer.current !== null) clearTimeout(timer.current);
    timer.current = setTimeout(flush, 200);
  }, [flush]);
  useEffect(() => {
    mounted.current = true;
    void load();
    const hide = () => { if (document.visibilityState === 'hidden') flush(); };
    window.addEventListener('pagehide', flush);
    document.addEventListener('visibilitychange', hide);
    return () => {
      mounted.current = false;
      flush();
      window.removeEventListener('pagehide', flush);
      document.removeEventListener('visibilitychange', hide);
    };
  }, [load, flush]);
  async function clear() {
    paused.current = true;
    setClearing(true);
    if (timer.current !== null) clearTimeout(timer.current);
    timer.current = null;
    try {
      await workspaceWrites.catch(() => undefined);
      await clearTemperatureWorkspace();
      current.current = null;
      return true;
    } catch {
      paused.current = false;
      setError('Could not clear the workspace. Your current data is still available. Retry.');
      return false;
    } finally {
      if (mounted.current) setClearing(false);
    }
  }
  function requestExit(cancelPending?: () => void) {
    beforeClear.current = cancelPending;
    setExitRequested(true);
  }
  async function confirmExit() {
    beforeClear.current?.();
    if (await clear()) onBack();
    if (mounted.current) setExitRequested(false);
  }
  return <>
    {!loaded && !error && <p role="status">Restoring workspace…</p>}
    {error && <div role="alert" className="temperature-error">{error}{' '}
      <button type="button" disabled={clearing} onClick={() => loaded ? flush() : void load()}>Retry</button>
      {!loaded && <button type="button" disabled={clearing} onClick={() => requestExit()}>Back To Tools</button>}</div>}
    {loaded && <Context.Provider value={{ initial: loaded.draft, update, requestExit, clearing }}>{children}</Context.Provider>}
    {exitRequested && <ClearWorkspaceDialog busy={clearing} onCancel={() => setExitRequested(false)} onConfirm={() => void confirmExit()} />}
  </>;
}
