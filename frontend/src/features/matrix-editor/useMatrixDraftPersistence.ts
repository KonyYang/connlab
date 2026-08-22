import { useEffect, useRef, useState } from "react";
import {
  discardMatrixEditorSessionDraft,
  isProjectLifecycleReadonlyErrorDetail,
  saveMatrixEditorSessionDraft,
  type MatrixEditorSessionConfirmRequest,
  type MatrixEditorSessionDurationAuthority,
  type MatrixEditorSessionDraftSaveRequest,
  type MatrixEditorSessionDraftSaveResponse,
  type MatrixEditorSessionSeed,
  type MatrixImportCommitResponse,
  type MatrixPreviewResponse,
  type ProjectMatrixDraftSaveRequest,
} from "../../api/client";
import { deriveReadonlyApiErrorMessage } from "../project-lifecycle/projectLifecycleReadonlyModel";

export type MatrixDraftSaveState = "idle" | "dirty" | "saving" | "saved" | "error";

type MatrixDraftPersistenceOptions = {
  currentPayload: ProjectMatrixDraftSaveRequest;
  currentSignature: string;
  draftLoading: boolean;
  durationAuthorities: MatrixEditorSessionDurationAuthority[];
  onBackToWorkbench: () => void;
  onError: (message: string) => void;
  projectId: string;
  readonlyMessage: string | null;
  sourcePreview: MatrixPreviewResponse | null;
};

type HydrateSessionOptions = {
  baselineSignature: string;
  hasEditorDraft: boolean;
  seed: MatrixEditorSessionSeed;
};

const AUTOSAVE_DELAY_MS = 800;
const AUTOSAVE_CANCEL_WAIT_TIMEOUT_MS = 1500;

function parseRequestError(error: unknown, fallback: string): string {
  const detail =
    error && typeof error === "object" && "detail" in error
      ? (error as { detail: unknown }).detail
      : null;
  if (isProjectLifecycleReadonlyErrorDetail(detail)) {
    return deriveReadonlyApiErrorMessage(detail);
  }
  if (error instanceof Error && error.message.trim().length > 0) {
    return error.message;
  }
  return fallback;
}

function buildSessionDraftSaveRequest(
  currentPayload: ProjectMatrixDraftSaveRequest,
  sourcePreview: MatrixPreviewResponse | null,
  expectedActiveConfirmedMatrixId: string | null,
  expectedActiveConfirmedRevision: number | null,
  sourceImportId: string | null,
  sourceSnapshotId: string | null,
  durationAuthorities: MatrixEditorSessionDurationAuthority[],
): MatrixEditorSessionDraftSaveRequest {
  return {
    expected_active_confirmed_matrix_id: expectedActiveConfirmedMatrixId,
    expected_active_confirmed_revision: expectedActiveConfirmedRevision,
    source_document_path: sourcePreview?.source_document_path ?? null,
    source_document_name: sourcePreview?.source_document_name ?? null,
    source_format: sourcePreview?.source_format ?? null,
    source_import_id: sourceImportId,
    source_snapshot_id: sourceSnapshotId,
    pre_test_buffer_days: null,
    post_test_buffer_days: currentPayload.post_test_buffer_days ?? null,
    sample_received_date: currentPayload.sample_received_date ?? null,
    planned_test_start_date: currentPayload.planned_test_start_date ?? null,
    planned_test_complete_date: currentPayload.planned_test_complete_date ?? null,
    estimated_completion_date: currentPayload.estimated_completion_date ?? null,
    groups: currentPayload.groups.map((group, index) => ({
      draft_group_id: group.draft_group_id ?? `session-group-${index + 1}`,
      source_group_snapshot_id: group.source_group_snapshot_id ?? null,
      group_order: group.group_order,
      group_key: group.group_key,
      group_label: group.group_label,
      is_selected: group.is_selected,
      sample_quantity_expression: group.sample_quantity_expression ?? null,
      sample_note: group.sample_note ?? null,
    })),
    rows: currentPayload.rows.map((row, index) => ({
      draft_row_id: row.draft_row_id ?? `session-row-${index + 1}`,
      source_row_snapshot_id: row.source_row_snapshot_id ?? null,
      row_order: row.row_order,
      test_item: row.test_item,
      source_section: row.source_section ?? null,
      method: row.method ?? null,
      condition: row.condition ?? null,
      requirement: row.requirement ?? null,
      day_expression: row.day_expression ?? null,
      is_sample_row: Boolean(row.is_sample_row),
    })),
    cells: currentPayload.cells,
    duration_authorities: durationAuthorities,
  };
}

