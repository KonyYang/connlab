import type { FormEvent, ReactElement } from "react";
import type {
  LtrLocalCommitRequest,
  LtrPreviewRequest,
  LtrReadiness,
  LtrReadinessField,
  LtrRecord,
  LtrRegistrationPreview,
  LtrRegistrationType
} from "../../api/client";
import { lifecycleBlockReason } from "./lifecycleGuards";

type LtrActionPanelProps = {
  commitConfirmed: boolean;
  committing: boolean;
  ltrs: LtrRecord[];
  ltrPreview: LtrRegistrationPreview | null;
  ltrReadiness: LtrReadiness | null;
  onCommitLtr: () => Promise<void>;
  onPreviewLtr: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  previewing: boolean;
  previewInput: LtrPreviewRequest;
  projectStatus?: string | null;
  requestedBy: string;
  operatorNote: string;
  setCommitConfirmed: (value: boolean) => void;
  setOperatorNote: (value: string) => void;
  setPreviewInput: (value: LtrPreviewRequest) => void;
  setRequestedBy: (value: string) => void;
};

export function LtrActionPanel({
  commitConfirmed,
  committing,
  ltrs,
  ltrPreview,
  ltrReadiness,
  onCommitLtr,
  onPreviewLtr,
  previewing,
  previewInput,
  projectStatus,
  requestedBy,
  operatorNote,
  setCommitConfirmed,
  setOperatorNote,
  setPreviewInput,
  setRequestedBy
}: LtrActionPanelProps): ReactElement {
  const latest = ltrs[0] ?? null;
  const blockers = ltrPreview?.readiness.blockers ?? ltrReadiness?.blockers ?? [];
  const warnings = ltrPreview?.warnings ?? [];
  const conflicts = ltrPreview?.conflicts ?? [];
  const previewBlockReason = lifecycleBlockReason(projectStatus, "ltr_preview");
  const commitBlockedReason = commitBlockReason({
    commitConfirmed,
    conflicts,
    lifecycleReason: lifecycleBlockReason(projectStatus, "ltr_commit"),
    ltrPreview,
    readinessBlockers: blockers
  });

  return (
    <div className="action-panel-body">
      <div className="operator-panel">
        <div>
          <p className="eyebrow">LTR Number registration</p>
          <h4>{latest ? "LTR Number registered locally" : "Review LTR Number readiness"}</h4>
          <p>
            {latest
              ? "Confirm the latest local LTR record before preparing the project folder."
              : "Check required fields, run a no-write preview, then commit only after operator confirmation."}
          </p>
          <p className="fine-print">
            Normal LTR Number allocation is finalized only during an enabled Excel write session.
            Local commit is for approved preview records and does not write the workbook.
          </p>
        </div>
        <form className="card-form ltr-registration-panel" onSubmit={onPreviewLtr}>
          <div className="form-grid-two">
            <label>
              Year
              <input
                min="2000"
                max="9999"
                type="number"
                value={previewInput.year}
                onChange={(event) =>
                  setPreviewInput({ ...previewInput, year: Number(event.target.value) })
                }
              />
            </label>
            <label>
              Month
              <input
                min="1"
                max="12"
                type="number"
                value={previewInput.month}
                onChange={(event) =>
                  setPreviewInput({ ...previewInput, month: Number(event.target.value) })
                }
              />
            </label>
          </div>
          <label>
            Registration type
            <select
              value={previewInput.registration_type}
              onChange={(event) =>
                setPreviewInput({
                  ...previewInput,
                  registration_type: event.target.value as LtrRegistrationType
                })
              }
            >
              <option value="normal">Normal</option>
              <option value="associated">Associated</option>
            </select>
          </label>
          <label>
            Proposed LTR Number
            <input
              placeholder="DL-2026-04-001A"
              value={previewInput.proposed_ltr_number ?? ""}
              onChange={(event) =>
                setPreviewInput({
                  ...previewInput,
                  proposed_ltr_number: event.target.value
                })
              }
            />
          </label>
          {previewBlockReason && <p className="blocking-copy">{previewBlockReason}</p>}
          <button className="primary-action" disabled={previewing || Boolean(previewBlockReason)} type="submit">
            {previewing ? "Previewing..." : "Preview LTR Number"}
          </button>
        </form>
      </div>

      <ReadinessPanel readiness={ltrPreview?.readiness ?? ltrReadiness} />

      {ltrPreview && (
        <section className="ltr-preview-card">
          <div className="folder-preview-heading">
            <div>
              <span>No-write preview</span>
              <strong>{ltrPreview.proposed_ltr_number ?? "Final number pending Excel write"}</strong>
            </div>
            <span className={`status-badge status-badge-${previewBadgeState(ltrPreview.status)}`}>
              {ltrPreview.status}
            </span>
          </div>
          <dl className="metadata-grid">
            <div>
              <dt>Mode</dt>
              <dd>{ltrPreview.mode}</dd>
            </div>
            <div>
              <dt>Target sheet</dt>
              <dd>{ltrPreview.target_sheet ?? ltrPreview.target_write_year_sheet}</dd>
            </div>
            <div>
              <dt>Reserved</dt>
              <dd>{ltrPreview.final_number_reserved ? "Yes" : "No workbook write"}</dd>
            </div>
            <div>
              <dt>Conflicts</dt>
              <dd>{conflicts.length}</dd>
            </div>
          </dl>
          <MessageList title="Conflicts" tone="danger" values={conflicts} />
          <MessageList title="Warnings" tone="warning" values={warnings} />
        </section>
      )}

      <section className="operator-panel">
        <div>
          <p className="eyebrow">Local commit</p>
          <h4>Commit approved preview</h4>
          <p>Creates a local ConnLab LTR Number record and audit note. It does not write the shared Excel workbook.</p>
          {commitBlockedReason && <p className="blocking-copy">{commitBlockedReason}</p>}
        </div>
        <div className="card-form ltr-registration-panel">
          <label>
            Requested by
            <input
              value={requestedBy}
              onChange={(event) => setRequestedBy(event.target.value)}
            />
          </label>
          <label>
            Operator note
            <input
              value={operatorNote}
              onChange={(event) => setOperatorNote(event.target.value)}
              placeholder="Approved local registration"
            />
          </label>
          <label className="checkbox-row">
            <input
              checked={commitConfirmed}
              type="checkbox"
              onChange={(event) => setCommitConfirmed(event.target.checked)}
            />
            I confirm this preview should be committed locally.
          </label>
          <button
            className="primary-action"
            disabled={committing || Boolean(commitBlockedReason)}
            type="button"
            onClick={() => void onCommitLtr()}
          >
            {committing ? "Committing..." : "Commit locally"}
          </button>
        </div>
      </section>

      <div className="latest-ltr-card">
        <span>{latest ? "Latest local LTR Number" : "Not registered"}</span>
        <strong>{latest?.ltr_number ?? "No LTR Number yet"}</strong>
        <p>Status: {latest?.status ?? "waiting for registration"}</p>
        {latest?.notes && <p>Audit note stored locally.</p>}
      </div>
    </div>
  );
}

