import { useState, type ReactElement } from "react";
import type { Project } from "../../api/client";
import { FeeEvaluationStatusSummary } from "./FeeEvaluationStatusSummary";
import { ProjectFolderCreationPanel } from "./ProjectFolderCreationPanel";
import { ProjectPackagePreviewPanel } from "./ProjectPackagePreviewPanel";
import { ProjectSection2SyncPanel } from "./ProjectSection2SyncPanel";
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
  onOpenSettings,
}: {
  lifecycle: WorkbenchLifecycleViewModel;
  onOpenMatrixEditor: () => void;
  onOpenFeeEvaluation: () => void;
  onRefreshPackagePreview: () => void;
  onOpenSettings: () => void;
}): ReactElement {
  const actionHandler = getNextActionHandler(
    lifecycle.nextAction.actionTarget,
    onOpenMatrixEditor,
    onOpenFeeEvaluation,
    onRefreshPackagePreview,
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
          <p className="eyebrow">Package readiness</p>
          <strong>Controlled delivery checklist</strong>
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
  onOpenMatrixEditor,
  onOpenFeeEvaluation,
}: {
  onOpenMatrixEditor: () => void;
  onOpenFeeEvaluation: () => void;
}): ReactElement {
  return (
    <section className="runtime-console-mode-surface" aria-label="Temporary planning">
      <div className="runtime-console-mode-heading">
        <p className="eyebrow">Planning mode</p>
        <h3>Shape the request before formal registration</h3>
        <p>Build Matrix and estimate fee before DL registration.</p>
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
          <p>Open Fee Evaluation for pre-DL estimation when a Matrix draft is available.</p>
          <button type="button" onClick={onOpenFeeEvaluation}>
            Open Fee Evaluation
          </button>
        </article>
      </div>
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
  folderResources,
  folderReady,
  projectNumber,
  onFolderCreated,
  onOpenMatrixEditor,
  onOpenFeeEvaluation,
  onRefreshPackagePreview,
  onRefreshSection2Sync,
  onSyncSection2,
  packagePreview,
  packagePreviewError,
  packagePreviewLoading,
  project,
  section2SyncError,
  section2SyncLoading,
  section2SyncPreview,
  section2SyncSyncing,
  feeEvaluationOutputStatus,
}: {
  setupMaterials: SetupMaterialItem[];
  folderResources: ProjectRuntimeConsoleModel["folderResources"];
  folderReady: boolean;
  projectNumber: string | null;
  onFolderCreated: ProjectRuntimeConsoleModel["onFolderCreated"];
  onOpenMatrixEditor: () => void;
  onOpenFeeEvaluation: () => void;
  onRefreshPackagePreview: () => void;
  onRefreshSection2Sync: () => void;
  onSyncSection2: ProjectRuntimeConsoleModel["onSyncSection2"];
  packagePreview: ProjectRuntimeConsoleModel["packagePreview"];
  packagePreviewError: string | null;
  packagePreviewLoading: boolean;
  project: Project;
  section2SyncError: string | null;
  section2SyncLoading: boolean;
  section2SyncPreview: ProjectRuntimeConsoleModel["section2SyncPreview"];
  section2SyncSyncing: boolean;
  feeEvaluationOutputStatus: ProjectRuntimeConsoleModel["versionStatus"]["downstream"][number] | null;
}): ReactElement {
  const [activeDetail, setActiveDetail] = useState<PackageDetailKey | null>(null);
  return (
    <section className="runtime-console-mode-stack" aria-label="Package preparation">
      <section
        className="runtime-console-readiness"
        aria-label="Project setup and output materials"
      >
        <div className="runtime-console-readiness-title">
          <p className="eyebrow">Package readiness</p>
          <strong>Prepare controlled package files before placing them in Submitted Material.</strong>
        </div>
        {setupMaterials.map((item) => (
          <RuntimeSetupItem key={item.title} item={item} />
        ))}
      </section>

      <ProjectPackagePreviewPanel
        preview={packagePreview}
        loading={packagePreviewLoading}
        error={packagePreviewError}
        onRefresh={onRefreshPackagePreview}
      />

      <section className="runtime-console-package-secondary" aria-label="Secondary package links">
        <p className="eyebrow">Secondary links</p>
        <div>
          <button type="button" onClick={onOpenMatrixEditor}>
            Matrix Editor
          </button>
          <button type="button" onClick={onOpenFeeEvaluation}>
            Fee Evaluation
          </button>
        </div>
      </section>

      <section className="runtime-console-package-detail-selector" aria-label="Package detail panels">
        <p className="eyebrow">Package details</p>
        <div>
          <PackageDetailButton
            active={activeDetail === "folder"}
            label="Folder setup details"
            onClick={() => setActiveDetail(activeDetail === "folder" ? null : "folder")}
          />
          <PackageDetailButton
            active={activeDetail === "section2"}
            label="Section 2 details"
            onClick={() => setActiveDetail(activeDetail === "section2" ? null : "section2")}
          />
          <PackageDetailButton
            active={activeDetail === "fee"}
            label="Fee details"
            onClick={() => setActiveDetail(activeDetail === "fee" ? null : "fee")}
          />
        </div>
      </section>

      {activeDetail === "folder" ? (
        <ProjectFolderCreationPanel
          configuredOutputRoot={folderResources.outputRoot}
          configuredTemplate={folderResources.template}
          folderReady={folderReady}
          latestLtrNumber={projectNumber}
          onFolderCreated={onFolderCreated}
          projectId={project.project_id}
          projectStatus={project.status}
        />
      ) : null}

      {activeDetail === "section2" ? (
        <ProjectSection2SyncPanel
          preview={section2SyncPreview}
          loading={section2SyncLoading}
          syncing={section2SyncSyncing}
          error={section2SyncError}
          onRefresh={onRefreshSection2Sync}
          onSync={onSyncSection2}
        />
      ) : null}

      {activeDetail === "fee" ? (
        <FeeEvaluationStatusSummary
          projectId={project.project_id}
          outputStatus={feeEvaluationOutputStatus}
          canOpen
          onOpenFeeEvaluation={onOpenFeeEvaluation}
        />
      ) : null}
    </section>
  );
}

type PackageDetailKey = "folder" | "section2" | "fee";

function PackageDetailButton({
  active,
  label,
  onClick,
}: {
  active: boolean;
  label: string;
  onClick: () => void;
}): ReactElement {
  return (
    <button
      type="button"
      className={active ? "is-active" : ""}
      aria-pressed={active}
      onClick={onClick}
    >
      {label}
    </button>
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
  if (actionTarget === "settings") {
    return onOpenSettings;
  }
  return null;
}
