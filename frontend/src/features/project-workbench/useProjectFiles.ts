import { useEffect, useRef, useState } from "react";
import { previewProjectFiles, startProjectFiles, getProjectFilesOperation, resumeProjectFilesOperation,
  type ProjectFilesPreview, type ProjectFileOperation, type ProjectFileSelection } from "../../api/client";

export function useProjectFiles(projectId: string) {
  const [preview, setPreview] = useState<ProjectFilesPreview | null>(null);
  const [operation, setOperation] = useState<ProjectFileOperation | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const epoch = useRef(0);
  const project = useRef(projectId);
  if (project.current !== projectId) { project.current = projectId; epoch.current++; }
  const mounted = useRef(false);
  const changing = useRef(false);
  const request = useRef<{signature: string; id: string} | null>(null);
  const active = (token: number) => mounted.current && token === epoch.current && project.current === projectId;

  async function refresh() {
    const token = epoch.current;
    setLoading(true);
    try {
      const next = await previewProjectFiles(projectId);
      if (!active(token) || next.project_id !== projectId) return;
      setPreview(next); setOperation(next.operation); setError(null);
      if (next.operation?.status === "completed") request.current = null;
    } catch {
      if (active(token)) { setPreview(null); setError("Could not check project files. Check the connection and refresh before generating."); }
    } finally { if (active(token)) setLoading(false); }
  }
  useEffect(() => {
    mounted.current = true; changing.current = false; request.current = null;
    setPreview(null); setOperation(null); setError(null); setBusy(false);
    void refresh();
    return () => { mounted.current = false; epoch.current++; };
  }, [projectId]);

  const running = operation?.status === "queued" || operation?.status === "running";
  useEffect(() => {
    if (!operation || !running) return;
    const operationId = operation.operation_id;
    const token = epoch.current;
    let disposed = false;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try {
        const next = await getProjectFilesOperation(projectId, operationId);
        if (disposed || !active(token) || next.project_id !== projectId) return;
        setOperation(next); setError(null);
        if (next.status === "completed") {
          request.current = null;
          // Reload facts before offering another batch; GET never resumes work.
          await refresh();
        } else if (["queued", "running"].includes(next.status)) timer = setTimeout(poll, 1000);
      } catch {
        if (!disposed && active(token)) {
          setError("Connection interrupted. Generation may still be running. Reconnecting to saved progress.");
          timer = setTimeout(poll, 2000);
        }
      }
    }
    timer = setTimeout(poll, 1000);
    return () => { disposed = true; clearTimeout(timer); };
  }, [projectId, operation?.operation_id, running]);

  async function submit(items: ProjectFileSelection[]) {
    if (!preview || preview.project_id !== projectId || preview.status !== "ready" || changing.current || running
      || (operation && operation.status !== "completed")) return;
    const token = epoch.current;
    const signature = JSON.stringify({workspace_token: preview.workspace_token, items});
    if (request.current?.signature !== signature) request.current = {signature, id: crypto.randomUUID()};
    changing.current = true; setBusy(true); setError(null);
    try {
      const next = await startProjectFiles(projectId, {request_id: request.current.id, workspace_token: preview.workspace_token, items});
      if (active(token) && next.project_id === projectId) { setOperation(next); if (next.status === "completed") await refresh(); }
    } catch {
      if (active(token)) setError("Could not start this batch. Refresh to check saved progress and review the latest file conditions.");
    } finally { if (active(token)) { changing.current = false; setBusy(false); } }
  }
  async function resume() {
    if (!operation?.can_resume || operation.status !== "interrupted" || changing.current) return;
    const token = epoch.current; const id = operation.operation_id;
    changing.current = true; setBusy(true); setError(null);
    try {
      const latest = await getProjectFilesOperation(projectId, id);
      if (!active(token)) return;
      if (latest.project_id !== projectId) return;
      if (latest.status !== "interrupted" || !latest.can_resume) { setOperation(latest); return; }
      const next = await resumeProjectFilesOperation(projectId, id);
      if (active(token) && next.project_id === projectId) {setOperation(next); if (next.status === "completed") await refresh();}
    } catch {
      if (active(token)) setError("Could not resume saved progress. Close any open output documents and refresh to check again.");
    } finally { if (active(token)) { changing.current = false; setBusy(false); } }
  }
  return {preview: preview?.project_id === projectId ? preview : null,
    operation: operation?.project_id === projectId ? operation : null, loading, busy, running, error, refresh, submit, resume};
}
