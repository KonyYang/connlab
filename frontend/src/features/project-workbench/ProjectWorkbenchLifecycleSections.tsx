import { useState, type ReactElement } from "react";
import type {
  ProjectOutputStatusSummary,
  ProjectTestPlanDraft,
  ProjectTestPlanDraftGroup,
  ProjectTestPlanDraftStep,
  TemporaryProjectDeletePreview,
} from "../../api/client";
import { ProjectWorkbenchCloseConfirmation } from "./ProjectWorkbenchCloseConfirmation";
import type {
  WorkbenchLifecycleActionsViewModel,
  WorkbenchLifecycleMode,
  WorkbenchLifecycleTab,
  WorkbenchLifecycleViewModel,
} from "./projectWorkbenchLifecycleSelectors";
import { ProjectFolderTaskList } from "./ProjectFolderTaskList";
import type {
  ProjectFolderTaskActionTarget,
  ProjectFolderTaskKey,
  ProjectFolderTaskRow,
} from "./projectFolderTaskSelectors";
import type { ProjectRuntimeConsoleModel } from "./useProjectRuntimeConsoleModel";

export type SetupMaterialItem = {
  title: string;
  value: string;
  status: "ready" | "warning" | "blocked" | "neutral";
};

export function WorkbenchStageBanner({
  lifecycle,
  onOpenMatrixEditor,
  onOpenFeeEvaluation,
  onRefreshPackagePreview,
  onCollectRequestMaterial,
  onRefreshOfficialFolderCheck,
  onRepairOfficialFolderStructure,
  onRefreshPublicDriveUploadPreview,
  onUploadPublicDriveProjectFolder,
  onOpenSettings,
}: {
  lifecycle: WorkbenchLifecycleViewModel;
  onOpenMatrixEditor: () => void;
  onOpenFeeEvaluation: () => void;
  onRefreshPackagePreview: () => void;
  onCollectRequestMaterial: () => Promise<void>;
  onRefreshOfficialFolderCheck: () => Promise<void>;
  onRepairOfficialFolderStructure: () => Promise<void>;
  onRefreshPublicDriveUploadPreview: () => Promise<void>;
  onUploadPublicDriveProjectFolder: () => Promise<void>;
  onOpenSettings: () => void;
}): ReactElement {
  const actionHandler = getNextActionHandler(
    lifecycle.nextAction.actionTarget,
    onOpenMatrixEditor,
    onOpenFeeEvaluation,
    onRefreshPackagePreview,
    onCollectRequestMaterial,
    onRefreshOfficialFolderCheck,
    onRepairOfficialFolderStructure,
    onRefreshPublicDriveUploadPreview,
    onUploadPublicDriveProjectFolder,
    onOpenSettings
  );
  return (
    <section
      className={`runtime-console-stage-banner status-${lifecycle.nextAction.tone}`}
      aria-label="Current project stage"
    >
      <div>
        <p className="eyebrow">Current stage</p>
        <h3>{lifecycle.stageLabel}</h3>
        <p>{lifecycle.stageSummary}</p>
      </div>
      <div className="runtime-console-next-action">
        <span>Next action</span>
        <strong>{lifecycle.nextAction.title}</strong>
        <p>{lifecycle.nextAction.reason}</p>
        {actionHandler && lifecycle.nextAction.actionLabel ? (
          <button type="button" onClick={actionHandler}>
            {lifecycle.nextAction.actionLabel}
          </button>
        ) : null}
      </div>
    </section>
  );
}