function ReadinessPanel({
  readiness
}: {
  readiness: LtrReadiness | null;
}): ReactElement {
  if (!readiness) {
    return (
      <section className="readiness-panel">
        <div className="folder-preview-heading">
          <div>
            <span>Readiness</span>
            <strong>Loading LTR readiness</strong>
          </div>
        </div>
      </section>
    );
  }

  const placeholderFields = readiness.fields.filter((field) => field.state === "placeholder");
  const reviewFields = readiness.fields.filter((field) => field.state === "needs_review");

  return (
    <section className="readiness-panel">
      <div className="folder-preview-heading">
        <div>
          <span>Readiness</span>
          <strong>{readiness.status}</strong>
        </div>
        <span className={`status-badge status-badge-${previewBadgeState(readiness.status)}`}>
          {readiness.blockers.length} blockers
        </span>
      </div>
      <ReadinessList title="Blocking fields" fields={readiness.blockers} />
      <ReadinessList title="Needs review" fields={reviewFields} />
      <ReadinessList title="Placeholders" fields={placeholderFields} />
    </section>
  );
}

function ReadinessList({
  fields,
  title
}: {
  fields: LtrReadinessField[];
  title: string;
}): ReactElement {
  if (fields.length === 0) {
    return (
      <div className="readiness-section">
        <strong>{title}</strong>
        <p>No fields in this group.</p>
      </div>
    );
  }
  return (
    <div className="readiness-section">
      <strong>{title}</strong>
      <ul className="readiness-list">
        {fields.map((field) => (
          <li key={field.key}>
            <span>{field.label}</span>
            <em>{field.value ?? field.placeholder_policy ?? "Missing"}</em>
            <small>{field.operator_action}</small>
          </li>
        ))}
      </ul>
    </div>
  );
}

function MessageList({
  title,
  tone,
  values
}: {
  title: string;
  tone: "danger" | "warning";
  values: string[];
}): ReactElement | null {
  if (values.length === 0) {
    return null;
  }
  return (
    <div className={`message-list message-list-${tone}`}>
      <strong>{title}</strong>
      <ul>
        {values.map((value) => (
          <li key={value}>{value}</li>
        ))}
      </ul>
    </div>
  );
}

function commitBlockReason({
  commitConfirmed,
  conflicts,
  lifecycleReason,
  ltrPreview,
  readinessBlockers
}: {
  commitConfirmed: boolean;
  conflicts: string[];
  lifecycleReason: string | null;
  ltrPreview: LtrRegistrationPreview | null;
  readinessBlockers: LtrReadinessField[];
}): string | null {
  if (lifecycleReason) {
    return lifecycleReason;
  }
  if (!ltrPreview) {
    return "Run a no-write LTR Number preview before local commit.";
  }
  if (readinessBlockers.length > 0) {
    return "Resolve blocking readiness fields before local commit.";
  }
  if (conflicts.length > 0) {
    return "Resolve preview conflicts before local commit.";
  }
  if (!commitConfirmed) {
    return "Operator confirmation is required.";
  }
  if (!effectiveCommitNumber(ltrPreview)) {
    return "Normal LTR Number final allocation requires an enabled Excel write session. Use an approved associated number or defer commit.";
  }
  return null;
}

export function buildLocalCommitRequest(
  preview: LtrRegistrationPreview,
  input: LtrPreviewRequest,
  operatorConfirmed: boolean,
  requestedBy: string,
  operatorNote: string
): LtrLocalCommitRequest {
  return {
    ...input,
    mode: "local_only",
    operator_confirmed: operatorConfirmed,
    proposed_ltr_number: effectiveCommitNumber(preview),
    requested_by: requestedBy || null,
    operator_note: operatorNote || null
  };
}

function effectiveCommitNumber(preview: LtrRegistrationPreview): string | null {
  return preview.proposed_ltr_number ?? null;
}

function previewBadgeState(status: string): string {
  if (status === "ready") {
    return "current";
  }
  if (status === "blocked") {
    return "blocked";
  }
  return "warning";
}
