import { useEffect, useState } from "react";
import {
  getProject,
  getProjectLifecycle,
  listProjectLtrs,
  type Project,
  type ProjectLifecycleResponse,
} from "../../api/client";

type EditorContext = {
  projectId: string;
  project: Project | null;
  lifecycle: ProjectLifecycleResponse | null;
  latestLtr: string | null;
  loading: boolean;
  error: string | null;
};

function loadingContext(projectId: string): EditorContext {
  return { projectId, project: null, lifecycle: null, latestLtr: null, loading: true, error: null };
}

/** Matrix session data loads separately; folder/output preparation belongs to Workbench. */
export function useMatrixEditorContext(projectId: string) {
  const [context, setContext] = useState(() => loadingContext(projectId));
  const [reload, setReload] = useState(0);
  useEffect(() => {
    let active = true;
    setContext(loadingContext(projectId));
    void Promise.all([
      getProject(projectId),
      getProjectLifecycle(projectId),
      listProjectLtrs(projectId),
    ]).then(([project, lifecycle, ltrs]) => {
      if (active) {
        setContext({ projectId, project, lifecycle, latestLtr: ltrs.at(-1)?.ltr_number ?? null,
          loading: false, error: null });
      }
    }).catch(() => {
      if (active) {
        setContext({ ...loadingContext(projectId), loading: false,
          error: "Unable to load project information. Retry before editing Matrix." });
      }
    });
    return () => { active = false; };
  }, [projectId, reload]);

  return {
    ...(context.projectId === projectId ? context : loadingContext(projectId)),
    retry: () => setReload((value) => value + 1),
  };
}