export function WorkbenchModeTabs({
  activeMode,
  tabs,
  onSelect,
}: {
  activeMode: WorkbenchLifecycleMode;
  tabs: WorkbenchLifecycleTab[];
  onSelect: (mode: WorkbenchLifecycleMode) => void;
}): ReactElement | null {
  if (tabs.length < 2) {
    return null;
  }
  return (
    <div className="runtime-console-mode-tabs" role="tablist" aria-label="Workbench mode">
      {tabs.map((tab) => (
        <button
          key={tab.mode}
          type="button"
          role="tab"
          aria-selected={activeMode === tab.mode}
          className={activeMode === tab.mode ? "is-active" : ""}
          disabled={tab.disabled}
          title={tab.reason}
          onClick={() => onSelect(tab.mode)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

export function ProjectOverviewMode({
  setupMaterials,
  lifecycle,
}: {
  setupMaterials: SetupMaterialItem[];
  lifecycle: WorkbenchLifecycleViewModel;
}): ReactElement {
  const blockers =
    lifecycle.nextAction.tone === "blocked" ? [lifecycle.nextAction.reason] : [];
  return (
    <section className="runtime-console-overview" aria-label="Project overview">
      <section className="runtime-console-overview-panel">
        <p className="eyebrow">Lifecycle summary</p>
        <h3>{lifecycle.stageLabel}</h3>
        <p>{lifecycle.stageSummary}</p>
      </section>
      <section className="runtime-console-readiness" aria-label="Overview readiness checklist">
        <div className="runtime-console-readiness-title">
          <p className="eyebrow">Project Folder</p>
          <strong>Controlled folder checklist</strong>
        </div>
        {setupMaterials.map((item) => (
          <RuntimeSetupItem key={item.title} item={item} />
        ))}
      </section>
      <section className="runtime-console-overview-panel">
        <p className="eyebrow">Current blockers</p>
        {blockers.length > 0 ? (
          <ul className="runtime-console-blocker-list">
            {blockers.map((blocker) => (
              <li key={blocker}>{blocker}</li>
            ))}
          </ul>
        ) : (
          <p>No blocking action is currently reported.</p>
        )}
      </section>
    </section>
  );
}

export function TemporaryPlanningMode({
  deletePreview,
  lifecycleError,
  lifecycleBusy,
  feePlanningAvailable,
  onOpenMatrixEditor,
  onOpenFeeEvaluation,
  onStartPromotion,
  onStopProject,
  onResumeProject,
  onCloseCompletedProject,
  onCloseAdministrativeProject,
  onDeleteTemporaryProject,
  promotionMessage,
  lifecycleActions,
  outputStatusSummary,
  projectIdentity,
  projectReference,
}: {
  deletePreview: TemporaryProjectDeletePreview | null;
  lifecycleError: string | null;
  lifecycleBusy: boolean;
  feePlanningAvailable: boolean;
  onOpenMatrixEditor: () => void;
  onOpenFeeEvaluation: () => void;
  onStartPromotion: () => void;
  onStopProject: (reason: string | null) => void;
  onResumeProject: (reason: string | null) => void;
  onCloseCompletedProject: (closeNote: string) => void;
  onCloseAdministrativeProject: (reason: string) => void;
  onDeleteTemporaryProject: () => void;
  promotionMessage: string | null;
  lifecycleActions: WorkbenchLifecycleActionsViewModel;
  outputStatusSummary: ProjectOutputStatusSummary | null;
  projectIdentity: string;
  projectReference: string | null;
}): ReactElement {
  return (
    <section className="runtime-console-mode-surface" aria-label="Temporary planning">
      <div className="runtime-console-mode-heading">
        <p className="eyebrow">Temporary Planning</p>
        <h3>Shape the request before formal registration</h3>
        <p>
          This project has no registered LTR Number yet. Matrix and Fee planning tools are
          available for feasibility, duration, and cost estimation. Official package actions require LTR registration.
        </p>
      </div>
      <div className="runtime-console-planning-actions">
        <article>
          <strong>Matrix planning</strong>
          <p>Review or draft the testing map that will become the execution authority later.</p>
          <button type="button" onClick={onOpenMatrixEditor}>
            Matrix planning
          </button>
        </article>
        <article>
          <strong>Fee expectation</strong>
          <p>
            {feePlanningAvailable
              ? "Open Fee Evaluation for pre-DL estimation from the available Matrix draft."
              : "Create or import a Matrix draft before opening Fee Evaluation for pre-DL estimation."}
          </p>
          <button
            type="button"
            disabled={!feePlanningAvailable}
            onClick={onOpenFeeEvaluation}
          >
            Open Fee Evaluation
          </button>
        </article>
        <article>
          <strong>Formal registration</strong>
          <p>
            Keep this temporary project intact when it is ready to enter the LTR workflow.
          </p>
          <button type="button" onClick={onStartPromotion}>
            Convert to Formal Project
          </button>
          {promotionMessage ? (
            <p className="runtime-console-inline-warning">{promotionMessage}</p>
          ) : null}
        </article>
      </div>
      <ProjectLifecycleManagementPanel
        allowDelete
        deletePreview={deletePreview}
        lifecycleActions={lifecycleActions}
        lifecycleBusy={lifecycleBusy}
        lifecycleError={lifecycleError}
        outputStatusSummary={outputStatusSummary}
        onDeleteTemporaryProject={onDeleteTemporaryProject}
        onStopProject={onStopProject}
        onResumeProject={onResumeProject}
        onCloseCompletedProject={onCloseCompletedProject}
        onCloseAdministrativeProject={onCloseAdministrativeProject}
        projectIdentity={projectIdentity}
        projectReference={projectReference}
      />
    </section>
  );
}

export function ProjectLifecycleManagementPanel({
  allowDelete,
  compactBottom = false,
  deletePreview,
  lifecycleActions,
  lifecycleBusy,
  lifecycleError,
  outputStatusSummary,
  onDeleteTemporaryProject,
  onStopProject,
  onResumeProject,
  onCloseCompletedProject,
  onCloseAdministrativeProject,
  projectIdentity,
  projectReference,
}: {
  allowDelete: boolean;
  compactBottom?: boolean;
  deletePreview: TemporaryProjectDeletePreview | null;
  lifecycleActions: WorkbenchLifecycleActionsViewModel;
  lifecycleBusy: boolean;
  lifecycleError: string | null;
  outputStatusSummary: ProjectOutputStatusSummary | null;
  onDeleteTemporaryProject: () => void;
  onStopProject: (reason: string | null) => void;
  onResumeProject: (reason: string | null) => void;
  onCloseCompletedProject: (closeNote: string) => void;
  onCloseAdministrativeProject: (reason: string) => void;
  projectIdentity: string;
  projectReference: string | null;
}): ReactElement | null {
  const [pendingAction, setPendingAction] =
    useState<WorkbenchLifecycleActionsViewModel["primaryAction"]>("none");
  const [reason, setReason] = useState("");
  const blockers = deletePreview?.blockers ?? [];
  const deleteAvailable = allowDelete && deletePreview?.can_delete === true;
  const deleteUnavailable = allowDelete && deletePreview?.can_delete === false;
  const visibleBlockers = blockers.map((blocker) =>
    getTemporaryDeleteBlockerCopy(blocker, allowDelete)
  );
  const deleteUnavailableCopy =
    "Temporary deletion is unavailable here. Stop the project if work should not continue.";
  const lifecycleTitle = lifecycleActions.canResume
    ? "Resume this project lifecycle"
    : deleteAvailable
      ? "Stop or safely remove this temporary record"
      : allowDelete
        ? "Stop this temporary project lifecycle"
        : "Stop this project lifecycle";
  const lifecycleDescription = lifecycleActions.canResume
    ? "Resume restores editing and project work after the stopped state is cleared."
    : deleteAvailable
      ? "Stop keeps the project for review. Delete is only available for mistaken or duplicate temporary records with no formal or temporary workspace blockers."
      : allowDelete
        ? deleteUnavailableCopy
        : "Stop keeps the project for review when business work should not continue.";
  const hasLifecycleAction =
    lifecycleActions.canStop || lifecycleActions.canResume || lifecycleActions.canClose;
  const hasPanelContent =
    hasLifecycleAction ||
    allowDelete ||
    blockers.length > 0 ||
    Boolean(lifecycleError);

  if (!hasPanelContent) {
    return null;
  }

  function handleConfirmAction(): void {
    const normalizedReason = reason.trim() || null;
    if (pendingAction === "stop") {
      onStopProject(normalizedReason);
    }
    if (pendingAction === "resume") {
      onResumeProject(normalizedReason);
    }
    setPendingAction("none");
    setReason("");
  }

  function handleCancelAction(): void {
    setPendingAction("none");
    setReason("");
  }

  return (
    <section
      className={`runtime-console-lifecycle-management${
        compactBottom ? " is-compact-bottom" : ""
      }`}
      aria-label="Project lifecycle"
    >
      {compactBottom ? null : (
        <div>
          <p className="eyebrow">Project lifecycle</p>
          <strong>{lifecycleTitle}</strong>
          <p>{lifecycleDescription}</p>
        </div>
      )}
      <div className="runtime-console-lifecycle-actions">
        {lifecycleActions.canStop ? (
          <button
            type="button"
            disabled={lifecycleBusy}
            onClick={() => setPendingAction("stop")}
          >
            Stop project
          </button>
        ) : null}
        {lifecycleActions.canResume ? (
          <button
            type="button"
            disabled={lifecycleBusy}
            onClick={() => setPendingAction("resume")}
          >
            Resume project
          </button>
        ) : null}
        {allowDelete ? (
          <button
            type="button"
            disabled={lifecycleBusy || !deletePreview?.can_delete}
            title={deleteUnavailable ? deleteUnavailableCopy : undefined}
            onClick={onDeleteTemporaryProject}
          >
            Delete temporary project
          </button>
        ) : null}
      </div>
      <ProjectWorkbenchCloseConfirmation
        compact={compactBottom}
        lifecycleActions={lifecycleActions}
        lifecycleBusy={lifecycleBusy}
        onCloseAdministrativeProject={onCloseAdministrativeProject}
        onCloseCompletedProject={onCloseCompletedProject}
        outputStatusSummary={outputStatusSummary}
        projectIdentity={projectIdentity}
        projectReference={projectReference}
      />
      {pendingAction !== "none" ? (
        <div className="runtime-console-lifecycle-confirmation">
          <strong>
            {pendingAction === "stop"
              ? "Confirm stop project"
              : "Confirm resume project"}
          </strong>
          <label>
            <span>Reason optional</span>
            <textarea
              value={reason}
              onChange={(event) => setReason(event.target.value)}
              rows={3}
            />
          </label>
          <div className="runtime-console-lifecycle-confirm-actions">
            <button
              type="button"
              disabled={lifecycleBusy}
              onClick={handleConfirmAction}
            >
              {pendingAction === "stop"
                ? "Confirm stop project"
                : "Confirm resume project"}
            </button>
            <button type="button" disabled={lifecycleBusy} onClick={handleCancelAction}>
              Cancel
            </button>
          </div>
        </div>
      ) : null}
      {!compactBottom && lifecycleActions.readonlyReason ? (
        <p className="runtime-console-readonly-note">
          {lifecycleActions.readonlyReason}
        </p>
      ) : null}
      {!compactBottom && visibleBlockers.length > 0 ? (
        <ul className="runtime-console-blocker-list">
          {visibleBlockers.map((blocker) => (
            <li key={blocker}>{blocker}</li>
          ))}
        </ul>
      ) : null}
      {lifecycleError ? (
        <p className="runtime-console-error">{lifecycleError}</p>
      ) : null}
    </section>
  );
}

export function RegisteredSetupMode({
  hasCandidateMatrix,
  onOpenMatrixEditor,
}: {
  hasCandidateMatrix: boolean;
  onOpenMatrixEditor: () => void;
}): ReactElement {
  return (
    <section className="runtime-console-mode-surface" aria-label="Matrix authority setup">
      <div className="runtime-console-mode-heading">
        <p className="eyebrow">Registered setup</p>
        <h3>Matrix authority missing</h3>
        <p>
          DL is registered. Edit the Matrix and publish the authority before enabling Test Record,
          Fee Evaluation, Section 2 dates, or package preparation.
        </p>
      </div>
      <div className="runtime-console-setup-focus">
        <strong>{hasCandidateMatrix ? "Candidate Matrix is available" : "No Matrix draft is active"}</strong>
        <p>
          Keep setup focused here: package preparation and step execution appear after an active
          Matrix is confirmed.
        </p>
        <button type="button" onClick={onOpenMatrixEditor}>
          Edit Matrix
        </button>
        <button type="button" onClick={onOpenMatrixEditor}>
          Confirm Matrix authority
        </button>
      </div>
    </section>
  );
}

function getTemporaryDeleteBlockerCopy(blocker: string, allowDelete: boolean): string {
  if (allowDelete && blocker === "Project is not a temporary planning project.") {
    return "Temporary deletion is unavailable here. Stop the project if work should not continue.";
  }
  return blocker;
}

export function NoMatrixWorkspaceEmptyState({
  currentFolderTask,
  matrixDraft,
}: {
  currentFolderTask: ProjectFolderTaskRow;
  matrixDraft: ProjectTestPlanDraft | null;
}): ReactElement {
  const draftPreview = buildNoMatrixDraftPreview(matrixDraft);
  return (
    <section
      className="runtime-console-no-matrix-empty"
      aria-label="No active Matrix workspace"
    >
      <div className="runtime-console-no-matrix-main">
        <table className="runtime-console-no-matrix-table">
          <thead>
            <tr>
              <th>No.</th>
              <th>Test Item</th>
              <th>Section</th>
              <th>Method</th>
              <th>Condition</th>
              <th>Requirement</th>
              <th>Day</th>
              {draftPreview.groupLabels.map((label, index) => (
                <th key={`${label}:${index}`}>{label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {draftPreview.rows.map((row, index) => (
              <tr key={row.key}>
                <td>
                  <span className="runtime-console-no-matrix-index">{index + 1}</span>
                </td>
                <th scope="row">{row.testItem}</th>
                <td>{row.section || ""}</td>
                <td>{row.method}</td>
                <td>{row.condition}</td>
                <td>{row.requirement}</td>
                <td>{row.day || ""}</td>
                {draftPreview.groupLabels.map((label, index) => (
                  <td key={`${row.key}:${label}:${index}`}>
                    {row.tokensByGroup[label] ? (
                      <span className="runtime-console-no-matrix-token">
                        {row.tokensByGroup[label]}
                      </span>
                    ) : (
                      <span className="runtime-console-matrix-empty-cell">-</span>
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="runtime-console-no-matrix-side">
        <aside className="runtime-console-step-workspace" aria-label="Step workspace">
          <header>
            <div>
              <p className="eyebrow">Step Workspace</p>
              <p className="runtime-console-step-breadcrumb">Matrix authority pending</p>
            </div>
          </header>
          <section className="runtime-console-step-status-card runtime-console-step-status-compact">
            <div>
              <span>Lifecycle status</span>
              <strong className="runtime-console-step-status-empty">Not available</strong>
            </div>
          </section>
        </aside>
        <section className="runtime-console-folder-inspector" aria-label="Folder Action">
          <p className="eyebrow">Folder Action</p>
          <h3>{currentFolderTask.title}</h3>
          <strong
            className={`runtime-console-folder-inspector-status status-${currentFolderTask.status}`}
          >
            {currentFolderTask.statusLabel}
          </strong>
        </section>
      </div>
    </section>
  );
}

type NoMatrixDraftPreviewRow = {
  key: string;
  testItem: string;
  section: string;
  method: string;
  condition: string;
  requirement: string;
  day: string;
  tokensByGroup: Record<string, string>;
};

function buildNoMatrixDraftPreview(
  matrixDraft: ProjectTestPlanDraft | null
): { groupLabels: string[]; rows: NoMatrixDraftPreviewRow[] } {
  const groups = matrixDraft?.payload.groups ?? [];
  if (groups.length === 0 || !groups.some((group) => (group.steps ?? []).length > 0)) {
    return buildStarterNoMatrixDraftPreview();
  }

  const groupLabels = groups.map((group, index) =>
    normalizeNoMatrixGroupLabel(group, `${index + 1}`)
  );
  const rowsByKey = new Map<string, NoMatrixDraftPreviewRow>();
  groups.forEach((group, groupIndex) => {
    const groupLabel = groupLabels[groupIndex];
    (group.steps ?? []).forEach((step, stepIndex) => {
      const row = toNoMatrixDraftRow(step, stepIndex);
      const existing = rowsByKey.get(row.key) ?? row;
      existing.tokensByGroup[groupLabel] = normalizeNoMatrixToken(step, stepIndex);
      rowsByKey.set(row.key, existing);
    });
  });
  const rows = Array.from(rowsByKey.values());
  return rows.length > 0 ? { groupLabels, rows } : buildStarterNoMatrixDraftPreview();
}

function buildStarterNoMatrixDraftPreview(): {
  groupLabels: string[];
  rows: NoMatrixDraftPreviewRow[];
} {
  return {
    groupLabels: ["1"],
    rows: [
      {
        key: "starter-visual-examination",
        testItem: "Visual Examination",
        section: "",
        method: "EIA-364-18B",
        condition: "10x min magnification",
        requirement: "No detrimental condition",
        day: "",
        tokensByGroup: { "1": "1" },
      },
    ],
  };
}

function toNoMatrixDraftRow(
  step: ProjectTestPlanDraftStep,
  stepIndex: number
): NoMatrixDraftPreviewRow {
  const testItem = normalizeNoMatrixCell(step.test_item ?? step.step_label, "Untitled test");
  const method = normalizeNoMatrixCell(step.method_summary ?? step.reference_standard, "-");
  const condition = normalizeNoMatrixCell(step.condition_summary, "-");
  const requirement = normalizeNoMatrixCell(step.judgement_criteria, "-");
  const day = normalizeNoMatrixCell(
    step.duration_hint ??
      step.estimated_duration_hint ??
      step.duration_days?.toString() ??
      step.estimated_duration_days?.toString(),
    ""
  );
  return {
    key: [
      testItem,
      step.source_section ?? "",
      method,
      condition,
      requirement,
      day,
      step.sequence?.toString() ?? stepIndex.toString(),
    ].join("|"),
    testItem,
    section: normalizeNoMatrixCell(step.source_section, ""),
    method,
    condition,
    requirement,
    day,
    tokensByGroup: {},
  };
}

function normalizeNoMatrixGroupLabel(
  group: ProjectTestPlanDraftGroup,
  fallback: string
): string {
  const label = (group.group_label ?? group.group_key ?? "").trim();
  const withoutPrefix = label.replace(/^group[\s_-]*/i, "").trim();
  return withoutPrefix || fallback;
}

function normalizeNoMatrixToken(step: ProjectTestPlanDraftStep, stepIndex: number): string {
  return (
    step.raw_token?.trim() ||
    step.sequence?.toString() ||
    `${stepIndex + 1}`
  );
}

function normalizeNoMatrixCell(
  value: string | number | null | undefined,
  fallback: string
): string {
  const text = value === null || value === undefined ? "" : `${value}`.trim();
  return text || fallback;
}

export function PackagePreparationMode({
  projectFolderTasks,
  currentProjectFolderTaskKey,
  selectedProjectFolderTaskKey,
  onSelectProjectFolderTask,
  onProjectFolderTaskAction,
  requestMaterialPreview,
  requestMaterialError,
  requestMaterialLoading,
  requiredFormsPreview,
  requiredFormsError,
  requiredFormsLoading,
  publicDriveUploadPreview,
  publicDriveUploadError,
  publicDriveUploadLoading,
}: {
  projectFolderTasks: ProjectFolderTaskRow[];
  currentProjectFolderTaskKey: ProjectFolderTaskKey;
  selectedProjectFolderTaskKey: ProjectFolderTaskKey;
  onSelectProjectFolderTask: (taskKey: ProjectFolderTaskKey) => void;
  onProjectFolderTaskAction: (actionTarget: ProjectFolderTaskActionTarget) => void;
  requestMaterialPreview: ProjectRuntimeConsoleModel["requestMaterialPreview"];
  requestMaterialError: string | null;
  requestMaterialLoading: boolean;
  requiredFormsPreview: ProjectRuntimeConsoleModel["requiredFormsPreview"];
  requiredFormsError: string | null;
  requiredFormsLoading: boolean;
  publicDriveUploadPreview: ProjectRuntimeConsoleModel["publicDriveUploadPreview"];
  publicDriveUploadError: string | null;
  publicDriveUploadLoading: boolean;
}): ReactElement {
  return (
    <section className="runtime-console-mode-stack" aria-label="Project Folder preparation">
      <ProjectFolderTaskList
        tasks={projectFolderTasks}
        currentTaskKey={currentProjectFolderTaskKey}
        selectedTaskKey={selectedProjectFolderTaskKey}
        onSelectTask={onSelectProjectFolderTask}
        onTaskAction={onProjectFolderTaskAction}
        requestMaterialPreview={requestMaterialPreview}
        requestMaterialError={requestMaterialError}
        requestMaterialLoading={requestMaterialLoading}
        requiredFormsPreview={requiredFormsPreview}
        requiredFormsError={requiredFormsError}
        requiredFormsLoading={requiredFormsLoading}
        publicDriveUploadPreview={publicDriveUploadPreview}
        publicDriveUploadError={publicDriveUploadError}
        publicDriveUploadLoading={publicDriveUploadLoading}
      />
    </section>
  );
}

function RuntimeSetupItem({ item }: { item: SetupMaterialItem }): ReactElement {
  return (
    <article className="runtime-console-readiness-item">
      <span className={`runtime-console-state-dot runtime-console-state-${item.status}`} />
      <div>
        <strong>{item.title}</strong>
        <p>{item.value}</p>
      </div>
    </article>
  );
}

function getNextActionHandler(
  actionTarget: string | null | undefined,
  onOpenMatrixEditor: () => void,
  onOpenFeeEvaluation: () => void,
  onRefreshPackagePreview: () => void,
  onCollectRequestMaterial: () => Promise<void>,
  onRefreshOfficialFolderCheck: () => Promise<void>,
  onRepairOfficialFolderStructure: () => Promise<void>,
  onRefreshPublicDriveUploadPreview: () => Promise<void>,
  onUploadPublicDriveProjectFolder: () => Promise<void>,
  onOpenSettings: () => void
): (() => void) | null {
  if (actionTarget === "matrix") {
    return onOpenMatrixEditor;
  }
  if (actionTarget === "fee") {
    return onOpenFeeEvaluation;
  }
  if (actionTarget === "package") {
    return onRefreshPackagePreview;
  }
  if (actionTarget === "request_material") {
    return () => void onCollectRequestMaterial();
  }
  if (actionTarget === "official_folder_refresh") {
    return () => void onRefreshOfficialFolderCheck();
  }
  if (actionTarget === "official_folder_repair") {
    return () => void onRepairOfficialFolderStructure();
  }
  if (actionTarget === "public_drive_refresh") {
    return () => void onRefreshPublicDriveUploadPreview();
  }
  if (actionTarget === "public_drive_upload") {
    return () => void onUploadPublicDriveProjectFolder();
  }
  if (actionTarget === "settings") {
    return onOpenSettings;
  }
  return null;
}
