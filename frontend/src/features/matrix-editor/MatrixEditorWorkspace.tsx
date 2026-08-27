import { useEffect, useLayoutEffect, useRef, useState, type MouseEvent, type ReactElement } from "react";
import { useProjectRuntimeConsoleModel } from "../project-workbench/useProjectRuntimeConsoleModel";
import { buildProjectIdentityLine, deriveProjectReference } from "../projectIdentity";
import {
  deriveProjectLifecycleReadonlyView,
  deriveReadonlyApiErrorMessage,
} from "../project-lifecycle/projectLifecycleReadonlyModel";
import {
  ApiRequestError,
  confirmMatrixEditorSession,
  createMatrixRevisionDraft,
  fetchMatrixEditorSession,
  generateMatrixEditorTestRecordDraftDownload,
  generateMatrixEditorTestStatusDraftDownload,
  previewMatrixEditorTestRecordPublication,
  publishMatrixEditorTestRecord,
  isProjectLifecycleReadonlyErrorDetail,
  type MatrixEditorTestRecordPublicationPreview,
  type MatrixEditorSessionDraft,
  type MatrixEditorSessionDurationAuthority,
  type MatrixEditorSessionSeed,
  type MatrixEditorSessionConfirmResponse,
  type MatrixPreviewResponse,
} from "../../api/client";
import { MatrixSchedulePlanningCard } from "./MatrixSchedulePlanningCard";
import { MatrixEditorXlsxExportButton } from "./MatrixEditorXlsxExportButton";
import {
  buildMatrixEditorXlsxExportRequest,
  getMatrixEditorXlsxExportDisabledReason,
} from "./matrixEditorXlsxExportProjection";
import { useMatrixEditorXlsxExport } from "./useMatrixEditorXlsxExport";
import { MatrixImportSourceCandidatePicker } from "./MatrixImportSourceCandidatePicker";
import { MatrixMethodVersionSyncPanel } from "./MatrixMethodVersionSyncPanel";
import { useMatrixMethodVersionSync } from "./useMatrixMethodVersionSync";
import { MatrixImportStandardVersionChoiceDialog } from "./MatrixImportStandardVersionChoiceDialog";
import { MatrixImportDialog } from "./MatrixImportDialog";
import { useMatrixImportWorkflow } from "./useMatrixImportWorkflow";
import {
  useMatrixDraftPersistence,
  type MatrixDraftSaveState,
} from "./useMatrixDraftPersistence";
import { ContactMeasurementPlanSummaryCard } from "../contact-measurement-plan/ContactMeasurementPlanSummaryCard";
import { MatrixAutoGrowTextarea } from "./MatrixAutoGrowTextarea";
import { MatrixStepWorkspace } from "./MatrixStepWorkspace";
import { useProjectPointProfileSummaryModel } from "../contact-measurement-plan/useProjectPointProfileSummaryModel";
import { LlcrCrRecordWorkbookPanel } from "./LlcrCrRecordWorkbookPanel";
import {
  calculateMatrixSchedule,
  emptySchedulePlan,
  formatPlanningDays,
  type MatrixSchedulePlan,
} from "./matrixSchedulePlanning";
import {
  buildAuthorityComparableSignatureFromDraft,
  buildDraftSavePayload,
  buildEmptyRow,
  buildInitialGroupColumns,
  buildInitialMatrixRows,
  buildInvalidSelectedSampleGroupIds,
  buildMatrixEditorTestRecordDraftRequest,
  buildMatrixFromSessionSeedDraft,
  buildSessionDraftFromProjectMatrixDraft,
  cloneGroups,
  cloneRows,
  nextGroupId,
  normalizeGroupName,
  schedulePlanFromProjectMatrixDraft,
  schedulePlanFromSeed,
  type EditableMatrixRow,
  type GroupColumn,
} from "./matrixEditorDraftModel";
import {
  buildPreviewStepNoteLookup,
  buildSelectedGroupStepPreviewRows,
  extractMarkerKey,
  formatConciseItemSectionNote,
  parseStepTokens,
  replaceItemSectionNoteSection,
  stripLeadingMarkerPrefix,
  type StepOutputOverride,
} from "./matrixStepWorkspaceModel";
import "../../workbench.css";

type MatrixEditorWorkspaceProps = {
  projectId: string;
  onBackToWorkbench: () => void;
  onOpenContactMeasurementSetup?: () => void;
};

type MatrixSnapshot = {
  rows: EditableMatrixRow[];
  groups: GroupColumn[];
  schedulePlan: MatrixSchedulePlan;
};

type MatrixPublishState = "idle" | "loading" | "success" | "error";
type MatrixTestRecordState = "idle" | "loading" | "success" | "error";
type MatrixPublishMode = "first_authority" | "revision_authority";
type MatrixRevisionDraftActionState = "idle" | "opening" | "error";

const MVP_REVISION_CONFIRMED_BY = "connlab-operator";

const AUTO_SAVE_STATUS_COPY: Record<MatrixDraftSaveState, string> = {
  idle: "",
  dirty: "",
  saving: "",
  saved: "",
  error: "Save failed. Retry before confirming.",
};

type MatrixContextMenu =
  | { kind: "row"; rowIndex: number; x: number; y: number }
  | { kind: "group"; groupId: string; x: number; y: number };

function parseRequestError(error: unknown, fallback: string): string {
  const detail =
    error && typeof error === "object" && "detail" in error
      ? (error as { detail: unknown }).detail
      : null;
  if (
    isProjectLifecycleReadonlyErrorDetail(detail)
  ) {
    return deriveReadonlyApiErrorMessage(detail);
  }
  if (error instanceof Error && error.message.trim().length > 0) {
    return error.message;
  }
  return fallback;
}

function triggerBlobDownload(blob: Blob, fileName: string): void {
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = fileName;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.URL.revokeObjectURL(url);
}

