import {
  useEffect,
  useMemo,
  useState,
  type ReactElement
} from "react";
import type { ExternalResource, ExternalResourceType } from "../../api/client";
import type { LtrWorkbookPasswordStatus } from "../../api/client";
import { SHARED_RESOURCE_CONFIGS } from "./settingsResourceConfig";
import { buildSettingsResourceRows, type SettingsResourceRow } from "./settingsSelectors";

type SettingsExternalResourcesPanelProps = {
  resources: ExternalResource[];
  savingType: ExternalResourceType | null;
  passwordStatus: LtrWorkbookPasswordStatus | null;
  savingPassword: boolean;
  browseEnabled: boolean;
  pathValidationMessages: Record<ExternalResourceType, string | null>;
  onPathChange: (resourceType: ExternalResourceType) => void;
  onSave: (
    resourceType: ExternalResourceType,
    input: { path: string; active: boolean; worksheet_name?: string | null }
  ) => Promise<void>;
  onPasswordSave: (password: string) => Promise<void>;
  onBrowse: (resourceType: ExternalResourceType) => Promise<string | null>;
};

type DraftValue = {
  path: string;
  worksheetName: string;
};

export function SettingsExternalResourcesPanel({
  resources,
  savingType,
  passwordStatus,
  savingPassword,
  browseEnabled,
  pathValidationMessages,
  onPathChange,
  onSave,
  onPasswordSave,
  onBrowse
}: SettingsExternalResourcesPanelProps): ReactElement {
  const rows = useMemo(() => buildSettingsResourceRows(resources), [resources]);
  const categoryOrder = useMemo(
    () => [...new Set(SHARED_RESOURCE_CONFIGS.map((item) => item.category))],
    []
  );
  const [drafts, setDrafts] = useState<Record<ExternalResourceType, DraftValue>>(
    () => initialDrafts(rows)
  );

  useEffect(() => {
    setDrafts(initialDrafts(rows));
  }, [rows]);

  function updateDraft(resourceType: ExternalResourceType, value: Partial<DraftValue>): void {
    setDrafts((current) => ({
      ...current,
      [resourceType]: {
        path: current[resourceType]?.path ?? "",
        worksheetName: current[resourceType]?.worksheetName ?? "",
        ...value
      }
    }));
  }

  return (
    <section className="settings-panel">
      <div className="settings-panel-heading">
        <div>
          <h2 className="ui-panel-title">Editable file locations</h2>
        </div>
      </div>

      {categoryOrder.map((category) => {
        const categoryRows = rows.filter((row) => row.category === category);
        if (categoryRows.length === 0) {
          return null;
        }
        return (
          <div className="settings-resource-group" key={category}>
            <h3 className="ui-section-title">{category}</h3>
            <div className="settings-resource-list">
              {categoryRows.map((row) => (
                <ResourceRow
                  draft={drafts[row.resourceType] ?? {
                    path: row.path,
                    worksheetName: row.worksheetName ?? ""
                  }}
                  key={row.resourceType}
                  row={row}
                  saving={savingType === row.resourceType}
                  browseEnabled={browseEnabled}
                  validationMessage={pathValidationMessages[row.resourceType] ?? null}
                  onDraftChange={(value) => updateDraft(row.resourceType, value)}
                  onPathChange={() => onPathChange(row.resourceType)}
                  onSave={(input) =>
                    onSave(row.resourceType, {
                      path: input.path,
                      active: true,
                      ...(input.worksheetNameSupplied
                        ? { worksheet_name: input.worksheetName }
                        : {})
                    })
                  }
                  onBrowse={() => onBrowse(row.resourceType)}
                />
              ))}
              {category === "Public registration and record files" ? (
                <LtrWorkbookPasswordRow
                  status={passwordStatus}
                  saving={savingPassword}
                  onSave={onPasswordSave}
                />
              ) : null}
            </div>
          </div>
        );
      })}
    </section>
  );
}

