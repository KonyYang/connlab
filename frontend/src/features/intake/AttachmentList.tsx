import type { ReactElement } from "react";

import type { DraftDuplicateAction, DraftDuplicateCheck } from "../../api/client";
import { UiIcon } from "../../components/common/UiIcon";
import type { IntakeAttachmentViewModel, IntakeAttachmentKind } from "./intakeSelectors";

type AttachmentListProps = {
  attachments: IntakeAttachmentViewModel[];
  disabled?: boolean;
  disabledReason?: string;
  duplicateDraft?: DraftDuplicateCheck | null;
  importingAssetId?: string | null;
  resolvingDuplicateAction?: string | null;
  onDuplicateAction?: (action: DraftDuplicateAction) => void;
  onImport?: (attachment: IntakeAttachmentViewModel) => void;
  onOpen?: (attachment: IntakeAttachmentViewModel) => void;
  onSelect: (attachment: IntakeAttachmentViewModel) => void;
  packageLoaded: boolean;
};

export function AttachmentList({
  attachments,
  disabled = false,
  disabledReason = "Applying LTR number. Keep this page open.",
  duplicateDraft,
  importingAssetId,
  resolvingDuplicateAction,
  onDuplicateAction,
  onImport,
  onOpen,
  onSelect,
  packageLoaded,
}: AttachmentListProps): ReactElement {
  return (
    <section className="intake-panel intake-attachments-panel">
      <div className="attachments-heading">
        <h3 className="ui-panel-title">Attachments ({attachments.length})</h3>
      </div>
      {duplicateDraft && onDuplicateAction ? (
        <DraftDuplicateResolution
          disabled={disabled}
          disabledReason={disabledReason}
          duplicate={duplicateDraft}
          resolvingAction={resolvingDuplicateAction ?? null}
          onAction={onDuplicateAction}
        />
      ) : null}
      {packageLoaded ? (
        <div className="attachment-list" role="list">
          {attachments.map((attachment) => (
            <div
              className={attachment.selected ? "attachment-row attachment-row-active" : "attachment-row"}
              key={attachment.asset.asset_id}
              onDoubleClick={() => {
                if (!disabled) {
                  onOpen?.(attachment);
                }
              }}
            >
              <button
                className="attachment-select-button"
                disabled={disabled}
                title={disabled ? disabledReason : undefined}
                type="button"
                onClick={() => {
                  if (!disabled) {
                    onSelect(attachment);
                  }
                }}
              >
                <span className={`file-chip file-chip-${attachment.kind}`}>
                  {fileChipIcon(attachment.kind)}
                </span>
                <span className="attachment-name">
                  <span className="attachment-title">{attachment.asset.original_name}</span>
                </span>
              </button>
              {attachment.word && onImport ? (
                <button
                  className="attachment-import-button"
                  disabled={disabled || importingAssetId === attachment.asset.asset_id}
                  title={disabled ? disabledReason : undefined}
                  type="button"
                  onClick={() => {
                    if (!disabled) {
                      onImport?.(attachment);
                    }
                  }}
                  aria-label="Import into editor"
                >
                  <svg viewBox="0 0 12 12" width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="m4 2 4 4-4 4" />
                  </svg>
                </button>
              ) : null}
            </div>
          ))}
        </div>
      ) : (
        <div className="attachment-empty">
          <UiIcon name="package" />
          <strong>No source imported</strong>
          <span>Import a .msg package or upload an application form.</span>
        </div>
      )}
    </section>
  );
}

type DraftDuplicateResolutionProps = {
  disabled: boolean;
  disabledReason: string;
  duplicate: DraftDuplicateCheck;
  resolvingAction: string | null;
  onAction: (action: DraftDuplicateAction) => void;
};

function DraftDuplicateResolution({
  disabled,
  disabledReason,
  duplicate,
  resolvingAction,
  onAction,
}: DraftDuplicateResolutionProps): ReactElement {
  const formName = duplicate.incoming_application_form_name
    || duplicate.existing_application_form_name
    || "Selected application form";
  const canOpen = duplicate.allowed_actions.includes("open_existing");
  const canReplace = duplicate.allowed_actions.includes("replace_existing");

  return (
    <section className="email-duplicate-panel" aria-live="polite">
      <div className="email-duplicate-heading">
        <strong>This application draft already exists</strong>
        <span>{formName}</span>
      </div>
      <div className="email-duplicate-actions">
        <button
          className="new-project-secondary-action ui-secondary-action"
          disabled={disabled || Boolean(resolvingAction) || !canReplace}
          title={disabled ? disabledReason : undefined}
          type="button"
          onClick={() => {
            if (!disabled) {
              onAction("replace_existing");
            }
          }}
        >
          {resolvingAction === "replace_existing" ? "Reinitializing..." : "Reinitialize"}
        </button>
        <button
          className="new-project-primary-action ui-primary-action"
          disabled={disabled || Boolean(resolvingAction) || !canOpen}
          title={disabled ? disabledReason : undefined}
          type="button"
          onClick={() => {
            if (!disabled) {
              onAction("open_existing");
            }
          }}
        >
          {resolvingAction === "open_existing" ? "Loading..." : "Load existing"}
        </button>
      </div>
    </section>
  );
}

function fileChipIcon(kind: IntakeAttachmentKind): ReactElement {
  const config: Record<IntakeAttachmentKind, { label: string; bg: string; color: string }> = {
    word:  { label: "DOC", bg: "#E6F1FB", color: "#185FA5" },
    excel: { label: "XLS", bg: "#EAF3DE", color: "#3B6D11" },
    pdf:   { label: "PDF", bg: "#FCEBEB", color: "#A32D2D" },
    image: { label: "IMG", bg: "#EEEDFE", color: "#534AB7" },
    msg:   { label: "MSG", bg: "#FAEEDA", color: "#854F0B" },
    file:  { label: "FILE", bg: "#F1EFE8", color: "#5F5E5A" },
  };
  const { label, bg, color } = config[kind] ?? config.file;
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        width: 24,
        height: 24,
        borderRadius: 5,
        background: bg,
        color: color,
        fontSize: 9,
        fontWeight: 500,
        letterSpacing: "0.02em",
        flexShrink: 0,
        lineHeight: 1,
        whiteSpace: "nowrap",
      }}
    >
      {label}
    </span>
  );
}
