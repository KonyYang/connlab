import { useEffect, useRef, useState } from "react";
import { createBasicProjectWorkspace, previewBasicProjectWorkspace, resumeBasicProjectWorkspace,
  type BasicProjectWorkspacePreview, type BasicProjectWorkspaceResult } from "../../api/client";

// The basic directory has its own journal and availability, independent of derived Office outputs.
export function useBasicProjectWorkspace(projectId: string, onChanged: () => Promise<void> | void) {
  const [state, setState] = useState<{projectId: string; preview: BasicProjectWorkspacePreview | null; result: BasicProjectWorkspaceResult | null; error: string | null; loading: boolean; busy: boolean}>({projectId, preview: null, result: null, error: null, loading: true, busy: false});
  const currentProject = useRef(projectId);
  const epoch = useRef(0);
  if (currentProject.current !== projectId) { currentProject.current = projectId; epoch.current += 1; }
  const alive = useRef(true);
  const changing = useRef<number | null>(null);
  const previewSequence = useRef(0);
  const requestId = useRef<{projectId: string; value: string} | null>(null);
  const changed = useRef(onChanged); changed.current = onChanged;
  const active = (token: number) => alive.current && currentProject.current === projectId && token === epoch.current;

  async function refresh() {
    const token = epoch.current;
    const sequence = ++previewSequence.current;
    if (!active(token)) return;
    setState(previous => ({ ...previous, loading: true }));
    try {
      const preview = await previewBasicProjectWorkspace(projectId);
      if (active(token) && sequence === previewSequence.current && preview.project_id === projectId) setState(previous => ({ ...previous, projectId, preview, loading: false, error: null }));
    } catch (error) {
      if (active(token) && sequence === previewSequence.current) setState(previous => ({ ...previous, loading: false, error: error instanceof Error ? error.message : "Could not check the project folder." }));
    }
  }
  useEffect(() => {
    alive.current = true;
    changing.current = null;
    requestId.current = null;
    setState({projectId, preview: null, result: null, error: null, loading: true, busy: false});
    void refresh();
    return () => { alive.current = false; epoch.current += 1; };
  }, [projectId]);

  async function create(confirmExisting = false) {
    const token = epoch.current;
    if (!active(token) || changing.current === token) return;
    const preview = state.projectId === projectId ? state.preview : null;
    if (!preview || preview.status === "blocked" || (preview.status === "review_required" && !confirmExisting)) return;
    if (preview.status === "recovery_required" && !preview.operation_id) {
      setState(previous => ({...previous, error:"Refresh the saved project folder operation before resuming."}));
      return;
    }
    changing.current = token;
    setState(previous => ({ ...previous, busy: true, error: null }));
    try {
      if (requestId.current?.projectId !== projectId) requestId.current = {projectId, value: crypto.randomUUID()};
      const result = preview.status === "recovery_required" && preview.operation_id
        ? await resumeBasicProjectWorkspace(projectId, preview.operation_id)
        : await createBasicProjectWorkspace(projectId, {expected_context: preview.expected_context, request_id: requestId.current.value, confirm_existing: confirmExisting});
      if (!active(token)) return;
      setState(previous => ({ ...previous, result, preview: previous.preview ? {...previous.preview, directory_available:result.directory_available, official_project_folder_path:result.official_project_folder_path} : null, error: result.directory_available ? null : result.message ?? "The project folder is not available yet." }));
      if (result.status === "completed") requestId.current = null;
      await refresh();
      if (active(token) && !result.directory_available) setState(previous => ({...previous, error: result.message ?? "The project folder is not available yet."}));
      if (active(token)) await changed.current();
      if (active(token)) window.dispatchEvent(new CustomEvent("connlab:project-folder-changed", {detail: projectId}));
    } catch (error) {
      if (active(token)) setState(previous => ({ ...previous, error: error instanceof Error ? error.message : "Could not prepare the project folder." }));
    } finally {
      if (active(token)) { changing.current = null; setState(previous => ({ ...previous, busy: false })); }
    }
  }
  const visible = state.projectId === projectId ? state : {preview: null, result: null, error: null, loading: true, busy: false};
  return { ...visible, refresh, create,
    directoryAvailable: visible.preview?.directory_available ?? false,
    folderPath: visible.preview?.official_project_folder_path ?? null };
}
