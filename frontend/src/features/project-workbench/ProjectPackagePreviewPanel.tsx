import type { ReactElement } from "react";
import type { ProjectPackagePreview } from "../../api/client";

type ProjectPackagePreviewPanelProps = {
  preview: ProjectPackagePreview | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
};

const STATUS_COPY: Record<ProjectPackagePreview["status"], string> = {
  ready: "Package readiness is clear.",
  blocked: "Package readiness has blockers.",
};

export function ProjectPackagePreviewPanel({
  preview,
  loading,
  error,
  onRefresh,
}: ProjectPackagePreviewPanelProps): ReactElement {
  const visibleOutputItems = preview
    ? [...preview.required_items, ...preview.optional_items].filter(isVisiblePackageOutputItem)
    : [];
  const statusLabel = error
    ? "Preview unavailable"
    : preview
      ? STATUS_COPY[preview.status]
      : loading
        ? "Checking package readiness."
        : "Refresh to inspect package readiness.";
  return (
    <section className="runtime-console-package-preview" aria-label="Project package preview">
      <header>
        <div>
          <p className="eyebrow">Package outputs</p>
          <strong>Controlled output readiness</strong>
        </div>
        <button type="button" onClick={onRefresh} disabled={loading}>
          {loading ? "Refreshing" : "Refresh preview"}
        </button>
      </header>

      <div className="runtime-console-package-summary">
        <div>
          <span>Status</span>
          <strong className={preview?.status === "ready" ? "is-ready" : "is-blocked"}>
            {statusLabel}
          </strong>
        </div>
        <div>
          <span>Target folder</span>
          <strong>{preview?.project_folder.path ?? "Not ready"}</strong>
        </div>
      </div>

      {error ? <p className="runtime-console-package-error">{error}</p> : null}

      {preview ? (
        <>
          {preview.blockers.length > 0 ? (
            <PackageMessageList title="Blockers" items={preview.blockers} tone="blocker" />
          ) : null}
          {preview.warnings.length > 0 ? (
            <PackageMessageList title="Warnings" items={preview.warnings} tone="warning" />
          ) : null}
          <div className="runtime-console-package-items" aria-label="Package outputs">
            {visibleOutputItems.map((item) => (
              <article key={item.key}>
                <span className={`runtime-console-package-badge status-${item.status}`}>
                  {item.status}
                </span>
                <div>
                  <strong>{item.label}</strong>
                  <p>{sanitizePackageMessage(item.message)}</p>
                  {item.target_folder ? <small>{item.target_folder}</small> : null}
                </div>
              </article>
            ))}
          </div>
        </>
      ) : null}
    </section>
  );
}

function isVisiblePackageOutputItem(
  item: ProjectPackagePreview["required_items"][number]
): boolean {
  const searchable = `${item.key} ${item.label} ${item.message}`.toLowerCase();
  return !(
    searchable.includes("evidence") ||
    searchable.includes("later package execution concern")
  );
}

function sanitizePackageMessage(message: string): string {
  return message
    .replace(/\s+in\s+TASK_\d+[A-Z]?\b/gi, "")
    .replace(/\bTASK_\d+[A-Z]?\b/gi, "this workflow")
    .replace(/\s+\./g, ".")
    .trim();
}

function PackageMessageList({
  title,
  items,
  tone,
}: {
  title: string;
  items: string[];
  tone: "blocker" | "warning";
}): ReactElement {
  return (
    <div className={`runtime-console-package-messages ${tone}`}>
      <strong>{title}</strong>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