export function useMatrixDraftPersistence({
  currentPayload,
  currentSignature,
  draftLoading,
  durationAuthorities,
  onBackToWorkbench,
  onError,
  projectId,
  readonlyMessage,
  sourcePreview,
}: MatrixDraftPersistenceOptions) {
  const [saveState, setSaveState] = useState<MatrixDraftSaveState>("idle");
  const [baselineSignature, setBaselineSignature] = useState<string | null>(null);
  const [activeConfirmedMatrixId, setActiveConfirmedMatrixId] = useState<string | null>(null);
  const [activeConfirmedRevision, setActiveConfirmedRevision] = useState<number | null>(null);
  const [sourceImportId, setSourceImportId] = useState<string | null>(null);
  const [sourceSnapshotId, setSourceSnapshotId] = useState<string | null>(null);
  const [activeAuthoritySourceImportId, setActiveAuthoritySourceImportId] = useState<string | null>(null);
  const [savedEditorDraftId, setSavedEditorDraftId] = useState<string | null>(null);
  const [savedPayloadSignature, setSavedPayloadSignature] = useState<string | null>(null);
  const [savedLocalSignature, setSavedLocalSignature] = useState<string | null>(null);
  const [isCancelling, setIsCancelling] = useState(false);
  const autosaveTimeoutRef = useRef<number | null>(null);
  const autosaveGenerationRef = useRef(0);
  const autosaveInFlightRef = useRef<Promise<MatrixEditorSessionDraftSaveResponse | null> | null>(null);
  const autosaveAbortControllerRef = useRef<AbortController | null>(null);
  const latestAutosaveResultRef = useRef<MatrixEditorSessionDraftSaveResponse | null>(null);
  const cancellingRef = useRef(false);
  const currentPayloadRef = useRef(currentPayload);
  const durationAuthoritiesRef = useRef(durationAuthorities);
  const sourcePreviewRef = useRef(sourcePreview);
  const onBackRef = useRef(onBackToWorkbench);
  const onErrorRef = useRef(onError);
  currentPayloadRef.current = currentPayload;
  durationAuthoritiesRef.current = durationAuthorities;
  sourcePreviewRef.current = sourcePreview;
  onBackRef.current = onBackToWorkbench;
  onErrorRef.current = onError;

  const hasUnsavedChanges =
    baselineSignature !== null && currentSignature !== baselineSignature;
  const hasCurrentSavedDraft =
    Boolean(savedEditorDraftId) &&
    Boolean(savedPayloadSignature) &&
    savedLocalSignature === currentSignature;

  useEffect(() => {
    if (autosaveTimeoutRef.current !== null) {
      window.clearTimeout(autosaveTimeoutRef.current);
      autosaveTimeoutRef.current = null;
    }
    if (
      !hasUnsavedChanges ||
      !projectId.trim() ||
      !activeConfirmedMatrixId ||
      draftLoading ||
      Boolean(readonlyMessage) ||
      cancellingRef.current ||
      isCancelling
    ) {
      return;
    }
    const generation = autosaveGenerationRef.current + 1;
    autosaveGenerationRef.current = generation;
    const signatureToSave = currentSignature;
    const request = buildSessionDraftSaveRequest(
      currentPayloadRef.current,
      sourcePreviewRef.current,
      activeConfirmedMatrixId,
      activeConfirmedRevision,
      sourceImportId,
      sourceSnapshotId,
      durationAuthoritiesRef.current,
    );
    setSaveState("dirty");
    autosaveTimeoutRef.current = window.setTimeout(() => {
      if (cancellingRef.current) {
        return;
      }
      setSaveState("saving");
      autosaveAbortControllerRef.current?.abort();
      const autosaveAbortController = new AbortController();
      autosaveAbortControllerRef.current = autosaveAbortController;
      const saveRequest = saveMatrixEditorSessionDraft(projectId, request, {
        signal: autosaveAbortController.signal,
      })
        .then((response) => {
          latestAutosaveResultRef.current = response;
          if (
            autosaveGenerationRef.current === generation &&
            !cancellingRef.current
          ) {
            setSavedEditorDraftId(response.editor_draft_id);
            setSavedPayloadSignature(response.saved_payload_signature);
            setSavedLocalSignature(signatureToSave);
            setActiveConfirmedMatrixId(response.active_confirmed_matrix_id);
            setActiveConfirmedRevision(response.active_confirmed_revision);
            setBaselineSignature(signatureToSave);
            setSaveState("saved");
          }
          return response;
        })
        .catch((error) => {
          if (autosaveAbortController.signal.aborted) {
            return null;
          }
          if (
            autosaveGenerationRef.current === generation &&
            !cancellingRef.current
          ) {
            setSaveState("error");
            onErrorRef.current(parseRequestError(error, "Autosave failed."));
          }
          return null;
        })
        .finally(() => {
          if (autosaveInFlightRef.current === saveRequest) {
            autosaveInFlightRef.current = null;
          }
          if (autosaveAbortControllerRef.current === autosaveAbortController) {
            autosaveAbortControllerRef.current = null;
          }
        });
      autosaveInFlightRef.current = saveRequest;
    }, AUTOSAVE_DELAY_MS);
    return () => {
      if (autosaveTimeoutRef.current !== null) {
        window.clearTimeout(autosaveTimeoutRef.current);
        autosaveTimeoutRef.current = null;
      }
    };
  }, [
    activeConfirmedMatrixId,
    activeConfirmedRevision,
    currentSignature,
    draftLoading,
    hasUnsavedChanges,
    isCancelling,
    projectId,
    readonlyMessage,
    sourceImportId,
    sourceSnapshotId,
  ]);

  const hydrateSession = ({
    baselineSignature: nextBaselineSignature,
    hasEditorDraft,
    seed,
  }: HydrateSessionOptions): void => {
    setBaselineSignature(nextBaselineSignature);
    setSaveState(hasEditorDraft ? "saved" : "idle");
    setActiveConfirmedMatrixId(seed.active_confirmed_matrix_id ?? null);
    setActiveConfirmedRevision(seed.active_confirmed_revision ?? null);
    setSourceImportId(seed.editor_source_import_id ?? seed.active_source_import_id ?? null);
    setSourceSnapshotId(seed.editor_source_snapshot_id ?? seed.active_source_snapshot_id ?? null);
    setActiveAuthoritySourceImportId(seed.active_source_import_id ?? null);
    setSavedEditorDraftId(seed.editor_draft_id ?? null);
    setSavedPayloadSignature(seed.saved_payload_signature ?? null);
    setSavedLocalSignature(
      seed.editor_draft_id && seed.saved_payload_signature ? nextBaselineSignature : null,
    );
    latestAutosaveResultRef.current = null;
    cancellingRef.current = false;
    setIsCancelling(false);
  };

  const clearAfterLoadFailure = (): void => {
    setActiveConfirmedMatrixId(null);
    setActiveConfirmedRevision(null);
    setSourceImportId(null);
    setSourceSnapshotId(null);
    setActiveAuthoritySourceImportId(null);
    setSavedEditorDraftId(null);
    setSavedPayloadSignature(null);
    setSavedLocalSignature(null);
    setSaveState("error");
  };

  const acceptImportedDraft = (
    response: MatrixImportCommitResponse,
    nextBaselineSignature: string,
  ): void => {
    setSourceImportId(response.source_import_id);
    setSourceSnapshotId(response.source_snapshot_id);
    setSavedEditorDraftId(null);
    setSavedPayloadSignature(null);
    setSavedLocalSignature(null);
    setBaselineSignature(nextBaselineSignature);
    latestAutosaveResultRef.current = null;
    setSaveState("saved");
  };

  const markUnsaved = (): void => {
    if (saveState !== "saving") {
      setSaveState("dirty");
    }
  };

  const observeAuthority = (matrixId: string | null, revision: number | null): void => {
    setActiveConfirmedMatrixId(matrixId);
    setActiveConfirmedRevision(revision);
  };

  const acceptNoChange = (nextBaselineSignature: string): void => {
    setSaveState("saved");
    setBaselineSignature(nextBaselineSignature);
  };

  const buildConfirmRequest = (
    confirmedBy: string,
    expectedMatrixId = activeConfirmedMatrixId,
    expectedRevision = activeConfirmedRevision,
  ): MatrixEditorSessionConfirmRequest => ({
    ...buildSessionDraftSaveRequest(
      currentPayloadRef.current,
      sourcePreviewRef.current,
      expectedMatrixId,
      expectedRevision,
      sourceImportId,
      sourceSnapshotId,
      durationAuthoritiesRef.current,
    ),
    expected_editor_draft_id: savedEditorDraftId,
    expected_saved_payload_signature: savedPayloadSignature,
    confirmed_by: confirmedBy,
  });

  const waitForAutosaveBeforeCancel = async (): Promise<MatrixEditorSessionDraftSaveResponse | null> => {
    const inFlightAutosave = autosaveInFlightRef.current;
    if (!inFlightAutosave) {
      return null;
    }
    let timeoutId: number | null = null;
    const cancelWaitTimeout = new Promise<null>((resolve) => {
      timeoutId = window.setTimeout(() => resolve(null), AUTOSAVE_CANCEL_WAIT_TIMEOUT_MS);
    });
    try {
      return await Promise.race([inFlightAutosave.catch(() => null), cancelWaitTimeout]);
    } finally {
      if (timeoutId !== null) {
        window.clearTimeout(timeoutId);
      }
    }
  };

  const cancel = async (): Promise<void> => {
    if (readonlyMessage) {
      onBackRef.current();
      return;
    }
    if (hasUnsavedChanges || savedEditorDraftId) {
      const shouldDiscard = window.confirm(
        "Discard current Matrix edits and return to Workbench?",
      );
      if (!shouldDiscard) {
        return;
      }
    }
    cancellingRef.current = true;
    autosaveGenerationRef.current += 1;
    autosaveAbortControllerRef.current?.abort();
    autosaveAbortControllerRef.current = null;
    if (autosaveTimeoutRef.current !== null) {
      window.clearTimeout(autosaveTimeoutRef.current);
      autosaveTimeoutRef.current = null;
    }
    setIsCancelling(true);
    setSaveState("saving");
    const inFlightResult = await waitForAutosaveBeforeCancel();
    const discardTokens = inFlightResult ?? latestAutosaveResultRef.current;
    try {
      await discardMatrixEditorSessionDraft(projectId, {
        expected_editor_draft_id:
          discardTokens?.editor_draft_id ?? savedEditorDraftId ?? null,
        expected_saved_payload_signature:
          discardTokens?.saved_payload_signature ?? savedPayloadSignature ?? null,
      });
      onBackRef.current();
    } catch (error) {
      cancellingRef.current = false;
      setIsCancelling(false);
      setSaveState("error");
      onErrorRef.current(
        parseRequestError(error, "Cancel failed. Matrix draft was not discarded."),
      );
    }
  };

  return {
    acceptImportedDraft,
    acceptNoChange,
    activeAuthoritySourceImportId,
    activeConfirmedMatrixId,
    activeConfirmedRevision,
    buildConfirmRequest,
    cancel,
    clearAfterLoadFailure,
    hasCurrentSavedDraft,
    hasUnsavedChanges,
    hydrateSession,
    isCancelling,
    markUnsaved,
    observeAuthority,
    saveState,
    savedEditorDraftId,
    savedPayloadSignature,
    sourceImportId,
    sourceSnapshotId,
  };
}
