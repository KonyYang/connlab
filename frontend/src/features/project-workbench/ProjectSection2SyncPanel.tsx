import type { ReactElement } from "react";
import type {
  ProjectSection2SyncRequest,
  ProjectSection2SyncResponse
} from "../../api/client";

type ProjectSection2SyncPanelProps = {
  preview: ProjectSection2SyncResponse | null;
  loading: boolean;
  syncing: boolean;
  error: string | null;
  onRefresh: () => void;
  onSync: (input: ProjectSection2SyncRequest) => void;
};

const STATUS_COPY: Record<ProjectSection2SyncResponse["status"], string> = {
  ready: "Confirmed Matrix has newer Section 2 dates.",
  up_to_date: "Section 2 dates match Confirmed Matrix.",
  partial: "One Confirmed Matrix date is missing. Available dates can still sync.",
  blocked: "Section 2 dates are blocked.",
  synced: "Section 2 dates synced.",
};

const FIELD_LABELS: Record<ProjectSection2SyncResponse["fields"][number]["field_key"], string> = {
  received_date: "Received date",
  estimated_completion_date: "Estimated completion",
};

export function ProjectSection2SyncPanel({
  preview,
  loading,
  syncing,
  error,
  onRefresh,
  onSync,
}: ProjectSection2SyncPanelProps): ReactElement {
  const canSync =
    Boolean(preview) &&
    !loading &&
    !syncing &&
    preview?.status !== "blocked" &&
    preview?.fields.some((field) => field.status === "will_change");
  const statusText = error
    ? error
    : preview
      ? STATUS_COPY[preview.status]
      : loading
        ? "Checking Section 2 dates."
        : "Refresh to compare Section 2 dates.";

  function handleSync(): void {
    if (!preview) {
      return;
    }
    onSync({
      expected_confirmed_matrix_id: preview.confirmed_matrix_id,
      expected_confirmed_revision: preview.confirmed_revision,
    });
  }

  return (
    <section className="runtime-console-section2-sync" aria-label="Section 2 date sync">
      <header>
        <div>
          <p className="eyebrow">Application Form</p>
          <strong>Section 2 dates</strong>
        </div>
        <div className="runtime-console-section2-sync-actions">
          <button type="button" onClick={onRefresh} disabled={loading || syncing}>
            {loading ? "Checking" : "Refresh"}
          </button>
          <button type="button" onClick={handleSync} disabled={!canSync}>
            {syncing ? "Syncing" : "Sync Section 2 dates"}
          </button>
        </div>
      </header>
      <p className={error ? "runtime-console-section2-sync-error" : ""}>{statusText}</p>
      {preview ? (
        <dl className="runtime-console-section2-sync-fields">
          {preview.fields.map((field) => (
            <div key={field.field_key}>
              <dt>{FIELD_LABELS[field.field_key]}</dt>
              <dd>{formatFieldValue(field.current_value, field.next_value)}</dd>
            </div>
          ))}
        </dl>
      ) : null}
      <small>Updates structured Section 2 dates only. Word file update remains separate.</small>
    </section>
  );
}

function formatFieldValue(currentValue: string | null | undefined, nextValue: string | null | undefined): string {
  const current = currentValue?.trim() || "Blank";
  const next = nextValue?.trim() || "Blank";
  return current === next ? current : `${current} -> ${next}`;
}
