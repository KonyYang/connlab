import type { ReactElement } from "react";
import type { TemporaryProjectDeletePreview } from "../../api/client";
import type {
  WorkbenchLifecycleMode,
  WorkbenchLifecycleTab,
  WorkbenchLifecycleViewModel,
} from "./projectWorkbenchLifecycleSelectors";
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
  setupMaterials,
  requestMaterialPreview,
  requestMaterialError,
  requestMaterialLoading,
  publicDriveUploadPreview,
  publicDriveUploadError,
  publicDriveUploadLoading,
}: {
  setupMaterials: SetupMaterialItem[];
  requestMaterialPreview: ProjectRuntimeConsoleModel["requestMaterialPreview"];
  requestMaterialError: string | null;
  requestMaterialLoading: boolean;
  publicDriveUploadPreview: ProjectRuntimeConsoleModel["publicDriveUploadPreview"];
  publicDriveUploadError: string | null;
  publicDriveUploadLoading: boolean;
}): ReactElement {
  const copiedCount =
    requestMaterialPreview?.items.filter((item) =>
      item.status === "copied" || item.status === "already_present"
    ).length ?? 0;
  const plannedCount = requestMaterialPreview?.items.length ?? 0;
  const reviewCount =
    requestMaterialPreview?.items.filter((item) => item.review_required).length ?? 0;
  return (
    <section className="runtime-console-mode-stack" aria-label="Project Folder preparation">
      <section
        className="runtime-console-readiness"
        aria-label="Project Folder preparation checklist"
      >
        <div className="runtime-console-readiness-title">
          <p className="eyebrow">Project Folder</p>
          <strong>Prepare local project files before public-drive submission.</strong>
        </div>
        {setupMaterials.map((item) => (
          <RuntimeSetupItem key={item.title} item={item} />
        ))}
      </section>

      <section className="runtime-console-request-material" aria-label="Request material status">
        <div>
          <p className="eyebrow">Request material</p>
          <strong>{formatRequestMaterialStatus(requestMaterialPreview?.status ?? null)}</strong>
          <p>{formatRequestMaterialSummary(requestMaterialPreview?.status ?? null)}</p>
        </div>
        <dl>
          <div>
            <dt>Files checked</dt>
            <dd>{requestMaterialLoading ? "Loading" : plannedCount}</dd>
          </div>
          <div>
            <dt>Already collected</dt>
            <dd>{copiedCount}</dd>
          </div>
          <div>
            <dt>Needs review</dt>
            <dd>{reviewCount}</dd>
          </div>
        </dl>
        {requestMaterialError ? (
          <p className="runtime-console-error">{requestMaterialError}</p>
        ) : null}
        {requestMaterialPreview?.warnings.length ? (
          <ul className="runtime-console-blocker-list">
            {requestMaterialPreview.warnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        ) : null}
      </section>

      <PublicDriveUploadPreviewPanel
        preview={publicDriveUploadPreview}
        error={publicDriveUploadError}
        loading={publicDriveUploadLoading}
      />
    </section>
  );
}

function PublicDriveUploadPreviewPanel({
  preview,
  error,
  loading,
}: {
  preview: ProjectRuntimeConsoleModel["publicDriveUploadPreview"];
  error: string | null;
  loading: boolean;
}): ReactElement {
  const counts = preview?.counts ?? {};
  const items = preview?.items ?? [];
  return (
    <section className="runtime-console-public-drive-preview" aria-label="Public drive upload preview">
      <div className="runtime-console-public-drive-summary">
        <div>
          <p className="eyebrow">Public drive upload preview</p>
          <strong>{formatPublicDriveUploadPanelStatus(preview?.status ?? null)}</strong>
          <p>{formatPublicDriveUploadPanelSummary(preview?.status ?? null, loading)}</p>
        </div>
        <dl>
          <div>
            <dt>Add</dt>
            <dd>{loading ? "Loading" : counts.add ?? 0}</dd>
          </div>
          <div>
            <dt>Update</dt>
            <dd>{counts.update ?? 0}</dd>
          </div>
          <div>
            <dt>Already current</dt>
            <dd>{counts.skip ?? 0}</dd>
          </div>
          <div>
            <dt>Conflict</dt>
            <dd>{counts.conflict ?? 0}</dd>
          </div>
        </dl>
      </div>
      <div className="runtime-console-public-drive-target">
        <span>Public folder</span>
        <strong>{preview?.public_project_folder_path ?? "Not checked"}</strong>
      </div>
      {error ? <p className="runtime-console-error">{error}</p> : null}
      {preview?.blockers.length ? (
        <ul className="runtime-console-blocker-list">
          {preview.blockers.map((blocker) => (
            <li key={blocker}>{blocker}</li>
          ))}
        </ul>
      ) : null}
      {preview?.warnings.length ? (
        <ul className="runtime-console-blocker-list">
          {preview.warnings.map((warning) => (
            <li key={warning}>{warning}</li>
          ))}
        </ul>
      ) : null}
      <details className="runtime-console-public-drive-items" open={items.length > 0}>
        <summary>Upload preview items</summary>
        {items.length > 0 ? (
          <ul>
            {items.map((item) => (
              <li key={`${item.kind}:${item.relative_path}`}>
                <span>{formatPublicDriveUploadAction(item.action)}</span>
                <strong>{item.relative_path}</strong>
                <em>{item.kind === "directory" ? "Folder" : "File"}</em>
                <p>{item.message}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p>No upload items are available yet.</p>
        )}
      </details>
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

function formatRequestMaterialStatus(
  status: RequestMaterialStatus | null | undefined
): string {
  if (status === "collected") {
    return "Collected";
  }
  if (status === "ready") {
    return "Ready to collect";
  }
  if (status === "partial") {
    return "Partial collection available";
  }
  if (status === "review_required") {
    return "Needs attachment review";
  }
  if (status === "blocked" || status === "conflict") {
    return "Needs review";
  }
  return "Not checked";
}

function formatRequestMaterialSummary(
  status: RequestMaterialStatus | null | undefined
): string {
  if (status === "collected") {
    return "Original files and controlled copies are recorded for this project.";
  }
  if (status === "ready") {
    return "ConnLab can copy original request files and controlled Submitted Material copies.";
  }
  if (status === "partial") {
    return "Some request material can be collected, but the missing source is still visible.";
  }
  if (status === "review_required") {
    return "Available request files are collected. Review undecided attachments before placing them in Submitted Material.";
  }
  if (status === "blocked" || status === "conflict") {
    return "Review the request material source or target conflict before collecting.";
  }
  return "Refresh or collect request material after the local project folder is available.";
}

function formatPublicDriveUploadPanelStatus(
  status: PublicDriveUploadStatus | null | undefined
): string {
  if (status === "ready") {
    return "Ready to upload";
  }
  if (status === "current") {
    return "Already current";
  }
  if (status === "warning") {
    return "Ready with warnings";
  }
  if (status === "conflict") {
    return "Conflicts need review";
  }
  if (status === "blocked") {
    return "Not ready";
  }
  return "Not checked";
}

function formatPublicDriveUploadPanelSummary(
  status: PublicDriveUploadStatus | null | undefined,
  loading: boolean
): string {
  if (loading) {
    return "Loading public-drive upload preview.";
  }
  if (status === "ready") {
    return "Review the add, update, already-current, and conflict items before uploading.";
  }
  if (status === "current") {
    return "The public Project Folder matches the local Project Folder.";
  }
  if (status === "warning") {
    return "Review warnings before uploading to the public location.";
  }
  if (status === "conflict") {
    return "Resolve public-drive conflicts before uploading.";
  }
  if (status === "blocked") {
    return "Resolve the blocker before ConnLab can upload the Project Folder.";
  }
  return "Refresh public-drive preview after Project Folder readiness is complete.";
}

function formatPublicDriveUploadAction(action: string): string {
  if (action === "add") {
    return "Add";
  }
  if (action === "update") {
    return "Update";
  }
  if (action === "skip") {
    return "Skip";
  }
  if (action === "conflict") {
    return "Conflict";
  }
  if (action === "deferred") {
    return "Deferred";
  }
  return action;
}

type RequestMaterialStatus =
  NonNullable<ProjectRuntimeConsoleModel["requestMaterialPreview"]>["status"];

type PublicDriveUploadStatus =
  NonNullable<ProjectRuntimeConsoleModel["publicDriveUploadPreview"]>["status"];
