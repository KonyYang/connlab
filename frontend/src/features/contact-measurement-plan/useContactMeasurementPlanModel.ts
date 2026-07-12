import { useCallback, useEffect, useMemo, useState } from "react";
import {
  acceptCompatibleContactMeasurementPlanSuggestions,
  ApiRequestError,
  confirmContactMeasurementPlanRevision,
  fetchContactMeasurementPlanWorkspace,
  openContactMeasurementPlanRevision,
  patchContactMeasurementPlanTarget,
  rebindContactMeasurementPlanTarget,
  refreshContactMeasurementPlanImpacts,
  saveContactMeasurementPlanRevision,
  type ContactMeasurementPlanTarget,
  type ContactMeasurementPlanWorkspace,
} from "../../api/client";
import {
  addCustomContactFamily,
  validateContactMeasurementFamilies,
} from "./contactMeasurementPlanSelectors";

const ACTOR = "local-operator";

export function useContactMeasurementPlanModel({ projectId }: { projectId: string }) {
  const [workspace, setWorkspace] = useState<ContactMeasurementPlanWorkspace | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [localTarget, setLocalTarget] = useState<ContactMeasurementPlanTarget | null>(null);
  const [staleLocalTarget, setStaleLocalTarget] = useState<ContactMeasurementPlanTarget | null>(null);

  const reload = useCallback(async (): Promise<void> => {
    const next = await fetchContactMeasurementPlanWorkspace(projectId);
    setWorkspace(next);
    setSelectedKey((current) => current ?? next.targets[0]?.stable_target_key ?? null);
    setLocalTarget((current) => {
      const selected = next.targets.find((target) => target.stable_target_key === current?.stable_target_key);
      return selected ? cloneTarget(selected) : current;
    });
  }, [projectId]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    void fetchContactMeasurementPlanWorkspace(projectId)
      .then((next) => {
        if (cancelled) return;
        setWorkspace(next);
        const initial = next.targets[0] ?? null;
        setSelectedKey(initial?.stable_target_key ?? null);
        setLocalTarget(initial ? cloneTarget(initial) : null);
      })
      .catch((cause) => {
        if (!cancelled) setError(messageFor(cause, "Unable to load contact measurement setup."));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [projectId]);

  const selectedTarget = useMemo(
    () => localTarget ?? workspace?.targets.find((target) => target.stable_target_key === selectedKey) ?? null,
    [localTarget, selectedKey, workspace]
  );
  const dirty = Boolean(
    localTarget &&
      workspace?.targets.some(
        (target) =>
          target.stable_target_key === localTarget.stable_target_key &&
          JSON.stringify(target) !== JSON.stringify(localTarget)
      )
  );

  function selectTarget(key: string): void {
    if (busy || (dirty && key !== selectedKey)) {
      setError("Save or cancel the current target before selecting another target.");
      return;
    }
    const target = workspace?.targets.find((item) => item.stable_target_key === key) ?? null;
    setSelectedKey(key);
    setLocalTarget(target ? cloneTarget(target) : null);
    setError(null);
  }

  function updateSelectedTarget(update: (target: ContactMeasurementPlanTarget) => ContactMeasurementPlanTarget): void {
    if (!selectedTarget || busy) return;
    setLocalTarget(update(cloneTarget(selectedTarget)));
    setMessage(null);
  }

  function cancelSelectedTarget(): void {
    const source = workspace?.targets.find((target) => target.stable_target_key === selectedKey) ?? null;
    setLocalTarget(source ? cloneTarget(source) : null);
    setError(null);
  }

  function addCustomFamily(): void {
    if (!selectedTarget || busy) return;
    setLocalTarget(addCustomContactFamily(cloneTarget(selectedTarget)));
  }

  function removeCustomFamily(familyId: string): void {
    if (!selectedTarget || busy) return;
    setLocalTarget({
      ...cloneTarget(selectedTarget),
      families: selectedTarget.families.filter(
        (family) => family.family_id !== familyId || !family.is_custom
      ),
    });
  }

  async function run(
    action: string,
    command: () => Promise<unknown>,
    staleTarget: ContactMeasurementPlanTarget | null = null
  ): Promise<void> {
    if (busy) return;
    setBusy(action);
    setError(null);
    setMessage(null);
    try {
      await command();
      await reload();
      setMessage("Contact measurement plan reloaded.");
    } catch (cause) {
      if (isStale(cause) && staleTarget) {
        setStaleLocalTarget(cloneTarget(staleTarget));
      }
      setError(messageFor(cause, "Unable to update contact measurement plan."));
    } finally {
      setBusy(null);
    }
  }

  async function openDraft(): Promise<void> {
    await run("open", () => openContactMeasurementPlanRevision(projectId, ACTOR));
  }

  async function saveSelectedTarget(): Promise<void> {
    const revisionId = workspace?.editable_revision_id;
    const fingerprint = workspace?.editable_revision_fingerprint;
    if (!revisionId || !fingerprint || !selectedTarget) {
      setError("Open an editable measurement plan before saving a target.");
      return;
    }
    const validation = validateContactMeasurementFamilies(selectedTarget.families);
    if (validation) {
      setError(validation);
      return;
    }
    await run("target", () =>
      patchContactMeasurementPlanTarget(projectId, revisionId, {
        actor: ACTOR,
        expected_revision_fingerprint: fingerprint,
        stable_target_key: selectedTarget.stable_target_key,
        included: selectedTarget.included,
        exclusion_reason: selectedTarget.exclusion_reason,
        families: selectedTarget.families.map((family) => ({
          family_id: family.family_id,
          label: family.label,
          count_per_sample: family.count_per_sample,
          record_label: family.record_label,
          record_prefix: family.record_prefix,
          included: family.included,
          is_custom: family.is_custom,
        })),
      }), selectedTarget
    );
  }

  async function reloadLatest(): Promise<void> {
    if (busy) return;
    setBusy("reload");
    setError(null);
    try {
      await reload();
      setMessage("Latest contact measurement plan loaded.");
    } catch (cause) {
      setError(messageFor(cause, "Unable to reload contact measurement plan."));
    } finally {
      setBusy(null);
    }
  }

  function discardStaleLocalEdits(): void {
    setStaleLocalTarget(null);
    cancelSelectedTarget();
    setError(null);
    setMessage("Local edits discarded.");
  }

  async function reapplySavedEdits(): Promise<void> {
    if (!staleLocalTarget || busy) return;
    setBusy("reapply");
    setError(null);
    setMessage(null);
    try {
      const latest = await fetchContactMeasurementPlanWorkspace(projectId);
      setWorkspace(latest);
      setSelectedKey(staleLocalTarget.stable_target_key);
      const revisionId = latest.editable_revision_id;
      const fingerprint = latest.editable_revision_fingerprint;
      const currentTarget = latest.targets.find(
        (target) => target.stable_target_key === staleLocalTarget.stable_target_key
      );
      const validation = validateContactMeasurementFamilies(staleLocalTarget.families);
      if (!revisionId || !fingerprint || !currentTarget) {
        throw new Error("The saved target is no longer editable. Review the latest plan.");
      }
      if (validation) {
        throw new Error(validation);
      }
      await patchContactMeasurementPlanTarget(projectId, revisionId, {
        actor: ACTOR,
        expected_revision_fingerprint: fingerprint,
        stable_target_key: staleLocalTarget.stable_target_key,
        included: staleLocalTarget.included,
        exclusion_reason: staleLocalTarget.exclusion_reason,
        families: staleLocalTarget.families.map((family) => ({
          family_id: family.family_id,
          label: family.label,
          count_per_sample: family.count_per_sample,
          record_label: family.record_label,
          record_prefix: family.record_prefix,
          included: family.included,
          is_custom: family.is_custom,
        })),
      });
      await reload();
      setStaleLocalTarget(null);
      setMessage("Saved edits reapplied to the latest plan.");
    } catch (cause) {
      setError(messageFor(cause, "Unable to re-apply saved edits."));
    } finally {
      setBusy(null);
    }
  }

  async function saveDraft(): Promise<void> {
    const revisionId = workspace?.editable_revision_id;
    const fingerprint = workspace?.editable_revision_fingerprint;
    if (!revisionId || !fingerprint) return;
    await run("save", () => saveContactMeasurementPlanRevision(projectId, revisionId, ACTOR, fingerprint));
  }

  async function confirmPlan(): Promise<void> {
    const revisionId = workspace?.editable_revision_id;
    const fingerprint = workspace?.editable_revision_fingerprint;
    if (!revisionId || !fingerprint) return;
    await run("confirm", () => confirmContactMeasurementPlanRevision(projectId, revisionId, ACTOR, fingerprint));
  }

  async function refreshImpacts(): Promise<void> {
    const revisionId = workspace?.editable_revision_id;
    const fingerprint = workspace?.matrix_binding?.matrix_binding_fingerprint;
    if (!revisionId || !fingerprint) return;
    await run("review", () => refreshContactMeasurementPlanImpacts(projectId, revisionId, ACTOR, fingerprint));
  }

  async function acceptCompatible(): Promise<void> {
    const revisionId = workspace?.editable_revision_id;
    const fingerprint = workspace?.editable_revision_fingerprint;
    if (!revisionId || !fingerprint) return;
    await run("accept", () => acceptCompatibleContactMeasurementPlanSuggestions(projectId, revisionId, ACTOR, fingerprint));
  }

  async function rebindSelectedTarget(candidateSubjectKey: string): Promise<void> {
    const revisionId = workspace?.editable_revision_id;
    const fingerprint = workspace?.editable_revision_fingerprint;
    if (!revisionId || !fingerprint || !selectedTarget) return;
    await run("rebind", () =>
      rebindContactMeasurementPlanTarget(
        projectId,
        revisionId,
        ACTOR,
        fingerprint,
        selectedTarget.stable_target_key,
        candidateSubjectKey
      )
    );
  }

  return {
    workspace,
    loading,
    busy,
    error,
    message,
    selectedTarget,
    dirty,
    staleLocalTarget,
    reload,
    selectTarget,
    updateSelectedTarget,
    cancelSelectedTarget,
    addCustomFamily,
    removeCustomFamily,
    openDraft,
    saveSelectedTarget,
    saveDraft,
    confirmPlan,
    refreshImpacts,
    acceptCompatible,
    rebindSelectedTarget,
    reloadLatest,
    discardStaleLocalEdits,
    reapplySavedEdits,
  };
}

function cloneTarget(target: ContactMeasurementPlanTarget): ContactMeasurementPlanTarget {
  return { ...target, families: target.families.map((family) => ({ ...family })) };
}

function messageFor(cause: unknown, fallback: string): string {
  if (cause instanceof ApiRequestError && cause.status === 409) {
    return "Contact measurement plan changed. Reload before continuing.";
  }
  return cause instanceof Error ? cause.message : fallback;
}

function isStale(cause: unknown): cause is ApiRequestError {
  return cause instanceof ApiRequestError && cause.status === 409;
}
