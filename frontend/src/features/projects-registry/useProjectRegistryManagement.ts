import { useEffect, useRef, useState } from "react";
import { ApiRequestError } from "../../api/client";
import {
  moveProjectToTrash, previewProjectRegistryAction, restoreManagedProject,
  type ProjectRegistryAction, type ProjectRegistryEntry, type ProjectRegistryPreview,
} from "../../api/projectRegistryManagement";

type Target = {projectId: string; action: ProjectRegistryAction};

export function useProjectRegistryManagement(viewKey: string, onChanged: () => void) {
  const [target, setTarget] = useState<Target | null>(null);
  const [preview, setPreview] = useState<ProjectRegistryPreview | null>(null);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stale, setStale] = useState(false);
  const [lastChange, setLastChange] = useState<ProjectRegistryEntry | null>(null);
  const epoch = useRef(0);
  const submitLock = useRef(false);
  const mounted = useRef(true);
  const onChangedRef = useRef(onChanged);
  onChangedRef.current = onChanged;
  useEffect(() => {mounted.current = true; return () => {mounted.current = false; epoch.current += 1;};}, []);
  useEffect(() => {
    epoch.current += 1;
    setTarget(null); setPreview(null); setLoading(false); setError(null); setStale(false);
  }, [viewKey]);

  async function open(projectId: string, action: ProjectRegistryAction): Promise<void> {
    const request = ++epoch.current;
    setTarget({projectId, action}); setPreview(null); setLoading(true); setError(null); setStale(false);
    try {
      const result = await previewProjectRegistryAction(projectId, action);
      if (request === epoch.current && mounted.current) setPreview(result);
    } catch {
      if (request === epoch.current && mounted.current) setError("Could not load this project's management preview. Refresh and try again.");
    } finally {if (request === epoch.current && mounted.current) setLoading(false);}
  }
  function dismiss(): void {
    if (submitLock.current) return;
    epoch.current += 1; setTarget(null); setPreview(null); setError(null); setStale(false);
  }
  async function refresh(): Promise<void> {if (target) await open(target.projectId, target.action);}
  async function submit(operation: (current: ProjectRegistryPreview) => Promise<ProjectRegistryEntry>): Promise<void> {
    if (!preview || loading || stale || preview.blockers.length || submitLock.current) return;
    const request = epoch.current;
    submitLock.current = true; setBusy(true); setError(null);
    try {
      const result = await operation(preview);
      if (mounted.current) onChangedRef.current();
      if (request === epoch.current && mounted.current) {
        setLastChange(result); setTarget(null); setPreview(null);
      }
    } catch (failure) {
      if (request === epoch.current && mounted.current) {
        const changed = failure instanceof ApiRequestError && failure.status === 409;
        setStale(changed);
        setError(changed
          ? "This project or its conflicts changed. Refresh the preview and confirm again. No partial change was applied."
          : "The operation could not be confirmed. Refresh the preview before trying again.");
        // A lost response may hide a completed transition. A fresh token is required before retrying.
        if (!changed) setStale(true);
      }
    } finally {submitLock.current = false; if (mounted.current) setBusy(false);}
  }
  async function trash(reason: string): Promise<void> {
    if (!reason.trim() || preview?.action !== "trash") return;
    await submit((current) => moveProjectToTrash(current.project.project_id, {token: current.token, reason: reason.trim()}));
  }
  async function restore(destination: "active" | "history", replaceConflicts = false): Promise<void> {
    if (preview?.action !== "restore") return;
    await submit((current) => restoreManagedProject(current.project.project_id, {
      token: current.token, destination, replace_conflicts: replaceConflicts,
    }));
  }
  return {target, preview, loading, busy, error, stale, lastChange, open, dismiss, refresh, trash, restore,
    clearLastChange: () => setLastChange(null)};
}
