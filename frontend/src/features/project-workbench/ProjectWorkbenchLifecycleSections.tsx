import type { ReactElement } from "react";
import type { TemporaryProjectDeletePreview } from "../../api/client";
import type {
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
  onDeleteTemporaryProject,
  promotionMessage,
}: {
  deletePreview: TemporaryProjectDeletePreview | null;
  lifecycleError: string | null;
  lifecycleBusy: boolean;
  feePlanningAvailable: boolean;
  onOpenMatrixEditor: () => void;
  onOpenFeeEvaluation: () => void;
  onStartPromotion: () => void;
  onStopProject: () => void;
  onDeleteTemporaryProject: () => void;
  promotionMessage: string | null;
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
        lifecycleBusy={lifecycleBusy}
        lifecycleError={lifecycleError}
        onDeleteTemporaryProject={onDeleteTemporaryProject}
        onStopProject={onStopProject}
      />
    </section>
  );
}

export function ProjectLifecycleManagementPanel({
  allowDelete,
  deletePreview,
  lifecycleBusy,
  lifecycleError,
  onDeleteTemporaryProject,
  onStopProject,
}: {
  allowDelete: boolean;
  deletePreview: TemporaryProjectDeletePreview | null;
  lifecycleBusy: boolean;
  lifecycleError: string | null;
  onDeleteTemporaryProject: () => void;
  onStopProject: () => void;
}): ReactElement {
  const blockers = deletePreview?.blockers ?? [];
  return (
    <section className="runtime-console-lifecycle-management" aria-label="Project lifecycle">
      <div>
        <p className="eyebrow">Project lifecycle</p>
        <strong>
          {allowDelete
            ? "Stop or safely remove this temporary record"
            : "Stop this project lifecycle"}
        </strong>
        <p>
          {allowDelete
            ? "Stop keeps the project for review. Delete is only available for mistaken or duplicate temporary records with no formal or temporary workspace blockers."
            : "Stop keeps the project for review when business work should not continue."}
        </p>
      </div>
      <div className="runtime-console-lifecycle-actions">
        <button type="button" disabled={lifecycleBusy} onClick={onStopProject}>
          Stop project
        </button>
        {allowDelete ? (
          <button
            type="button"
            disabled={lifecycleBusy || !deletePreview?.can_delete}
            onClick={onDeleteTemporaryProject}
          >
            Delete temporary project
          </button>
        ) : null}
      </div>
      {blockers.length > 0 ? (
        <ul className="runtime-console-blocker-list">
          {blockers.map((blocker) => (
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

export function PackagePreparationMode({
  projectFolderTasks,
  currentProjectFolderTaskKey,
  selectedProjectFolderTaskKey,
  onSelectProjectFolderTask,
  onProjectFolderTaskAction,
  requestMaterialPreview,
  requestMaterialError,
  requestMaterialLoading,
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
