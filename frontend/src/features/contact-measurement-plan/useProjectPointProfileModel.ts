import { useCallback, useEffect, useMemo, useState } from "react";
import {
  confirmProjectPointProfile,
  fetchProjectPointProfileWorkspace,
  type ProjectPointProfileWorkspace,
} from "../../api/client";
import {
  emptyProjectPointProfileCategory,
  localPointProfileRows,
  pointProfileValidation,
  projectPointProfileTotal,
  type ProjectPointProfileDraftCategory,
} from "./projectPointProfileSelectors";

const ACTOR = "local-operator";

export function useProjectPointProfileModel({ projectId }: { projectId: string }) {
  const [workspace, setWorkspace] = useState<ProjectPointProfileWorkspace | null>(null);
  const [rows, setRows] = useState<ProjectPointProfileDraftCategory[]>([emptyProjectPointProfileCategory()]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const hydrate = useCallback((next: ProjectPointProfileWorkspace) => {
    setWorkspace(next);
    setRows(localPointProfileRows(next.confirmed_revision?.categories));
  }, []);

  const reload = useCallback(async () => hydrate(await fetchProjectPointProfileWorkspace(projectId)), [hydrate, projectId]);

  useEffect(() => {
    let current = true;
    setLoading(true);
    void fetchProjectPointProfileWorkspace(projectId)
      .then((next) => { if (current) hydrate(next); })
      .catch(() => { if (current) setError("Unable to load project point profile."); })
      .finally(() => { if (current) setLoading(false); });
    return () => { current = false; };
  }, [hydrate, projectId]);

  const total = useMemo(() => projectPointProfileTotal(rows), [rows]);
  const validation = useMemo(() => pointProfileValidation(rows), [rows]);

  async function confirm(): Promise<boolean> {
    if (validation || busy) {
      setError(validation);
      return false;
    }
    setBusy(true);
    setError(null);
    try {
      await confirmProjectPointProfile(projectId, {
        actor: ACTOR,
        expected_confirmed_revision_id: workspace?.confirmed_revision?.revision_id ?? null,
        expected_confirmed_revision_fingerprint: workspace?.confirmed_revision?.fingerprint ?? null,
        categories: rows.map((row) => ({ category_id: row.category_id, prefix: row.prefix.trim(), point_expression: row.point_expression })),
      });
      await reload();
      return true;
    } catch (cause) {
      setError(cause instanceof Error && cause.message.includes("stale") ? "Point Profile changed. Cancel and reopen the latest confirmed profile." : "Unable to confirm Point Profile.");
      return false;
    } finally {
      setBusy(false);
    }
  }

  return {
    workspace, rows, loading, busy, error, total, validation,
    updateRow: (index: number, patch: Partial<ProjectPointProfileDraftCategory>) => setRows((current) => current.map((row, itemIndex) => itemIndex === index ? { ...row, ...patch } : row)),
    addCategory: () => setRows((current) => current.length < 256 ? [...current, emptyProjectPointProfileCategory()] : current),
    removeCategory: (index: number) => setRows((current) => {
      const next = current.filter((_, itemIndex) => itemIndex !== index);
      return next.length ? next : [emptyProjectPointProfileCategory()];
    }),
    confirm,
  };
}
