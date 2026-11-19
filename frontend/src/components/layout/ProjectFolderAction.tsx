import { useEffect, useRef, useState } from "react";
import { getPublicFolderWorkflowContext, openLocalProjectFolder } from "../../api/client";
import { UiIcon } from "../common/UiIcon";

export function ProjectFolderAction({ projectId, blockedReason }: { projectId: string; blockedReason?: string }) {
  const [available, setAvailable] = useState(false);
  const [opening, setOpening] = useState(false);
  const [feedback, setFeedback] = useState<{ message: string; error: boolean } | null>(null);
  const mounted = useRef(false);
  const openPending = useRef(false);

  useEffect(() => {
    mounted.current = true;
    let active = true;
    let check = 0;
    const refresh = () => {
      const request = ++check;
      void getPublicFolderWorkflowContext(projectId).then(context => {
        if (active && request === check) setAvailable(context.project_id === projectId && context.local_official_folder_available);
      }).catch(() => {
        if (active && request === check) setAvailable(false);
      });
    };
    const onFolderChanged = (event: Event) => {
      if ((event as CustomEvent<string>).detail === projectId) refresh();
    };
    refresh();
    window.addEventListener("focus", refresh);
    window.addEventListener("connlab:project-folder-changed", onFolderChanged);
    return () => {
      active = false;
      mounted.current = false;
      window.removeEventListener("focus", refresh);
      window.removeEventListener("connlab:project-folder-changed", onFolderChanged);
    };
  }, [projectId]);

  async function openFolder() {
    if (!available || blockedReason || openPending.current) return;
    openPending.current = true;
    setOpening(true);
    setFeedback(null);
    try {
      const result = await openLocalProjectFolder(projectId);
      if (!mounted.current || result.project_id !== projectId || result.status === "opened") return;
      const path = result.local_official_folder_path;
      if (result.status === "unsupported" && path && navigator.clipboard?.writeText) {
        try {
          await navigator.clipboard.writeText(path);
          if (mounted.current) setFeedback({ message: "Project folder path copied. Open it in File Explorer.", error: false });
          return;
        } catch { /* Show the path when the clipboard is unavailable. */ }
      }
      if (mounted.current) setFeedback({ message: [result.message, path].filter(Boolean).join(" "), error: true });
    } catch (error) {
      if (mounted.current) setFeedback({ message: error instanceof Error ? error.message : "Could not open the project folder.", error: true });
    } finally {
      openPending.current = false;
      if (mounted.current) setOpening(false);
    }
  }

  const title = blockedReason ?? (opening ? "Opening project folder…" : available ? "Open project folder" : "Project folder is not available yet");
  return <>
    <button type="button" className="ui-secondary-action top-bar-folder-action" aria-label="Open project folder"
      title={title} disabled={Boolean(blockedReason) || !available || opening} onClick={() => void openFolder()}>
      <UiIcon name="folder" />
    </button>
    {feedback && <p className="top-bar-folder-feedback" role={feedback.error ? "alert" : "status"}>{feedback.message}</p>}
  </>;
}