export function MatrixEditorWorkspace({
  projectId,
  onBackToWorkbench,
  onOpenContactMeasurementSetup,
}: MatrixEditorWorkspaceProps): ReactElement {
  const model = useProjectRuntimeConsoleModel(projectId);
  const lifecycleReadonlyView = deriveProjectLifecycleReadonlyView(model.lifecycle);
  const isLifecycleReadonly = lifecycleReadonlyView.readonly;
  const [editableRows, setEditableRows] = useState<EditableMatrixRow[]>(() => buildInitialMatrixRows());
  const [groupColumns, setGroupColumns] = useState<GroupColumn[]>(() => buildInitialGroupColumns());
  const [selectedRowId, setSelectedRowId] = useState<string | null>(null);
  const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);
  const [, setLastMessage] = useState<string>("");
  const [, setUndoStack] = useState<MatrixSnapshot[]>([]);
  const [contextMenu, setContextMenu] = useState<MatrixContextMenu | null>(null);
  const [stepOutputOverrides, setStepOutputOverrides] = useState<Record<string, StepOutputOverride>>({});
  const [sampleValues, setSampleValues] = useState<Record<string, string>>({ "group-1": "" });
  const [sampleMergeNotes, setSampleMergeNotes] = useState<Record<string, string>>({});
  const [schedulePlan, setSchedulePlan] = useState<MatrixSchedulePlan>(() => emptySchedulePlan());
  const [showSelectedGroupsOnly, setShowSelectedGroupsOnly] = useState(false);
  const [draftLoading, setDraftLoading] = useState(false);
  const [sessionReloadGeneration, setSessionReloadGeneration] = useState(0);
  const [revisionDraftActionState, setRevisionDraftActionState] =
    useState<MatrixRevisionDraftActionState>("idle");
  const [revisionDraftActionMessage, setRevisionDraftActionMessage] = useState<string | null>(null);
  const [confirmActiveState, setConfirmActiveState] = useState<MatrixPublishState>("idle");
  const [confirmActiveMessage, setConfirmActiveMessage] = useState<string>("");
  const [testRecordState, setTestRecordState] = useState<MatrixTestRecordState>("idle");
  const [testRecordMessage, setTestRecordMessage] = useState<string>("");
  const [testRecordConflict, setTestRecordConflict] =
    useState<MatrixEditorTestRecordPublicationPreview | null>(null);
  const [testStatusState, setTestStatusState] = useState<MatrixTestRecordState>("idle");
  const [testStatusMessage, setTestStatusMessage] = useState<string>("");
  const [activeAuthorityConfirmed, setActiveAuthorityConfirmed] = useState(false);
  const [activeAuthorityBaselineSignature, setActiveAuthorityBaselineSignature] = useState<string | null>(null);
  const [durationAuthorities, setDurationAuthorities] =
    useState<MatrixEditorSessionDurationAuthority[]>([]);
  const pointProfileSummary = useProjectPointProfileSummaryModel(projectId);
  const [sourceUnavailableMessage, setSourceUnavailableMessage] = useState<string | null>(null);
  const revisionDraftReloadPendingRef = useRef(false);

  const currentSavePayload = buildDraftSavePayload(
    editableRows,
    groupColumns,
    sampleValues,
    schedulePlan,
    durationAuthorities
  );
  const currentSaveSignature = JSON.stringify(currentSavePayload);

  const applyDraftSnapshotToEditor = (
    draft: MatrixEditorSessionDraft,
    sourcePreview: MatrixPreviewResponse | null = null,
    nextSchedulePlan: MatrixSchedulePlan = emptySchedulePlan()
  ): string => {
    const mapped = buildMatrixFromSessionSeedDraft(draft, sourcePreview);
    const nextGroups = mapped.groups.length > 0 ? mapped.groups : buildInitialGroupColumns();
    const nextRows = mapped.rows.length > 0 ? mapped.rows : buildInitialMatrixRows();
    const nextSamples = mapped.samples;
    setGroupColumns(nextGroups);
    setEditableRows(nextRows);
    setSampleValues(nextSamples);
    setDurationAuthorities(draft.duration_authorities ?? []);
    setSampleMergeNotes({});
    setSchedulePlan(nextSchedulePlan);
    setSelectedGroupId(nextGroups[0]?.id ?? null);
    setSelectedRowId(null);
    const baselinePayload = buildDraftSavePayload(
      nextRows,
      nextGroups,
      nextSamples,
      nextSchedulePlan,
      draft.duration_authorities ?? []
    );
    setActiveAuthorityConfirmed(false);
    setConfirmActiveState("idle");
    setConfirmActiveMessage("");
    return JSON.stringify(baselinePayload);
  };

  const matrixImport = useMatrixImportWorkflow({
    projectId,
    readonlyMessage: isLifecycleReadonly ? lifecycleReadonlyView.message : null,
    onCommitted: ({ preview, response }) => {
      const baselineSignature = applyDraftSnapshotToEditor(
        buildSessionDraftFromProjectMatrixDraft(response.project_matrix_draft),
        preview,
        schedulePlanFromProjectMatrixDraft(response.project_matrix_draft)
      );
      draftPersistence.acceptImportedDraft(response, baselineSignature);
    },
  });
  const {
    committedSourceDocumentName,
    dialog: importDialog,
    preview: importPreview,
    resetSessionSource: resetImportSessionSource,
    sourcePicker: importSourcePicker,
  } = matrixImport;

  const draftPersistence = useMatrixDraftPersistence({
    currentPayload: currentSavePayload,
    currentSignature: currentSaveSignature,
    draftLoading,
    durationAuthorities,
    onBackToWorkbench,
    onError: setConfirmActiveMessage,
    projectId,
    readonlyMessage: isLifecycleReadonly ? lifecycleReadonlyView.message : null,
    sourcePreview: importPreview,
  });
  const {
    activeAuthoritySourceImportId,
    activeConfirmedMatrixId,
    activeConfirmedRevision,
    hasCurrentSavedDraft,
    hasUnsavedChanges,
    isCancelling,
    saveState,
    savedEditorDraftId,
    savedPayloadSignature,
    sourceImportId: sessionSourceImportId,
  } = draftPersistence;

  useEffect(() => {
    let cancelled = false;
    const loadSessionSeed = async (): Promise<void> => {
      setDraftLoading(true);
      try {
        const seed: MatrixEditorSessionSeed = await fetchMatrixEditorSession(projectId);
        if (cancelled) {
          return;
        }
        if (seed.editor_draft) {
          const loadedSchedulePlan = schedulePlanFromSeed(seed);
          const loadedSignature = applyDraftSnapshotToEditor(
            seed.editor_draft,
            seed.source_preview_payload ?? null,
            loadedSchedulePlan
          );
          draftPersistence.hydrateSession({
            baselineSignature: loadedSignature,
            hasEditorDraft: true,
            seed,
          });
          setActiveAuthorityBaselineSignature(
            buildAuthorityComparableSignatureFromDraft(seed.editor_draft, loadedSchedulePlan)
          );
        } else {
          const defaultRows = buildInitialMatrixRows();
          const defaultGroups = buildInitialGroupColumns();
          const defaultSamples: Record<string, string> = { "group-1": "" };
          const defaultSchedulePlan = emptySchedulePlan();
          setEditableRows(defaultRows);
          setGroupColumns(defaultGroups);
          setSampleValues(defaultSamples);
          setSampleMergeNotes({});
          setDurationAuthorities([]);
          setSchedulePlan(defaultSchedulePlan);
          setSelectedGroupId(defaultGroups[0]?.id ?? null);
          setSelectedRowId(null);
          const defaultSignature = JSON.stringify(
            buildDraftSavePayload(defaultRows, defaultGroups, defaultSamples, defaultSchedulePlan)
          );
          draftPersistence.hydrateSession({
            baselineSignature: defaultSignature,
            hasEditorDraft: false,
            seed,
          });
          setActiveAuthorityBaselineSignature(null);
        }
        resetImportSessionSource(seed.source_preview_payload ?? null);
        setSourceUnavailableMessage(seed.source_unavailable_message ?? null);
        setShowSelectedGroupsOnly(false);
        setConfirmActiveState("idle");
        setConfirmActiveMessage("");
        setActiveAuthorityConfirmed(false);
        if (revisionDraftReloadPendingRef.current) {
          revisionDraftReloadPendingRef.current = false;
          if (seed.editor_draft_id) {
            setRevisionDraftActionState("idle");
            setRevisionDraftActionMessage("Editable Matrix draft opened.");
          } else {
            setRevisionDraftActionState("error");
            setRevisionDraftActionMessage("Unable to open an editable Matrix draft. Retry.");
          }
        }
      } catch (error) {
        if (cancelled) {
          return;
        }
        setSourceUnavailableMessage(null);
        setActiveAuthorityBaselineSignature(null);
        draftPersistence.clearAfterLoadFailure();
        if (revisionDraftReloadPendingRef.current) {
          revisionDraftReloadPendingRef.current = false;
          setRevisionDraftActionState("error");
          setRevisionDraftActionMessage("Unable to reload the editable Matrix draft. Retry.");
        }
      } finally {
        if (!cancelled) {
          setDraftLoading(false);
        }
      }
    };
    void loadSessionSeed();
    return () => {
      cancelled = true;
    };
  }, [projectId, resetImportSessionSource, sessionReloadGeneration]);

  useLayoutEffect(() => {
    setSampleValues((previous) => {
      const next: Record<string, string> = {};
      groupColumns.forEach((group) => {
        next[group.id] = previous[group.id] ?? "";
      });
      return next;
    });
    setSampleMergeNotes((previous) => {
      const next: Record<string, string> = {};
      groupColumns.forEach((group) => {
        if (previous[group.id]) {
          next[group.id] = previous[group.id];
        }
      });
      return next;
    });
  }, [groupColumns]);

  const projectReference = deriveProjectReference({
    latestLtr: model.latestLtr,
    projectNo: model.project?.project_no,
    projectId: model.project?.project_id ?? projectId,
  });
  const matrixEditorIdentityLine = buildProjectIdentityLine({
    project: model.project,
    latestLtr: model.latestLtr,
    projectId,
  });
  const currentSourceDocumentName =
    committedSourceDocumentName ||
    model.matrixAuthorityDraft?.source_document_name?.trim() ||
    null;
  const normalizedNameMap = new Map<string, string[]>();
  const emptyGroupIds = new Set<string>();
  groupColumns.forEach((group) => {
    const normalized = normalizeGroupName(group.name);
    if (normalized === "") {
      emptyGroupIds.add(group.id);
      return;
    }
    const existing = normalizedNameMap.get(normalized);
    if (existing) {
      existing.push(group.id);
      return;
    }
    normalizedNameMap.set(normalized, [group.id]);
  });
  const duplicateGroupIds = new Set<string>();
  const duplicateNames: string[] = [];
  normalizedNameMap.forEach((groupIds, normalizedName) => {
    if (groupIds.length <= 1) {
      return;
    }
    groupIds.forEach((groupId) => duplicateGroupIds.add(groupId));
    duplicateNames.push(normalizedName.toUpperCase());
  });
  const hasGroupNameError = emptyGroupIds.size > 0 || duplicateGroupIds.size > 0;
  const groupNameErrorMessage =
    duplicateNames.length > 0
      ? `Group names duplicated: ${duplicateNames.join(", ")}`
      : emptyGroupIds.size > 0
        ? "Group name is required"
        : "";
  const invalidStepFormatCellKeys = new Set<string>();
  const stepCellErrorMessageByKey = new Map<string, string>();
  const groupStepSequenceErrorIds = new Set<string>();
  const groupStepSequenceErrorCellKeys = new Set<string>();
  const groupStepSequenceErrorMessageById = new Map<string, string>();
  groupColumns.forEach((group) => {
    if (!group.isSelected) {
      return;
    }
    const validNonEmptyCellKeys: string[] = [];
    const groupNumbers: number[] = [];
    editableRows.forEach((row, rowIndex) => {
      if (row.isSampleRow) {
        return;
      }
      const value = row.groups[group.id] ?? "";
      const parsed = parseStepTokens(value);
      const cellKey = `${group.id}-${rowIndex}`;
      if (!parsed.isValid) {
        invalidStepFormatCellKeys.add(cellKey);
        stepCellErrorMessageByKey.set(cellKey, parsed.errorMessage);
        return;
      }
      if (parsed.numbers.length === 0) {
        return;
      }
      validNonEmptyCellKeys.push(cellKey);
      groupNumbers.push(...parsed.numbers);
    });
    if (groupNumbers.length === 0) {
      return;
    }
    const sortedNumbers = [...groupNumbers].sort((a, b) => a - b);
    const hasDuplicate = sortedNumbers.some((value, index) => index > 0 && value === sortedNumbers[index - 1]);
    const uniqueSortedNumbers = [...new Set(sortedNumbers)];
    const startsFromOne = uniqueSortedNumbers[0] === 1;
    const hasGap = uniqueSortedNumbers.some((value, index) => index > 0 && value !== uniqueSortedNumbers[index - 1] + 1);
    if (!startsFromOne || hasGap || hasDuplicate) {
      const duplicates = sortedNumbers.filter((value, index) => index > 0 && value === sortedNumbers[index - 1]);
      const duplicateSet = [...new Set(duplicates)];
      const max = uniqueSortedNumbers[uniqueSortedNumbers.length - 1];
      const expected = new Set<number>();
      for (let value = 1; value <= max; value += 1) {
        expected.add(value);
      }
      uniqueSortedNumbers.forEach((value) => expected.delete(value));
      const missing = [...expected];
      const detailParts: string[] = [];
      if (!startsFromOne) {
        detailParts.push("must start at 1");
      }
      if (missing.length > 0) {
        detailParts.push(`missing: ${missing.join(",")}`);
      }
      if (duplicateSet.length > 0) {
        detailParts.push(`duplicates: ${duplicateSet.join(",")}`);
      }
      const groupDisplay = group.name.trim() || "(unnamed group)";
      const detailText = detailParts.join("; ");
      const sequenceErrorMessage = `${groupDisplay} sequence error: ${detailText}`;
      groupStepSequenceErrorIds.add(group.id);
      validNonEmptyCellKeys.forEach((cellKey) => groupStepSequenceErrorCellKeys.add(cellKey));
      groupStepSequenceErrorMessageById.set(group.id, sequenceErrorMessage);
      validNonEmptyCellKeys.forEach((cellKey) => {
        if (!stepCellErrorMessageByKey.has(cellKey)) {
          stepCellErrorMessageByKey.set(cellKey, sequenceErrorMessage);
        }
      });
    }
  });
  const hasStepTokenError = invalidStepFormatCellKeys.size > 0 || groupStepSequenceErrorIds.size > 0;
  const hasMatrixValidationError = hasGroupNameError || hasStepTokenError;
  const firstStepCellError = [...stepCellErrorMessageByKey.values()][0] ?? "";
  const stepTokenErrorMessage = hasStepTokenError ? firstStepCellError : "";
  const selectedGroup = groupColumns.find((group) => group.id === selectedGroupId) ?? null;
  const selectedGroupStepRows = buildSelectedGroupStepPreviewRows(
    editableRows,
    selectedGroup,
    stepOutputOverrides
  );
  const selectedGroupPreviewNotes = buildPreviewStepNoteLookup(importPreview, selectedGroup);
  const selectedGroupSamplesValue = selectedGroup ? sampleValues[selectedGroup.id] ?? "" : "";
  const onOpenEditableMatrixDraft = async (): Promise<void> => {
    if (
      isLifecycleReadonly ||
      !activeConfirmedMatrixId ||
      savedEditorDraftId ||
      revisionDraftActionState === "opening"
    ) {
      return;
    }
    setRevisionDraftActionState("opening");
    setRevisionDraftActionMessage("Opening editable Matrix draft.");
    try {
      await createMatrixRevisionDraft(projectId);
    } catch (error) {
      if (!(error instanceof ApiRequestError && error.status === 409)) {
        setRevisionDraftActionState("error");
        setRevisionDraftActionMessage(
          parseRequestError(error, "Unable to open an editable Matrix draft.")
        );
        return;
      }
    }
    revisionDraftReloadPendingRef.current = true;
    setSessionReloadGeneration((previous) => previous + 1);
  };
  const selectedGroupStepNotes = selectedGroupStepRows
    .map((row) => {
      const marker = extractMarkerKey(row.rawToken) ?? extractMarkerKey(row.suffixNote);
      const mapped = marker
        ? selectedGroupPreviewNotes.byStepAndMarker.get(`${row.stepNo}|${marker}`) ?? null
        : selectedGroupPreviewNotes.byStep.get(row.stepNo) ?? null;
      const rawNote = mapped?.sourceNote ?? row.sourceStepNote;
      if (!rawNote) {
        return null;
      }
      const body = stripLeadingMarkerPrefix(rawNote);
      return body.length > 0 ? `${row.rawToken} ${body}` : row.rawToken;
    })
    .filter((note): note is string => Boolean(note));
  const dedupedSelectedGroupStepNotes = [...new Set(selectedGroupStepNotes)];
  const selectedGroupItemSectionNotes = selectedGroupStepRows
    .map((row) => {
      const marker = extractMarkerKey(row.rawToken) ?? extractMarkerKey(row.suffixNote);
      const mapped = marker
        ? selectedGroupPreviewNotes.byStepAndMarker.get(`${row.stepNo}|${marker}`) ?? null
        : selectedGroupPreviewNotes.byStep.get(row.stepNo) ?? null;
      const markerNote = marker ? selectedGroupPreviewNotes.itemSectionByMarker.get(marker) ?? null : null;
      const rawNote = mapped?.sourceItemSectionNote ?? (markerNote ? replaceItemSectionNoteSection(markerNote, row.sourceSection) : row.sourceItemSectionNote);
      if (!rawNote) {
        return null;
      }
      const concise = formatConciseItemSectionNote(row.stepNo, rawNote);
      return concise.length > 0 ? concise : null;
    })
    .filter((note): note is string => Boolean(note));
  const sampleMarker = selectedGroupSamplesValue.match(/\((\d+|[a-zA-Z])\)|([*#])/);
  const selectedGroupSampleMergeNote = selectedGroup ? sampleMergeNotes[selectedGroup.id] ?? null : null;
  const selectedGroupSampleNotes = [
    selectedGroupPreviewNotes.sampleNote ?? (sampleMarker ? `${sampleMarker[0]}` : null),
    selectedGroupSampleMergeNote,
  ].filter((note): note is string => Boolean(note));
  const hasProjectId = projectId.trim().length > 0;
  const selectedDraftGroupIds = new Set(
    currentSavePayload.groups
      .filter((group) => group.is_selected)
      .map((group) => group.draft_group_id)
  );
  const hasAnyStepTokenValue = currentSavePayload.cells.some(
    (cell) => selectedDraftGroupIds.has(cell.draft_group_id) && (cell.cell_value ?? "").trim().length > 0
  );
  const testRecordDraftRequest = buildMatrixEditorTestRecordDraftRequest(
    editableRows,
    groupColumns,
    sampleValues
  );
  const canGenerateTestRecord =
    testRecordDraftRequest.groups.length > 0 && hasAnyStepTokenValue && !hasStepTokenError;
  const canGenerateTestStatus =
    testRecordDraftRequest.groups.length > 0 &&
    testRecordDraftRequest.rows.some(
      (row) => !row.is_sample_row && row.test_item.trim().length > 0
    );
  const scheduleCalculation = calculateMatrixSchedule(
    editableRows.map((row) => ({
      id: row.id,
      isSampleRow: row.isSampleRow,
      dayExpression: row.dayExpression,
      groups: row.groups,
    })),
    groupColumns.map((group) => ({
      id: group.id,
      name: group.name || group.groupKey,
      isSelected: group.isSelected,
    })),
    schedulePlan
  );
  const matrixXlsxExport = useMatrixEditorXlsxExport(projectId);
  const matrixXlsxExportRequest = buildMatrixEditorXlsxExportRequest({
    projectReference,
    groups: groupColumns,
    rows: editableRows,
    sampleValues,
    timeDisplays: Object.fromEntries(
      groupColumns.map((group) => [
        group.id,
        `${formatPlanningDays(scheduleCalculation.groupDays[group.id] ?? 0)} d`,
      ])
    ),
  });
  const matrixXlsxExportDisabledReason = getMatrixEditorXlsxExportDisabledReason({
    lifecycleMessage: isLifecycleReadonly ? lifecycleReadonlyView.message : "",
    busy: matrixXlsxExport.busy,
    selectedGroupCount: matrixXlsxExportRequest.groups.length,
    hasStepError: hasStepTokenError,
    stepErrorMessage: stepTokenErrorMessage,
    qualifyingRowCount: matrixXlsxExportRequest.rows.length,
  });
  const hasSchedulePlanningError = !scheduleCalculation.isValid;
  const schedulePlanningErrorMessage =
    Object.values(scheduleCalculation.rowErrors)[0] ??
    Object.values(scheduleCalculation.bufferErrors)[0] ??
    scheduleCalculation.dateError ??
    "";
  const invalidSelectedSampleGroupIds = buildInvalidSelectedSampleGroupIds(
    groupColumns,
    sampleValues
  );
  const hasSelectedSampleQuantityError = invalidSelectedSampleGroupIds.size > 0;
  const isPublishBusy = confirmActiveState === "loading" || isCancelling;
  const isSourceLineageReplacement =
    Boolean(sessionSourceImportId) &&
    Boolean(activeAuthoritySourceImportId) &&
    sessionSourceImportId !== activeAuthoritySourceImportId;
  const methodVersionSync = useMatrixMethodVersionSync({
    projectId,
    draftId: savedEditorDraftId,
    savedPayloadSignature,
    disabled: isLifecycleReadonly || draftLoading || !hasCurrentSavedDraft,
    onApplied: () => {
      setSessionReloadGeneration((previous) => previous + 1);
    },
  });
  const requiresCurrentSavedDraft =
    Boolean(activeConfirmedMatrixId) &&
    !isSourceLineageReplacement &&
    (hasUnsavedChanges ||
      saveState === "dirty" ||
      saveState === "saving" ||
      saveState === "error" ||
      Boolean(savedEditorDraftId));
  const publishDisabledReason =
    isLifecycleReadonly
      ? lifecycleReadonlyView.message
      : !hasProjectId
      ? "No project id."
      : hasMatrixValidationError
        ? groupNameErrorMessage || stepTokenErrorMessage
        : hasSelectedSampleQuantityError
          ? "Sample quantity is required for selected groups."
        : hasSchedulePlanningError
          ? schedulePlanningErrorMessage
        : isPublishBusy
          ? "Action in progress."
          : requiresCurrentSavedDraft && !hasCurrentSavedDraft
            ? saveState === "error"
              ? "Autosave failed. Retry before confirming."
              : "Saving Matrix draft before confirm..."
          : !hasAnyStepTokenValue
            ? "Add at least one step token before confirm."
            : "";
  const canPublishActiveMatrix = publishDisabledReason.length === 0;
  const publishBlockingMessage =
    publishDisabledReason && publishDisabledReason !== "Action in progress."
      ? publishDisabledReason
      : "";
  const visibleGroupColumns = showSelectedGroupsOnly
    ? groupColumns.filter((group) => group.isSelected)
    : groupColumns;
  const visibleRows = editableRows
    .map((row, rowIndex) => ({ row, rowIndex }))
    .filter(({ row }) => {
      if (!showSelectedGroupsOnly) {
        return true;
      }
      return visibleGroupColumns.some(
        (group) => (row.groups[group.id] ?? "").trim().length > 0
      );
    });
  const gridSaveStatusMessage =
    saveState === "error" ? AUTO_SAVE_STATUS_COPY.error : "";
  const completionStatusMessage =
    confirmActiveMessage ||
    publishBlockingMessage ||
    "Confirm returns to Workbench without creating a new version when nothing changed.";

  const markUnsaved = (): void => {
    if (isLifecycleReadonly) {
      setConfirmActiveMessage(lifecycleReadonlyView.message);
      return;
    }
    setActiveAuthorityConfirmed(false);
    draftPersistence.markUnsaved();
  };
  const toggleGroupIncluded = (groupId: string, included: boolean): void => {
    markUnsaved();
    setGroupColumns((previous) =>
      previous.map((group) =>
        group.id === groupId ? { ...group, isSelected: included } : group
      )
    );
    setSelectedGroupId(groupId);
    setSelectedRowId(null);
  };

  if ((!model.project && !model.error) || draftLoading) {
    return <></>;
  }

  const pushSnapshot = (): void => {
    setUndoStack((previous) => [
      ...previous,
      {
        rows: cloneRows(editableRows),
        groups: cloneGroups(groupColumns),
        schedulePlan,
      }
    ]);
  };

  const getSelectedRowIndex = (): number => editableRows.findIndex((row) => row.id === selectedRowId);

  const updateTextField = (
    rowIndex: number,
    field: keyof Omit<EditableMatrixRow, "groups" | "id">,
    value: string
  ): void => {
    markUnsaved();
    setEditableRows((previous) =>
      previous.map((row, index) => (index === rowIndex ? { ...row, [field]: value } : row))
    );
  };

  const updateGroupField = (rowIndex: number, groupId: string, value: string): void => {
    markUnsaved();
    setEditableRows((previous) =>
      previous.map((row, index) =>
        index === rowIndex
          ? {
              ...row,
              groups: {
                ...row.groups,
                [groupId]: value
              }
            }
          : row
      )
    );
  };

  const updateGroupName = (groupId: string, name: string): void => {
    markUnsaved();
    setGroupColumns((previous) =>
      previous.map((group) => (group.id === groupId ? { ...group, name } : group))
    );
  };

  const updateStepOutputOverride = (
    key: string,
    field: keyof StepOutputOverride,
    value: string
  ): void => {
    setStepOutputOverrides((previous) => ({
      ...previous,
      [key]: {
        ...previous[key],
        [field]: value
      }
    }));
  };

  const addRow = (): void => {
    markUnsaved();
    pushSnapshot();
    setEditableRows((previous) => [...previous, buildEmptyRow(groupColumns.map((group) => group.id), previous.length)]);
    setLastMessage("Test item row added");
  };

  const insertRow = (rowIndex: number, direction: "above" | "below"): void => {
    markUnsaved();
    pushSnapshot();
    const insertAt = direction === "above" ? rowIndex : rowIndex + 1;
    setEditableRows((previous) => {
      const next = [...previous];
      next.splice(insertAt, 0, buildEmptyRow(groupColumns.map((group) => group.id), insertAt));
      return next;
    });
    setLastMessage(direction === "above" ? "Row inserted above" : "Row inserted below");
  };

  const duplicateRow = (rowIndex: number): void => {
    markUnsaved();
    pushSnapshot();
    setEditableRows((previous) => {
      const next = [...previous];
      const source = previous[rowIndex];
      const duplicated: EditableMatrixRow = {
        ...source,
        id: `matrix-row-copy-${Date.now()}-${rowIndex}`,
        draftRowId: null,
        sourceRowSnapshotId: null,
        groups: { ...source.groups }
      };
      next.splice(rowIndex + 1, 0, duplicated);
      return next;
    });
    setLastMessage("Row duplicated");
  };

  const deleteRow = (rowIndex: number): void => {
    if (editableRows[rowIndex]?.sourceRowSnapshotId) {
      setLastMessage("Source test item cannot be deleted");
      return;
    }
    if (editableRows.length <= 1) {
      setLastMessage("At least one test item row is required");
      return;
    }
    markUnsaved();
    pushSnapshot();
    const deletingId = editableRows[rowIndex].id;
    setEditableRows((previous) => previous.filter((row) => row.id !== deletingId));
    setSelectedRowId((previous) => (previous === deletingId ? null : previous));
    setLastMessage("Row deleted");
  };

  const moveRow = (rowIndex: number, direction: "up" | "down"): void => {
    if (direction === "up" && rowIndex === 0) {
      setLastMessage("First row cannot move up");
      return;
    }
    if (direction === "down" && rowIndex === editableRows.length - 1) {
      setLastMessage("Last row cannot move down");
      return;
    }
    markUnsaved();
    pushSnapshot();
    setEditableRows((previous) => {
      const next = [...previous];
      const target = direction === "up" ? rowIndex - 1 : rowIndex + 1;
      const [row] = next.splice(rowIndex, 1);
      next.splice(target, 0, row);
      return next;
    });
    setLastMessage(direction === "up" ? "Row moved up" : "Row moved down");
  };

  const addGroup = (): void => {
    markUnsaved();
    pushSnapshot();
    const nextId = nextGroupId(groupColumns);
    setGroupColumns((previous) => [
      ...previous,
      {
        id: nextId,
        name: "",
        draftGroupId: null,
        sourceGroupSnapshotId: null,
        groupKey: `g${previous.length + 1}`,
        isSelected: true,
        isSourceBacked: false,
        sampleNote: null,
      },
    ]);
    setEditableRows((previous) =>
      previous.map((row) => ({
        ...row,
        groups: {
          ...row.groups,
          [nextId]: ""
        }
      }))
    );
    setLastMessage("Group column added");
  };

  const insertGroup = (groupId: string, direction: "left" | "right"): void => {
    const currentIndex = groupColumns.findIndex((group) => group.id === groupId);
    if (currentIndex < 0) {
      return;
    }
    markUnsaved();
    pushSnapshot();
    const nextId = nextGroupId(groupColumns);
    const insertAt = direction === "left" ? currentIndex : currentIndex + 1;
    setGroupColumns((previous) => {
      const next = [...previous];
      next.splice(insertAt, 0, {
        id: nextId,
        name: "",
        draftGroupId: null,
        sourceGroupSnapshotId: null,
        groupKey: `g${insertAt + 1}`,
        isSelected: true,
        isSourceBacked: false,
        sampleNote: null,
      });
      return next;
    });
    setEditableRows((previous) =>
      previous.map((row) => ({
        ...row,
        groups: {
          ...row.groups,
          [nextId]: ""
        }
      }))
    );
    setLastMessage("Group column inserted");
  };

  const duplicateGroup = (groupId: string): void => {
    const currentIndex = groupColumns.findIndex((group) => group.id === groupId);
    if (currentIndex < 0) {
      return;
    }
    markUnsaved();
    pushSnapshot();
      const sourceGroup = groupColumns[currentIndex];
      const nextId = nextGroupId(groupColumns);
      setGroupColumns((previous) => {
        const next = [...previous];
      next.splice(currentIndex + 1, 0, {
        id: nextId,
        name: sourceGroup.name,
        draftGroupId: null,
        sourceGroupSnapshotId: null,
        groupKey: sourceGroup.groupKey,
        isSelected: sourceGroup.isSelected,
        isSourceBacked: false,
        sampleNote: sourceGroup.sampleNote,
      });
        return next;
      });
    setEditableRows((previous) =>
      previous.map((row) => ({
        ...row,
        groups: {
          ...row.groups,
          [nextId]: row.groups[groupId]
        }
      }))
    );
    setLastMessage("Group column duplicated");
  };

  const deleteGroup = (groupId: string): void => {
    const targetGroup = groupColumns.find((group) => group.id === groupId);
    if (targetGroup?.isSourceBacked) {
      toggleGroupIncluded(groupId, false);
      setLastMessage("Source group excluded");
      return;
    }
    if (groupColumns.length <= 1) {
      setLastMessage("At least one group column is required");
      return;
    }
    markUnsaved();
    pushSnapshot();
    setGroupColumns((previous) => previous.filter((group) => group.id !== groupId));
    setEditableRows((previous) =>
      previous.map((row) => {
        const groups = { ...row.groups };
        delete groups[groupId];
        return { ...row, groups };
      })
    );
    setSelectedGroupId((previous) => (previous === groupId ? null : previous));
    setLastMessage("Group column deleted");
  };

  const setRowSampleClassification = (rowIndex: number, isSampleRow: boolean): void => {
    markUnsaved();
    setEditableRows((previous) =>
      previous.map((row, index) => (index === rowIndex ? { ...row, isSampleRow } : row))
    );
  };

  const includeSourceGroup = (groupId: string): void => {
    toggleGroupIncluded(groupId, true);
    setLastMessage("Source group included");
  };

  const moveGroup = (groupId: string, direction: "left" | "right"): void => {
    const currentIndex = groupColumns.findIndex((group) => group.id === groupId);
    if (currentIndex < 0) {
      return;
    }
    if (direction === "left" && currentIndex === 0) {
      setLastMessage("First group cannot move left");
      return;
    }
    if (direction === "right" && currentIndex === groupColumns.length - 1) {
      setLastMessage("Last group cannot move right");
      return;
    }
    markUnsaved();
    pushSnapshot();
    setGroupColumns((previous) => {
      const next = [...previous];
      const target = direction === "left" ? currentIndex - 1 : currentIndex + 1;
      const [item] = next.splice(currentIndex, 1);
      next.splice(target, 0, item);
      return next;
    });
    setLastMessage(direction === "left" ? "Group column moved left" : "Group column moved right");
  };

  const openRowContextMenu = (event: MouseEvent, rowIndex: number): void => {
    event.preventDefault();
    if (isLifecycleReadonly) {
      setConfirmActiveMessage(lifecycleReadonlyView.message);
      return;
    }
    setSelectedRowId(editableRows[rowIndex].id);
    setSelectedGroupId(null);
    setContextMenu({ kind: "row", rowIndex, x: event.clientX, y: event.clientY });
  };

  const openGroupContextMenu = (event: MouseEvent, groupId: string): void => {
    event.preventDefault();
    if (isLifecycleReadonly) {
      setConfirmActiveMessage(lifecycleReadonlyView.message);
      return;
    }
    setSelectedGroupId(groupId);
    setSelectedRowId(null);
    setContextMenu({ kind: "group", groupId, x: event.clientX, y: event.clientY });
  };

  const runContextAction = (action: () => void): void => {
    if (isLifecycleReadonly) {
      setConfirmActiveMessage(lifecycleReadonlyView.message);
      setContextMenu(null);
      return;
    }
    action();
    setContextMenu(null);
  };

  const selectRow = (rowId: string): void => {
    setSelectedRowId(rowId);
    setSelectedGroupId(null);
    setContextMenu(null);
  };

  const selectGroup = (groupId: string): void => {
    setSelectedGroupId(groupId);
    setSelectedRowId(null);
    setContextMenu(null);
  };

  const onGenerateTestRecordPreview = async (): Promise<void> => {
    if (isLifecycleReadonly) {
      setTestRecordState("error");
      setTestRecordMessage(lifecycleReadonlyView.message);
      return;
    }
    if (!canGenerateTestRecord) {
      setTestRecordState("error");
      setTestRecordMessage(
        hasStepTokenError
          ? "Fix Matrix step numbering before generating a Test Record preview."
          : "Select at least one group with Matrix steps before generating a Test Record preview."
      );
      return;
    }
    setTestRecordState("loading");
    setTestRecordConflict(null);
    setTestRecordMessage("Checking Test Record destination...");
    try {
      const preview = await previewMatrixEditorTestRecordPublication(
        projectId,
        testRecordDraftRequest
      );
      if (preview.status === "blocked") {
        throw new Error(preview.blockers[0] ?? "Test Record cannot be saved.");
      }
      if (preview.mode === "download") {
        const response = await generateMatrixEditorTestRecordDraftDownload(
          projectId,
          testRecordDraftRequest
        );
        triggerBlobDownload(
          response.blob,
          response.fileName ?? `${projectId} Test Record Preview - Unconfirmed Matrix draft.docx`
        );
        setTestRecordState("success");
        setTestRecordMessage("Downloaded unconfirmed Test Record preview.");
        return;
      }
      if (preview.status === "conflict") {
        setTestRecordConflict(preview);
        setTestRecordState("idle");
        setTestRecordMessage("An existing Test Record needs a replacement choice.");
        return;
      }
      const result = await publishMatrixEditorTestRecord(projectId, {
        ...testRecordDraftRequest,
        preview_token: preview.preview_token,
        conflict_action: "none",
      });
      setTestRecordState("success");
      setTestRecordMessage(`Saved ${result.file_name} to Test results.`);
    } catch (error) {
      setTestRecordState("error");
      setTestRecordMessage(
        parseRequestError(error, "Failed to generate Test Record preview.")
      );
    }
  };

  const resolveTestRecordConflict = async (
    action: "archive" | "recycle"
  ): Promise<void> => {
    if (!testRecordConflict) {
      return;
    }
    setTestRecordState("loading");
    setTestRecordMessage(
      action === "archive"
        ? "Archiving the existing Test Record..."
        : "Moving the existing Test Record to Recycle Bin..."
    );
    try {
      const result = await publishMatrixEditorTestRecord(projectId, {
        ...testRecordDraftRequest,
        preview_token: testRecordConflict.preview_token,
        conflict_action: action,
      });
      setTestRecordConflict(null);
      setTestRecordState("success");
      setTestRecordMessage(
        action === "archive" && result.archive_path
          ? `Saved ${result.file_name}; archived the previous file in History.`
          : `Saved ${result.file_name} to Test results.`
      );
    } catch (error) {
      setTestRecordState("error");
      setTestRecordMessage(
        parseRequestError(error, "Failed to replace the existing Test Record.")
      );
    }
  };

  const onGenerateTestStatusPreview = async (): Promise<void> => {
    if (isLifecycleReadonly) {
      setTestStatusState("error");
      setTestStatusMessage(lifecycleReadonlyView.message);
      return;
    }
    if (!canGenerateTestStatus) {
      setTestStatusState("error");
      setTestStatusMessage("Select at least one Matrix group before generating Test Status.");
      return;
    }
    setTestStatusState("loading");
    setTestStatusMessage("Generating Test Status draft...");
    try {
      const response = await generateMatrixEditorTestStatusDraftDownload(projectId, {
        ...testRecordDraftRequest,
        project_reference: projectReference,
      });
      triggerBlobDownload(
        response.blob,
        response.fileName ?? `${projectId} test status.xlsx`
      );
      setTestStatusState("success");
      setTestStatusMessage("Downloaded Test Status draft.");
    } catch (error) {
      setTestStatusState("error");
      setTestStatusMessage(parseRequestError(error, "Failed to generate Test Status draft."));
    }
  };

  const onConfirmMatrix = async (): Promise<void> => {
    if (isLifecycleReadonly) {
      setConfirmActiveMessage(lifecycleReadonlyView.message);
      return;
    }
    if (!canPublishActiveMatrix) {
      if (
        publishDisabledReason &&
        publishDisabledReason !== "Sample quantity is required for selected groups."
      ) {
        setConfirmActiveMessage(publishDisabledReason);
      }
      return;
    }
    const handleConfirmResponse = (
      response: MatrixEditorSessionConfirmResponse
    ): void => {
      if (response.publish_status === "no_change") {
        setConfirmActiveState("idle");
        setConfirmActiveMessage(response.message);
        draftPersistence.acceptNoChange(currentSaveSignature);
        onBackToWorkbench();
        return;
      }
      setConfirmActiveState("success");
      setActiveAuthorityConfirmed(true);
      setConfirmActiveMessage(response.message);
      onBackToWorkbench();
    };
    setConfirmActiveState("loading");
    setConfirmActiveMessage("Confirming matrix...");
    try {
      const response: MatrixEditorSessionConfirmResponse =
        await confirmMatrixEditorSession(
          projectId,
          draftPersistence.buildConfirmRequest(
            MVP_REVISION_CONFIRMED_BY,
            activeConfirmedMatrixId,
            activeConfirmedRevision
          )
        );
      handleConfirmResponse(response);
    } catch (error) {
      if (
        error instanceof ApiRequestError &&
        error.status === 409 &&
        error.detail &&
        typeof error.detail === "object" &&
        "code" in error.detail &&
        (error.detail as { code?: unknown }).code === "active_matrix_changed"
      ) {
        try {
          const latestSeed = await fetchMatrixEditorSession(projectId);
          if (latestSeed.active_confirmed_matrix_id) {
            draftPersistence.observeAuthority(
              latestSeed.active_confirmed_matrix_id,
              latestSeed.active_confirmed_revision ?? null
            );
            const retryResponse = await confirmMatrixEditorSession(
              projectId,
              draftPersistence.buildConfirmRequest(
                MVP_REVISION_CONFIRMED_BY,
                latestSeed.active_confirmed_matrix_id,
                latestSeed.active_confirmed_revision ?? null
              )
            );
            handleConfirmResponse(retryResponse);
            return;
          }
        } catch (retryError) {
          console.warn("Matrix confirm retry did not publish; returning to Workbench with latest authority.", retryError);
        }
        onBackToWorkbench();
        return;
      }
      setConfirmActiveState("error");
      setConfirmActiveMessage(parseRequestError(error, "Confirm failed."));
    }
  };
  const contextMenuGroup =
    contextMenu?.kind === "group"
      ? groupColumns.find((group) => group.id === contextMenu.groupId) ?? null
      : null;
  const contextMenuRow =
    contextMenu?.kind === "row" ? editableRows[contextMenu.rowIndex] ?? null : null;

  return (
    <section className="workbench-page matrix-editor-shell matrix-editor-target-shell" onClick={() => setContextMenu(null)}>
      <section className="matrix-editor-target-header">
        <p className="matrix-editor-project-identity matrix-editor-target-title-compact" title={matrixEditorIdentityLine}>
          {matrixEditorIdentityLine}
        </p>
        <div className="matrix-editor-target-actions">
          {currentSourceDocumentName ? (
            <span
              className="matrix-editor-source-document-name"
              title={currentSourceDocumentName}
            >
              {currentSourceDocumentName}
            </span>
          ) : null}
          <button
            type="button"
            disabled={isLifecycleReadonly}
            title={isLifecycleReadonly ? lifecycleReadonlyView.message : undefined}
            onClick={() => void matrixImport.chooseSource()}
          >
            Import Matrix
          </button>
          <MatrixEditorXlsxExportButton
            disabledReason={matrixXlsxExportDisabledReason}
            busy={matrixXlsxExport.busy}
            onExport={() => {
              if (!matrixXlsxExportDisabledReason) {
                void matrixXlsxExport.exportSnapshot(matrixXlsxExportRequest);
              }
            }}
          />
          <button
            type="button"
            disabled={
              isLifecycleReadonly || !canGenerateTestRecord || testRecordState === "loading"
            }
            title={isLifecycleReadonly ? lifecycleReadonlyView.message : undefined}
            onClick={() => void onGenerateTestRecordPreview()}
          >
            {testRecordState === "loading" ? "Generating..." : "Test record"}
          </button>
          <button
            type="button"
            disabled={
              isLifecycleReadonly || !canGenerateTestStatus || testStatusState === "loading"
            }
            title={isLifecycleReadonly ? lifecycleReadonlyView.message : undefined}
            onClick={() => void onGenerateTestStatusPreview()}
          >
            {testStatusState === "loading" ? "Generating..." : "Test Status"}
          </button>
        </div>
      </section>

      {isLifecycleReadonly ? (
        <div className="matrix-editor-state-banner" role="status">
          <strong>{lifecycleReadonlyView.title}</strong>
          <span>{lifecycleReadonlyView.message}</span>
        </div>
      ) : null}

      {testRecordMessage ? (
        <section
          className={`matrix-editor-save-status${
            testRecordState === "error" ? " matrix-editor-save-status-error" : ""
          }`}
        >
          {testRecordMessage}
        </section>
      ) : null}
      {testRecordConflict ? (
        <section
          aria-describedby="test-record-conflict-description"
          aria-labelledby="test-record-conflict-title"
          aria-modal="true"
          className="matrix-editor-test-record-conflict-backdrop"
          role="alertdialog"
        >
          <article className="matrix-editor-test-record-conflict-panel">
            <h3 id="test-record-conflict-title">Replace existing Test Record?</h3>
            <p id="test-record-conflict-description">
              A file with the same name already exists in Test results. Choose what to do
              with the existing Word document before the new version is saved.
            </p>
            {testRecordConflict.existing_modified_at ? (
              <p className="fine-print">
                Existing file modified: {new Date(testRecordConflict.existing_modified_at).toLocaleString()}
              </p>
            ) : null}
            <div className="matrix-editor-test-record-conflict-actions">
              <button
                type="button"
                disabled={testRecordState === "loading"}
                onClick={() => void resolveTestRecordConflict("archive")}
              >
                Archive old file
              </button>
              <button
                type="button"
                disabled={testRecordState === "loading"}
                onClick={() => void resolveTestRecordConflict("recycle")}
              >
                Move old file to Recycle Bin
              </button>
              <button
                type="button"
                disabled={testRecordState === "loading"}
                onClick={() => {
                  setTestRecordConflict(null);
                  setTestRecordState("idle");
                  setTestRecordMessage("Test Record replacement cancelled.");
                }}
              >
                Cancel
              </button>
            </div>
          </article>
        </section>
      ) : null}
      {testStatusMessage ? (
        <section
          className={`matrix-editor-save-status${
            testStatusState === "error" ? " matrix-editor-save-status-error" : ""
          }`}
        >
          {testStatusMessage}
        </section>
      ) : null}
      {matrixXlsxExport.error || matrixXlsxExport.message ? (
        <section
          className={`matrix-editor-save-status${
            matrixXlsxExport.error ? " matrix-editor-save-status-error" : ""
          }`}
          role="status"
        >
          {matrixXlsxExport.error || matrixXlsxExport.message}
        </section>
      ) : null}
      <input
        ref={matrixImport.fileInputRef}
        accept=".pdf,.doc,.docx"
        disabled={isLifecycleReadonly || matrixImport.actionBusy}
        style={{ display: "none" }}
        type="file"
        onChange={(event) => void matrixImport.onFileChange(event)}
      />
      {matrixImport.openingPreview ? (
        <section
          aria-describedby="matrix-import-opening-description"
          aria-labelledby="matrix-import-opening-title"
          aria-modal="true"
          className="matrix-editor-import-opening-backdrop"
          role="alertdialog"
        >
          <article className="matrix-editor-import-opening-panel" aria-busy="true">
            <div className="matrix-editor-import-opening-spinner" aria-hidden="true" />
            <div className="matrix-editor-import-opening-copy">
              <h3 id="matrix-import-opening-title">Searching for Matrix</h3>
              <p id="matrix-import-opening-description">
                ConnLab is reading the source document and preparing the preview.
              </p>
            </div>
          </article>
        </section>
      ) : null}
      {importSourcePicker ? (
        <MatrixImportSourceCandidatePicker
          candidates={importSourcePicker.candidates}
          sourceTitle={importSourcePicker.sourceTitle}
          loading={importSourcePicker.loading}
          previewBusy={importSourcePicker.previewBusy}
          error={importSourcePicker.error}
          onCancel={importSourcePicker.close}
          onUploadOtherFile={importSourcePicker.uploadOtherFile}
          onUseCandidate={(sourceAssetId) => void importSourcePicker.preview(sourceAssetId)}
        />
      ) : null}
      {importDialog ? (
        <MatrixImportDialog dialog={importDialog} readOnly={isLifecycleReadonly} />
      ) : null}
      <MatrixImportStandardVersionChoiceDialog
        busy={matrixImport.standardVersionChoice.busy}
        error={matrixImport.standardVersionChoice.error}
        onChooseFile={() => void matrixImport.standardVersionChoice.chooseFile()}
        onClose={matrixImport.standardVersionChoice.close}
        onSkip={() => void matrixImport.standardVersionChoice.skip()}
        open={matrixImport.standardVersionChoice.isOpen}
      />
      {matrixImport.commitMessage ? (
        <p aria-live="polite" className="matrix-editor-import-status-success" role="status">
          {matrixImport.commitMessage}
        </p>
      ) : null}
      {matrixImport.commitWarning ? (
        <p aria-live="polite" className="matrix-editor-import-status-warning" role="status">
          {matrixImport.commitWarning}
        </p>
      ) : null}
      <section className="matrix-editor-studio">
        <section className="matrix-editor-grid-surface">
          <div className="matrix-editor-main-table-wrap">
            <div className="matrix-editor-grid-controls">
              <label className="matrix-editor-filter-toggle">
                <input
                  aria-label="Show selected groups only"
                  type="checkbox"
                  checked={showSelectedGroupsOnly}
                  disabled={isLifecycleReadonly}
                  onChange={(event) => setShowSelectedGroupsOnly(event.target.checked)}
                />
                Show selected groups only
              </label>
              {gridSaveStatusMessage ? (
                <span className="matrix-editor-grid-save-error" role="status">
                  {gridSaveStatusMessage}
                </span>
              ) : null}
            </div>
            <table className="matrix-editor-main-table">
              <thead>
                <tr>
                  <th className="matrix-editor-row-selector-head">No.</th>
                  <th>Test Item</th>
                  <th>Section</th>
                  <th>Method</th>
                  <th>Condition</th>
                  <th>Requirement</th>
                  <th>Day</th>
                  {visibleGroupColumns.map((group) => (
                    <th
                      className={`matrix-editor-group-band${selectedGroupId === group.id ? " matrix-editor-group-selected" : ""}`}
                      key={group.id}
                      onClick={() => selectGroup(group.id)}
                      onContextMenu={(event) => openGroupContextMenu(event, group.id)}
                    >
                      <div className="matrix-editor-group-header-content">
                        {!showSelectedGroupsOnly ? (
                          <label className="matrix-editor-group-include-control">
                            <input
                              aria-label={`Include group ${group.name || group.groupKey}`}
                              type="checkbox"
                              checked={group.isSelected}
                              disabled={isLifecycleReadonly}
                              onChange={(event) => {
                                event.stopPropagation();
                                toggleGroupIncluded(group.id, event.target.checked);
                              }}
                            />
                          </label>
                        ) : null}
                        <input
                          className={`matrix-editor-group-name-input${group.name.trim() === "" ? " is-empty" : ""}${duplicateGroupIds.has(group.id) ? " is-duplicate" : ""}`}
                          disabled={isLifecycleReadonly}
                          type="text"
                          value={group.name}
                          onClick={(event) => {
                            event.stopPropagation();
                            setSelectedGroupId(group.id);
                            setSelectedRowId(null);
                            setContextMenu(null);
                          }}
                          onFocus={() => {
                            setSelectedGroupId(group.id);
                            setSelectedRowId(null);
                            setContextMenu(null);
                          }}
                          onChange={(event) => updateGroupName(group.id, event.target.value)}
                        />
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {visibleRows.map(({ row, rowIndex }) => (
                  (() => {
                    const rowHasNoGroupSteps = visibleGroupColumns.every((group) => (row.groups[group.id] ?? "").trim() === "");
                    const rowNeedsStepWarning = !row.isSampleRow && rowHasNoGroupSteps;
                    return (
                      <tr
                        className={`${selectedRowId === row.id ? "matrix-editor-row-selected" : ""}${row.isSampleRow ? " matrix-editor-row-sample" : ""}`.trim() || undefined}
                        key={row.id}
                      >
                        <td className="matrix-editor-row-selector-cell">
                          <button
                            type="button"
                            className={`matrix-editor-row-selector-button${rowNeedsStepWarning ? " is-step-missing" : ""}${row.isSampleRow ? " is-sample-row" : ""}`}
                            aria-label={row.isSampleRow ? `Select sample/instruction row ${rowIndex + 1}` : `Select row ${rowIndex + 1}`}
                            title={rowHasNoGroupSteps ? "Missing step number" : undefined}
                            onClick={() => selectRow(row.id)}
                            onContextMenu={(event) => openRowContextMenu(event, rowIndex)}
                          >
                            {row.isSampleRow ? "Info" : rowIndex + 1}
                          </button>
                        </td>
                        <td>
                          <MatrixAutoGrowTextarea
                            ariaLabel={`Row ${rowIndex + 1} test item`}
                            className={!row.isSampleRow && row.item.trim() === "" ? "is-empty-required" : undefined}
                            disabled={isLifecycleReadonly}
                            value={row.item}
                            onChange={(value) => updateTextField(rowIndex, "item", value)}
                          />
                        </td>
                        <td>
                          <MatrixAutoGrowTextarea
                            ariaLabel={`Row ${rowIndex + 1} section`}
                            disabled={isLifecycleReadonly}
                            value={row.section}
                            onChange={(value) => updateTextField(rowIndex, "section", value)}
                          />
                        </td>
                        <td>
                          <MatrixAutoGrowTextarea
                            ariaLabel={`Row ${rowIndex + 1} method`}
                            className={!row.isSampleRow && row.method.trim() === "" ? "is-empty-required" : undefined}
                            disabled={isLifecycleReadonly}
                            value={row.method}
                            onChange={(value) => updateTextField(rowIndex, "method", value)}
                          />
                        </td>
                        <td>
                          <MatrixAutoGrowTextarea
                            ariaLabel={`Row ${rowIndex + 1} condition`}
                            className={!row.isSampleRow && row.condition.trim() === "" ? "is-empty-required" : undefined}
                            disabled={isLifecycleReadonly}
                            value={row.condition}
                            onChange={(value) => updateTextField(rowIndex, "condition", value)}
                          />
                        </td>
                        <td>
                          <MatrixAutoGrowTextarea
                            ariaLabel={`Row ${rowIndex + 1} requirement`}
                            className={!row.isSampleRow && row.requirement.trim() === "" ? "is-empty-required" : undefined}
                            disabled={isLifecycleReadonly}
                            value={row.requirement}
                            onChange={(value) => updateTextField(rowIndex, "requirement", value)}
                          />
                        </td>
                        <td>
                          <MatrixAutoGrowTextarea
                            ariaLabel={`Row ${rowIndex + 1} day`}
                            className={scheduleCalculation.rowErrors[row.id] ? "is-invalid" : undefined}
                            disabled={isLifecycleReadonly}
                            errorMessage={scheduleCalculation.rowErrors[row.id]}
                            value={row.dayExpression}
                            onChange={(value) => updateTextField(rowIndex, "dayExpression", value)}
                          />
                        </td>
                        {visibleGroupColumns.map((group) => {
                          const cellKey = `${group.id}-${rowIndex}`;
                          const cellErrorMessage = stepCellErrorMessageByKey.get(cellKey) ?? "";
                          const groupCellClass = `matrix-editor-inline-input${
                            invalidStepFormatCellKeys.has(cellKey) || groupStepSequenceErrorCellKeys.has(cellKey)
                              ? " is-invalid"
                                : ""
                          }`;
                          return (
                            <td
                              className={selectedGroupId === group.id ? "matrix-editor-group-selected-cell" : undefined}
                              key={`${group.id}-${rowIndex}`}
                            >
                              <MatrixAutoGrowTextarea
                                ariaLabel={`Row ${rowIndex + 1} ${group.name || "Group"}`}
                                className={groupCellClass}
                                disabled={isLifecycleReadonly}
                                errorMessage={cellErrorMessage}
                                value={row.groups[group.id] ?? ""}
                                onFocus={() => {
                                  setSelectedGroupId(group.id);
                                  setSelectedRowId(null);
                                  setContextMenu(null);
                                }}
                                onChange={(value) => {
                                  markUnsaved();
                                  setSelectedGroupId(group.id);
                                  updateGroupField(rowIndex, group.id, value);
                                }}
                              />
                            </td>
                          );
                        })}
                      </tr>
                    );
                  })()
                ))}
                <tr>
                  <td />
                  <td className="matrix-editor-sample-label-cell">Samples Quantity (PCS)</td>
                  <td />
                  <td />
                  <td />
                  <td />
                  <td />
                  {visibleGroupColumns.map((group) => (
                    <td key={`sample-${group.id}`}>
                      <MatrixAutoGrowTextarea
                        ariaLabel={`Samples ${group.name || "group"}`}
                        className={`matrix-editor-sample-textarea${invalidSelectedSampleGroupIds.has(group.id) ? " is-invalid" : ""}`}
                        disabled={isLifecycleReadonly}
                        value={sampleValues[group.id] ?? ""}
                        onFocus={() => {
                          setSelectedGroupId(group.id);
                          setSelectedRowId(null);
                          setContextMenu(null);
                        }}
                        onChange={(value) => {
                          markUnsaved();
                          setSampleValues((previous) => ({ ...previous, [group.id]: value }));
                          setSampleMergeNotes((previous) => {
                            const { [group.id]: _removed, ...next } = previous;
                            return next;
                          });
                        }}
                      />
                    </td>
                  ))}
                </tr>
                <tr className="matrix-editor-test-days-row">
                  <td />
                  <td className="matrix-editor-sample-label-cell">Test Days</td>
                  <td />
                  <td />
                  <td />
                  <td />
                  <td />
                  {visibleGroupColumns.map((group) => (
                    <td key={`days-${group.id}`}>
                      {group.isSelected ? `${formatPlanningDays(scheduleCalculation.groupDays[group.id] ?? 0)} d` : ""}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
            {contextMenu ? (
              <div
                className="matrix-editor-context-menu"
                style={{ left: contextMenu.x, top: contextMenu.y }}
                onClick={(event) => event.stopPropagation()}
              >
                {contextMenu.kind === "row" ? (
                  <>
                    {contextMenuRow?.isSampleRow ? (
                      <button type="button" onClick={() => runContextAction(() => setRowSampleClassification(contextMenu.rowIndex, false))}>Mark as Test Item</button>
                    ) : (
                      <button type="button" onClick={() => runContextAction(() => setRowSampleClassification(contextMenu.rowIndex, true))}>Mark as Information</button>
                    )}
                    <button type="button" onClick={() => runContextAction(() => insertRow(contextMenu.rowIndex, "above"))}>Insert above</button>
                    <button type="button" onClick={() => runContextAction(() => insertRow(contextMenu.rowIndex, "below"))}>Insert below</button>
                    <button type="button" onClick={() => runContextAction(() => duplicateRow(contextMenu.rowIndex))}>Duplicate row</button>
                    <button
                      type="button"
                      disabled={contextMenu.rowIndex === 0}
                      title={contextMenu.rowIndex === 0 ? "First row cannot move up" : ""}
                      onClick={() => runContextAction(() => moveRow(contextMenu.rowIndex, "up"))}
                    >
                      Move up
                    </button>
                    <button
                      type="button"
                      disabled={contextMenu.rowIndex === editableRows.length - 1}
                      title={contextMenu.rowIndex === editableRows.length - 1 ? "Last row cannot move down" : ""}
                      onClick={() => runContextAction(() => moveRow(contextMenu.rowIndex, "down"))}
                    >
                      Move down
                    </button>
                    <button
                      type="button"
                      disabled={Boolean(contextMenuRow?.sourceRowSnapshotId) || editableRows.length <= 1}
                      title={
                        contextMenuRow?.sourceRowSnapshotId
                          ? "Source test item cannot be deleted"
                          : editableRows.length <= 1
                            ? "At least one test item row is required"
                            : ""
                      }
                      onClick={() => runContextAction(() => deleteRow(contextMenu.rowIndex))}
                    >
                      Delete row
                    </button>
                  </>
                ) : (
                  <>
                    <button type="button" onClick={() => runContextAction(() => insertGroup(contextMenu.groupId, "left"))}>Insert left</button>
                    <button type="button" onClick={() => runContextAction(() => insertGroup(contextMenu.groupId, "right"))}>Insert right</button>
                    <button
                      type="button"
                      onClick={() => runContextAction(() => duplicateGroup(contextMenu.groupId))}
                    >
                      Duplicate group
                    </button>
                    <button
                      type="button"
                      disabled={groupColumns.findIndex((group) => group.id === contextMenu.groupId) === 0}
                      title={groupColumns.findIndex((group) => group.id === contextMenu.groupId) === 0 ? "First group cannot move left" : ""}
                      onClick={() => runContextAction(() => moveGroup(contextMenu.groupId, "left"))}
                    >
                      Move left
                    </button>
                    <button
                      type="button"
                      disabled={groupColumns.findIndex((group) => group.id === contextMenu.groupId) === groupColumns.length - 1}
                      title={groupColumns.findIndex((group) => group.id === contextMenu.groupId) === groupColumns.length - 1 ? "Last group cannot move right" : ""}
                      onClick={() => runContextAction(() => moveGroup(contextMenu.groupId, "right"))}
                    >
                      Move right
                    </button>
                    {contextMenuGroup?.isSourceBacked ? (
                      <button
                        type="button"
                        onClick={() =>
                          runContextAction(() =>
                            contextMenuGroup.isSelected
                              ? deleteGroup(contextMenu.groupId)
                              : includeSourceGroup(contextMenu.groupId)
                          )
                        }
                      >
                        {contextMenuGroup.isSelected ? "Exclude group" : "Include group"}
                      </button>
                    ) : (
                      <button
                        type="button"
                        disabled={groupColumns.length <= 1}
                        title={groupColumns.length <= 1 ? "At least one group column is required" : ""}
                        onClick={() => runContextAction(() => deleteGroup(contextMenu.groupId))}
                      >
                        Delete group
                      </button>
                    )}
                  </>
                )}
              </div>
            ) : null}
          </div>
          <MatrixMethodVersionSyncPanel
            preview={methodVersionSync.preview}
            selectedRowIds={methodVersionSync.selectedRowIds}
            busy={methodVersionSync.busy}
            error={methodVersionSync.error}
            message={methodVersionSync.message}
            disabled={isLifecycleReadonly || draftLoading || !hasCurrentSavedDraft}
            onPreview={() => void methodVersionSync.previewMethods()}
            onToggle={methodVersionSync.toggleRow}
            onApply={() => void methodVersionSync.applySelected()}
          />
          <MatrixSchedulePlanningCard
            plan={schedulePlan}
            groups={groupColumns.map((group) => ({
              id: group.id,
              name: group.name || group.groupKey,
              isSelected: group.isSelected,
            }))}
            calculation={scheduleCalculation}
            readOnly={isLifecycleReadonly}
            onChange={(nextPlan) => {
              markUnsaved();
              setSchedulePlan(nextPlan);
            }}
          />
          {revisionDraftActionMessage ? (
            <p className="matrix-editor-revision-draft-message" role="status">
              {revisionDraftActionMessage}
            </p>
          ) : null}
          <ContactMeasurementPlanSummaryCard
            summary={pointProfileSummary.summary}
            loading={pointProfileSummary.loading}
            onOpenSetup={() => onOpenContactMeasurementSetup?.()}
          />
          <LlcrCrRecordWorkbookPanel
            projectId={projectId}
            draftRequest={testRecordDraftRequest}
          />
        </section>

        <MatrixStepWorkspace
          readOnly={isLifecycleReadonly}
          view={{
            groupName: selectedGroup ? selectedGroup.name || "Unnamed" : null,
            itemSectionNotes: selectedGroupItemSectionNotes,
            rows: selectedGroupStepRows,
            sampleNotes: selectedGroupSampleNotes,
            sampleValue: selectedGroupSamplesValue,
            stepNotes: dedupedSelectedGroupStepNotes,
          }}
          onChangeStep={updateStepOutputOverride}
          onChangeSample={(value) => {
            if (!selectedGroup) {
              return;
            }
            markUnsaved();
            setSampleValues((previous) => ({ ...previous, [selectedGroup.id]: value }));
            setSampleMergeNotes((previous) => {
              const { [selectedGroup.id]: _removed, ...next } = previous;
              return next;
            });
          }}
        />
      </section>
      <footer
        aria-label="Matrix editor completion actions"
        className="matrix-editor-completion-dock"
      >
        <span>{completionStatusMessage}</span>
        <div className="matrix-editor-completion-actions">
          <button type="button" onClick={() => void draftPersistence.cancel()}>
            Cancel
          </button>
          <button
            className="matrix-editor-primary-action"
            disabled={!canPublishActiveMatrix}
            title={isLifecycleReadonly ? lifecycleReadonlyView.message : undefined}
            type="button"
            onClick={() => void onConfirmMatrix()}
          >
            {confirmActiveState === "loading" ? "Confirming..." : "Confirm Matrix"}
          </button>
        </div>
      </footer>
    </section>
  );
}
