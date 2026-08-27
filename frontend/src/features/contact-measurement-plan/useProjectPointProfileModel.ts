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
  projectPointProfileCrCoverageMode,
  projectPointProfileCrTotal,
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
  const [deltaREnabled, setDeltaREnabled] = useState(true);

  const hydrate = useCallback((next: ProjectPointProfileWorkspace) => {
    setWorkspace(next);
    const coverage = next.confirmed_revision?.cr_coverage;
    setDeltaREnabled(next.confirmed_revision?.delta_r_enabled ?? true);
    setRows(localPointProfileRows(
      next.confirmed_revision?.categories,
      coverage?.selected_category_ids ?? [],
    ));
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
  const crCoverageMode = useMemo(
    () => projectPointProfileCrCoverageMode(rows),
    [rows],
  );
  const crTotal = useMemo(
    () => projectPointProfileCrTotal(rows, crCoverageMode),
    [crCoverageMode, rows],
  );
  const crSelectedCount = useMemo(
    () => rows.filter((row) => row.cr_selected).length,
    [rows],
  );
  const validation = useMemo(
    () => pointProfileValidation(rows),
    [rows],
  );

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
        cr_coverage_mode: crCoverageMode,
        delta_r_enabled: deltaREnabled,
        categories: rows.map((row) => ({
          category_id: row.category_id,
          prefix: row.prefix.trim(),
          point_expression: row.point_expression,
          cr_selected: crCoverageMode === "custom" && Boolean(row.cr_selected),
        })),
      });
      await reload();
      return true;
    } catch (cause) {
      setError(pointProfileConfirmErrorMessage(cause));
      return false;
    } finally {
      setBusy(false);
    }
  }

  return {
    workspace, rows, loading, busy, error, total, crTotal, crSelectedCount,
    crCoverageMode, deltaREnabled, validation,
    setDeltaREnabled,
    updateRow: (index: number, patch: Partial<ProjectPointProfileDraftCategory>) => setRows((current) => current.map((row, itemIndex) => itemIndex === index ? { ...row, ...patch } : row)),
    addCategory: () => setRows((current) => current.length < 256 ? [...current, emptyProjectPointProfileCategory()] : current),
    removeCategory: (index: number) => setRows((current) => {
      const next = current.filter((_, itemIndex) => itemIndex !== index);
      return next.length ? next : [emptyProjectPointProfileCategory()];
    }),
    setCrSelected: (index: number, selected: boolean) => setRows((current) => current.map(
      (row, itemIndex) => itemIndex === index ? { ...row, cr_selected: selected } : row,
    )),
    confirm,
  };
}

function pointProfileConfirmErrorMessage(cause: unknown): string {
  if (!(cause instanceof Error)) {
    return "Unable to confirm Point Profile.";
  }
  const detail = cause.message.trim();
  if (/stale/i.test(detail)) {
    return "Point Profile changed. Cancel and reopen the latest confirmed profile.";
  }
  if (!detail || /^Request failed with \d{3}$/i.test(detail)) {
    return "Unable to confirm Point Profile.";
  }
  return `Unable to confirm Point Profile: ${detail}`;
}
