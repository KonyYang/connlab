import type { ReactElement } from "react";
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
  onOpenSettings,
}: {
  lifecycle: WorkbenchLifecycleViewModel;
  onOpenMatrixEditor: () => void;
  onOpenFeeEvaluation: () => void;
  onRefreshPackagePreview: () => void;
  onCollectRequestMaterial: () => Promise<void>;
  onOpenSettings: () => void;
}): ReactElement {
  const actionHandler = getNextActionHandler(
    lifecycle.nextAction.actionTarget,
    onOpenMatrixEditor,
    onOpenFeeEvaluation,
    onRefreshPackagePreview,
    onCollectRequestMaterial,
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
  requestMaterialPreview,
  requestMaterialError,
  requestMaterialLoading,
}: {
  setupMaterials: SetupMaterialItem[];
  requestMaterialPreview: ProjectRuntimeConsoleModel["requestMaterialPreview"];
  requestMaterialError: string | null;
  requestMaterialLoading: boolean;
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

type RequestMaterialStatus =
  NonNullable<ProjectRuntimeConsoleModel["requestMaterialPreview"]>["status"];
