import { useCallback, useEffect, useMemo, useState } from "react";
import {
  confirmProjectPointProfile,
  fetchProjectPointProfileWorkspace,
  saveProjectPointProfileDraft,
  type ProjectPointProfileCategory,
  type ProjectPointProfileWorkspace,
} from "../../api/client";
import {
  addProjectPointProfileTemplate,
  emptyProjectPointProfileCategory,
  moveProjectPointProfileCategory,
  normalizeOrdinals,
  parsePositiveCount,
  pointProfileValidation,
  projectPointProfileTotal,
  type ProjectPointProfileDraftCategory,
} from "./projectPointProfileSelectors";

const ACTOR = "local-operator";

export function useProjectPointProfileModel({ projectId }: { projectId: string }) {
  const [workspace, setWorkspace] = useState<ProjectPointProfileWorkspace | null>(null);
  const [rows, setRows] = useState<ProjectPointProfileDraftCategory[]>([emptyProjectPointProfileCategory()]);
  const [baselineRows, setBaselineRows] = useState<ProjectPointProfileDraftCategory[]>([emptyProjectPointProfileCategory()]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<"save" | "confirm" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const hydrate = useCallback((next: ProjectPointProfileWorkspace) => {
    const nextRows = profileBaselineRows(next);
    setWorkspace(next);
    setRows(nextRows);
    setBaselineRows(nextRows);
  }, []);

  const reload = useCallback(async () => {
    hydrate(await fetchProjectPointProfileWorkspace(projectId));
  }, [hydrate, projectId]);

  useEffect(() => {
    let current = true;
    setLoading(true);
    setError(null);
    void fetchProjectPointProfileWorkspace(projectId)
      .then((next) => { if (current) hydrate(next); })
      .catch(() => { if (current) setError("Unable to load project point profile."); })
      .finally(() => { if (current) setLoading(false); });
    return () => { current = false; };
  }, [hydrate, projectId]);

  const total = useMemo(() => projectPointProfileTotal(rows), [rows]);
  const validation = useMemo(() => pointProfileValidation(rows), [rows]);
  const editable = workspace?.editable_revision ?? null;

  const command = () => ({
    actor: ACTOR,
    expected_revision_id: editable?.revision_id ?? null,
    expected_revision_fingerprint: editable?.fingerprint ?? null,
    categories: normalizeOrdinals(rows).map((row) => ({
      ...row,
      count_per_sample: parsePositiveCount(row.count_per_sample),
    })) as ProjectPointProfileCategory[],
  });

  async function saveDraft(): Promise<void> {
    if (validation || busy) {
      setError(validation);
      return;
    }
    setBusy("save");
    setError(null);
    setMessage(null);
    try {
      await saveProjectPointProfileDraft(projectId, command());
      await reload();
      setMessage("Point Profile draft saved.");
    } catch (cause) {
      setError(messageFor(cause));
    } finally {
      setBusy(null);
    }
  }

  async function confirm(): Promise<void> {
    if (validation || total <= 0 || busy) {
      setError(validation ?? "Confirm Point Profile requires an included positive total.");
      return;
    }
    if (!editable) {
      setError("Save the Point Profile draft before confirming it.");
      return;
    }
    setBusy("confirm");
    setError(null);
    setMessage(null);
    try {
      await confirmProjectPointProfile(projectId, command());
      await reload();
      setMessage("Point Profile confirmed.");
    } catch (cause) {
      setError(messageFor(cause));
    } finally {
      setBusy(null);
    }
  }

  function discard(): void {
    setRows(baselineRows);
    setError(null);
    setMessage("Local changes discarded.");
  }

  return {
    workspace,
    rows,
    loading,
    busy,
    error,
    message,
    total,
    validation,
    updateRow: (index: number, patch: Partial<ProjectPointProfileDraftCategory>) =>
      setRows((current) => normalizeOrdinals(current.map((row, itemIndex) => itemIndex === index ? { ...row, ...patch } : row))),
    addCategory: () => setRows((current) => normalizeOrdinals([...current, emptyProjectPointProfileCategory()])),
    addTemplate: (template: "high_power" | "low_power" | "signal") =>
      setRows((current) => addProjectPointProfileTemplate(current, template)),
    removeCategory: (index: number) => setRows((current) => normalizeOrdinals(current.filter((_, itemIndex) => itemIndex !== index))),
    moveCategory: (index: number, direction: -1 | 1) => setRows((current) => moveProjectPointProfileCategory(current, index, direction)),
    saveDraft,
    confirm,
    discard,
  };
}

export function profileBaselineRows(workspace: ProjectPointProfileWorkspace): ProjectPointProfileDraftCategory[] {
  const source = workspace.editable_revision?.categories.length
    ? workspace.editable_revision.categories
    : workspace.confirmed_revision?.categories.length
      ? workspace.confirmed_revision.categories
      : null;
  return source ? source.map(toDraftRow) : [emptyProjectPointProfileCategory()];
}

function toDraftRow(row: ProjectPointProfileCategory): ProjectPointProfileDraftCategory {
  return { ...row, category_id: row.category_id };
}

function messageFor(cause: unknown): string {
  return cause instanceof Error && cause.message.includes("stale")
    ? "Point Profile changed. Reload the latest draft before saving."
    : "Unable to update Point Profile.";
}