function ResourceRow({
  row,
  draft,
  saving,
  browseEnabled,
  validationMessage,
  onDraftChange,
  onPathChange,
  onSave,
  onBrowse
}: {
  row: SettingsResourceRow;
  draft: DraftValue;
  saving: boolean;
  browseEnabled: boolean;
  validationMessage: string | null;
  onDraftChange: (value: Partial<DraftValue>) => void;
  onPathChange: () => void;
  onSave: (input: {
    path: string;
    worksheetNameSupplied?: boolean;
    worksheetName?: string | null;
  }) => void;
  onBrowse: () => Promise<string | null>;
}): ReactElement {
  const isFolder = row.expectedKind === "Folder";
  const canBrowse = browseEnabled;
  const inputClassName = validationMessage
    ? "settings-path-input is-invalid-path"
    : "settings-path-input";
  const [picking, setPicking] = useState(false);

  function autoSaveFromInput(path: string): void {
    const normalized = path.trim();
    if (!normalized || saving) {
      return;
    }
    void onSave({ path: normalized });
  }

  function saveWorksheetName(value: string): void {
    if (!draft.path.trim() || saving) {
      return;
    }
    const normalized = value.trim();
    void onSave({
      path: draft.path.trim(),
      worksheetNameSupplied: true,
      worksheetName: normalized || null
    });
  }

  async function browseForPath(): Promise<void> {
    setPicking(true);
    try {
      const nextPath = await onBrowse();
      if (!nextPath) {
        return;
      }
      onDraftChange({ path: nextPath });
      onPathChange();
      autoSaveFromInput(nextPath);
    } finally {
      setPicking(false);
    }
  }

  const browseLabel = isFolder ? "Browse folder" : "Browse file";

  return (
    <article className="settings-resource-row">
      <div className="settings-resource-label">
        <strong>{row.label}</strong>
      </div>
      <label className="settings-path-field">
        <div
          className={
            canBrowse
              ? "settings-path-control"
              : "settings-path-control settings-path-control-no-browse"
          }
        >
          <input
            aria-label={`${row.label} path`}
            className={inputClassName}
            aria-invalid={validationMessage ? "true" : "false"}
            title={validationMessage ?? `${row.label} path`}
            value={draft.path}
            onChange={(event) => {
              onDraftChange({ path: event.target.value });
              onPathChange();
            }}
            onBlur={(event) => autoSaveFromInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                autoSaveFromInput((event.target as HTMLInputElement).value);
                event.preventDefault();
              }
            }}
            disabled={saving}
            placeholder="Paste path"
          />
          {canBrowse ? (
            <button
              className="ui-tertiary-action"
              type="button"
              disabled={saving || picking}
              onClick={() => {
                void browseForPath();
              }}
            >
              {browseLabel}
            </button>
          ) : null}
        </div>
      </label>
      {row.resourceType === "standard_record_excel" ? (
        <label className="settings-standard-sheet-field">
          <span>Standard record sheet</span>
          <input
            aria-label="Standard record sheet"
            disabled={saving}
            maxLength={31}
            value={draft.worksheetName}
            onChange={(event) => onDraftChange({ worksheetName: event.target.value })}
            onBlur={(event) => saveWorksheetName(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                saveWorksheetName((event.target as HTMLInputElement).value);
                event.preventDefault();
              }
            }}
          />
        </label>
      ) : null}
    </article>
  );
}

function LtrWorkbookPasswordRow({
  status,
  saving,
  onSave
}: {
  status: LtrWorkbookPasswordStatus | null;
  saving: boolean;
  onSave: (password: string) => Promise<void>;
}): ReactElement {
  const [draft, setDraft] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [hidePassword, setHidePassword] = useState(true);
  const configured = Boolean(status?.configured);
  const overridden = Boolean(status?.overridden_by_environment);
  const canSave = draft.trim().length > 0 && !saving && !overridden;

  useEffect(() => {
    setDraft(status?.password ?? "");
    setMessage(null);
  }, [status?.password]);

  async function savePassword(): Promise<void> {
    setMessage(null);
    await onSave(draft);
    setMessage("Password updated.");
  }

  return (
    <article className="settings-resource-row settings-password-row">
      <div className="settings-resource-label">
        <strong>LTR workbook password</strong>
      </div>
      <div className="settings-password-field">
        <div className="settings-password-control">
          <input
            aria-label="LTR workbook password"
            autoComplete="new-password"
            disabled={saving || overridden}
            type={hidePassword ? "password" : "text"}
            value={draft}
            onChange={(event) => {
              setDraft(event.target.value);
              setMessage(null);
            }}
            placeholder={configured ? "Enter new password" : "Enter password"}
          />
          <label className="settings-secret-toggle">
            <input
              checked={hidePassword}
              disabled={saving || overridden}
              type="checkbox"
              onChange={(event) => setHidePassword(event.target.checked)}
            />
            <span>Hide password</span>
          </label>
          <button
            className="ui-secondary-action"
            type="button"
            disabled={!canSave}
            onClick={() => {
              void savePassword().catch(() => undefined);
            }}
          >
            {saving ? "Updating..." : "Update password"}
          </button>
        </div>
        {overridden ? (
          <span className="settings-secret-note">
            Environment password is active; local changes will not take effect.
          </span>
        ) : null}
        {message ? <span className="settings-secret-note">{message}</span> : null}
      </div>
    </article>
  );
}

function initialDrafts(rows: SettingsResourceRow[]): Record<ExternalResourceType, DraftValue> {
  return SHARED_RESOURCE_CONFIGS.reduce(
    (drafts, config) => {
      const row = rows.find((item) => item.resourceType === config.resourceType);
      drafts[config.resourceType] = {
        path: row?.path ?? "",
        worksheetName: row?.worksheetName ?? ""
      };
      return drafts;
    },
    {} as Record<ExternalResourceType, DraftValue>
  );
}
