import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  acceptCompatibleContactMeasurementPlanSuggestions,
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
  addFreeformContactFamily,
  cloneContactMeasurementTarget,
  contactMeasurementFamilyPayload,
  editableContactMeasurementTarget,
  freeformFamilyNumber,
  freeformFamilySemanticKey,
  initializeFreeformRecordLabelsForOrigins,
  markIntroducedFreeformFamilyOrigins,
  mergePersistedFreeformFamilyOrigins,
  moveContactFamily,
  moveFreeformFamilyOrigin,
  nextFamilyHighWater,
  renewFreeformContactFamilyIdentity,
  resolveWorkspaceSelectedTarget,
  resolveFreeformPrefix,
  validateContactMeasurementFamilies,
  workspaceFreeformFamilySemantics,
} from "./contactMeasurementPlanSelectors";
import {
  contactMeasurementPlanMessageFor,
  isStaleContactMeasurementPlanError,
} from "./contactMeasurementPlanModelErrors";

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
  const [issuedFamilyHighWater, setIssuedFamilyHighWater] = useState({
    llcr: 0,
    cr_specified_current: 0,
  });
  const [issuedFamilySemantics, setIssuedFamilySemantics] = useState<Record<string, string>>({});
  const familyOrigins = useRef<Record<string, "starter" | "added" | "template" | "persisted">>({});
  const activeProjectId = useRef(projectId);
  const projectGeneration = useRef(0);
  const reloadOperation = useRef(0);

  const reload = useCallback(async (): Promise<void> => {
    const callerGeneration = projectGeneration.current;
    const next = await fetchContactMeasurementPlanWorkspace(projectId);
    if (activeProjectId.current !== projectId || projectGeneration.current !== callerGeneration) return;
    setWorkspace(next);
    familyOrigins.current = mergePersistedFreeformFamilyOrigins(familyOrigins.current, next);
    setIssuedFamilyHighWater((current) => nextFamilyHighWater(current, next));
    setIssuedFamilySemantics((current) => ({ ...current, ...workspaceFreeformFamilySemantics(next) }));
    const selected = resolveWorkspaceSelectedTarget(
      next, localTarget?.stable_target_key ?? selectedKey
    );
    setSelectedKey(selected?.stable_target_key ?? null);
    setLocalTarget(() => {
      if (!selected) return null;
      const editable = editableContactMeasurementTarget(selected, next);
      familyOrigins.current = markIntroducedFreeformFamilyOrigins(
        familyOrigins.current, selected, editable, "starter"
      );
      return editable;
    });
    setStaleLocalTarget((current) => current?.stable_target_key === selected?.stable_target_key
      ? current
      : null);
  }, [localTarget, projectId, selectedKey]);

  useEffect(() => {
    let cancelled = false;
    const projectChanged = activeProjectId.current !== projectId;
    activeProjectId.current = projectId;
    if (projectChanged) {
      projectGeneration.current += 1;
      familyOrigins.current = {};
      setWorkspace(null);
      setBusy(null);
      setError(null);
      setMessage(null);
      setSelectedKey(null);
      setLocalTarget(null);
      setStaleLocalTarget(null);
      setIssuedFamilyHighWater({ llcr: 0, cr_specified_current: 0 });
      setIssuedFamilySemantics({});
    }
    setLoading(true);
    setError(null);
    void fetchContactMeasurementPlanWorkspace(projectId)
      .then((next) => {
        if (cancelled || activeProjectId.current !== projectId) return;
        setWorkspace(next);
        familyOrigins.current = mergePersistedFreeformFamilyOrigins(familyOrigins.current, next);
        setIssuedFamilyHighWater((current) => nextFamilyHighWater(current, next));
        setIssuedFamilySemantics((current) => ({ ...current, ...workspaceFreeformFamilySemantics(next) }));
        const initial = resolveWorkspaceSelectedTarget(next, null);
        setSelectedKey(initial?.stable_target_key ?? null);
        const editable = initial ? editableContactMeasurementTarget(initial, next) : null;
        if (initial && editable) {
          familyOrigins.current = markIntroducedFreeformFamilyOrigins(
            familyOrigins.current, initial, editable, "starter"
          );
        }
        setLocalTarget(editable);
      })
      .catch((cause) => {
        if (!cancelled) setError(contactMeasurementPlanMessageFor(cause, "Unable to load contact measurement setup."));
      })
      .finally(() => {
        if (!cancelled && activeProjectId.current === projectId) setLoading(false);
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
    const editable = target && workspace ? editableContactMeasurementTarget(target, workspace) : null;
    if (target && editable) {
      familyOrigins.current = markIntroducedFreeformFamilyOrigins(
        familyOrigins.current, target, editable, "starter"
      );
    }
    setLocalTarget(editable);
    setError(null);
  }

  function updateSelectedTarget(update: (target: ContactMeasurementPlanTarget) => ContactMeasurementPlanTarget): void {
    if (!selectedTarget || busy) return;
    setLocalTarget(update(cloneContactMeasurementTarget(selectedTarget)));
    setMessage(null);
  }

  function cancelSelectedTarget(): void {
    const source = workspace?.targets.find((target) => target.stable_target_key === selectedKey) ?? null;
    const editable = source && workspace ? editableContactMeasurementTarget(source, workspace) : null;
    if (source && editable) {
      familyOrigins.current = markIntroducedFreeformFamilyOrigins(
        familyOrigins.current, source, editable, "starter"
      );
    }
    setLocalTarget(editable);
    setError(null);
  }

  function addFreeformFamily(template?: "high_power" | "low_power" | "signal"): void {
    if (!selectedTarget || busy) return;
    const next = addFreeformContactFamily(
      cloneContactMeasurementTarget(selectedTarget),
      issuedFamilyHighWater,
      template
    );
    const added = next.families.at(-1);
    const number = added ? freeformFamilyNumber(added.family_id) : 0;
    setIssuedFamilyHighWater((current) => ({
      ...current,
      [next.contact_kind]: Math.max(current[next.contact_kind], number),
    }));
    if (added) setIssuedFamilySemantics((current) => ({ ...current, [added.family_id]: freeformFamilySemanticKey(added) }));
    familyOrigins.current = markIntroducedFreeformFamilyOrigins(
      familyOrigins.current, selectedTarget, next, template ? "template" : "added"
    );
    setLocalTarget(next);
  }

  function removeFamily(familyId: string): void {
    if (!selectedTarget || busy) return;
    setLocalTarget({
      ...cloneContactMeasurementTarget(selectedTarget),
      families: selectedTarget.families.filter((family) => family.family_id !== familyId),
    });
  }

  function moveFamily(familyId: string, direction: -1 | 1): void {
    if (!selectedTarget || busy) return;
    setLocalTarget(moveContactFamily(cloneContactMeasurementTarget(selectedTarget), familyId, direction));
  }

  function renewSemanticFamilyIdentity(
    target: ContactMeasurementPlanTarget,
    familyId: string
  ): ContactMeasurementPlanTarget {
    const current = target.families.find((family) => family.family_id === familyId);
    const persisted = workspace?.targets
      .find((item) => item.stable_target_key === target.stable_target_key)
      ?.families.find((family) => family.family_id === familyId);
    const baseline = persisted ? freeformFamilySemanticKey(persisted) : issuedFamilySemantics[familyId];
    if (!current || baseline === freeformFamilySemanticKey(current)) {
      return target;
    }
    const renewed = renewFreeformContactFamilyIdentity(target, familyId, issuedFamilyHighWater);
    const replacement = renewed.families.find(
      (family, index) => family.family_id !== target.families[index]?.family_id
    );
    if (replacement) {
      const number = freeformFamilyNumber(replacement.family_id);
      setIssuedFamilyHighWater((state) => ({
        ...state,
        [renewed.contact_kind]: Math.max(state[renewed.contact_kind], number),
      }));
      setIssuedFamilySemantics((state) => ({ ...state, [replacement.family_id]: freeformFamilySemanticKey(replacement) }));
      familyOrigins.current = moveFreeformFamilyOrigin(
        familyOrigins.current, familyId, replacement.family_id
      );
    }
    return renewed;
  }

  function resolveSelectedFamilyPrefix(familyId: string): void {
    if (!selectedTarget || busy) return;
    const resolvedTarget = {
      ...cloneContactMeasurementTarget(selectedTarget),
      families: selectedTarget.families.map((family) => family.family_id === familyId
        ? {
            ...family,
            record_prefix: resolveFreeformPrefix(
              family.record_prefix,
              family.label,
              freeformFamilyNumber(family.family_id)
            ),
          }
        : family),
    };
    setLocalTarget(renewSemanticFamilyIdentity(resolvedTarget, familyId));
  }

  function finalizeSelectedFamilyLabel(familyId: string): void {
    if (!selectedTarget || busy) return;
    setLocalTarget(renewSemanticFamilyIdentity(cloneContactMeasurementTarget(selectedTarget), familyId));
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
      if (activeProjectId.current !== projectId) return;
      setMessage("Contact measurement plan reloaded.");
    } catch (cause) {
      if (activeProjectId.current !== projectId) return;
      if (isStaleContactMeasurementPlanError(cause) && staleTarget) {
        setStaleLocalTarget(cloneContactMeasurementTarget(staleTarget));
      }
      setError(contactMeasurementPlanMessageFor(cause, "Unable to update contact measurement plan."));
    } finally {
      if (activeProjectId.current === projectId) setBusy(null);
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
    const targetForSave = initializeFreeformRecordLabelsForOrigins(selectedTarget, familyOrigins.current);
    const validation = validateContactMeasurementFamilies(targetForSave.families);
    if (validation) {
      setError(validation);
      return;
    }
    setLocalTarget(targetForSave);
    await run("target", () =>
      patchContactMeasurementPlanTarget(projectId, revisionId, {
        actor: ACTOR,
        expected_revision_fingerprint: fingerprint,
        stable_target_key: targetForSave.stable_target_key,
        included: targetForSave.included,
        exclusion_reason: targetForSave.exclusion_reason,
        families: contactMeasurementFamilyPayload(targetForSave.families),
      }), targetForSave
    );
  }

  async function applySelectedFamiliesToBlankTargets(): Promise<void> {
    const source = selectedTarget
      && initializeFreeformRecordLabelsForOrigins(selectedTarget, familyOrigins.current);
    if (!source || busy || source.is_override) return;
    const validation = validateContactMeasurementFamilies(source.families);
    if (validation) {
      setError(validation);
      return;
    }
    setLocalTarget(source);
    const blankKeys = (workspace?.targets ?? [])
      .filter((target) => target.stable_target_key !== source.stable_target_key)
      .filter((target) => target.eligible && !target.is_override && target.families.length === 0)
      .map((target) => target.stable_target_key);
    if (blankKeys.length === 0) {
      setMessage("No blank eligible targets are available for this profile.");
      return;
    }
    setBusy("apply-blank");
    setError(null);
    try {
      for (const stableTargetKey of blankKeys) {
        const latest = await fetchContactMeasurementPlanWorkspace(projectId);
        if (activeProjectId.current !== projectId) return;
        const revisionId = latest.editable_revision_id;
        const fingerprint = latest.editable_revision_fingerprint;
        const target = latest.targets.find((item) => item.stable_target_key === stableTargetKey);
        if (!revisionId || !fingerprint || !target || target.is_override || target.families.length > 0) continue;
        await patchContactMeasurementPlanTarget(projectId, revisionId, {
          actor: ACTOR,
          expected_revision_fingerprint: fingerprint,
          stable_target_key: stableTargetKey,
          included: target.included,
          exclusion_reason: target.exclusion_reason,
          families: contactMeasurementFamilyPayload(source.families),
        });
      }
      await reload();
      if (activeProjectId.current !== projectId) return;
      setMessage("Profile applied to blank eligible targets.");
    } catch (cause) {
      if (activeProjectId.current !== projectId) return;
      setError(contactMeasurementPlanMessageFor(cause, "Unable to apply the contact profile."));
    } finally {
      if (activeProjectId.current === projectId) setBusy(null);
    }
  }

  async function reloadLatest(): Promise<void> {
    if (busy) return;
    const callerProjectId = projectId;
    const callerGeneration = projectGeneration.current;
    const operation = ++reloadOperation.current;
    const ownsReload = () => (
      activeProjectId.current === callerProjectId
      && projectGeneration.current === callerGeneration
      && reloadOperation.current === operation
    );
    setBusy("reload");
    setError(null);
    try {
      await reload();
      if (!ownsReload()) return;
      setMessage("Latest contact measurement plan loaded.");
    } catch (cause) {
      if (!ownsReload()) return;
      setError(contactMeasurementPlanMessageFor(cause, "Unable to reload contact measurement plan."));
    } finally {
      if (ownsReload()) setBusy((current) => current === "reload" ? null : current);
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
      if (activeProjectId.current !== projectId) return;
      setWorkspace(latest);
      setSelectedKey(staleLocalTarget.stable_target_key);
      const revisionId = latest.editable_revision_id;
      const fingerprint = latest.editable_revision_fingerprint;
      const currentTarget = latest.targets.find(
        (target) => target.stable_target_key === staleLocalTarget.stable_target_key
      );
      if (!revisionId || !fingerprint || !currentTarget) {
        throw new Error("The saved target is no longer editable. Review the latest plan.");
      }
      const targetForReapply = initializeFreeformRecordLabelsForOrigins(
        staleLocalTarget, familyOrigins.current
      );
      const validation = validateContactMeasurementFamilies(targetForReapply.families);
      if (validation) {
        throw new Error(validation);
      }
      await patchContactMeasurementPlanTarget(projectId, revisionId, {
        actor: ACTOR,
        expected_revision_fingerprint: fingerprint,
        stable_target_key: targetForReapply.stable_target_key,
        included: targetForReapply.included,
        exclusion_reason: targetForReapply.exclusion_reason,
        families: contactMeasurementFamilyPayload(targetForReapply.families),
      });
      await reload();
      if (activeProjectId.current !== projectId) return;
      setStaleLocalTarget(null);
      setMessage("Saved edits reapplied to the latest plan.");
    } catch (cause) {
      if (activeProjectId.current !== projectId) return;
      setError(contactMeasurementPlanMessageFor(cause, "Unable to re-apply saved edits."));
    } finally {
      if (activeProjectId.current === projectId) setBusy(null);
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
    addFreeformFamily,
    removeFamily,
    moveFamily,
    resolveSelectedFamilyPrefix,
    finalizeSelectedFamilyLabel,
    openDraft,
    saveSelectedTarget,
    applySelectedFamiliesToBlankTargets,
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
