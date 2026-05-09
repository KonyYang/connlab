import { useEffect, useMemo, useState, type ReactElement } from "react";
import type { ExternalResource, ExternalResourceType } from "../../api/client";
import {
  LOCAL_MACHINE_PATH_CONFIGS,
  SHARED_RESOURCE_CONFIGS
} from "./settingsResourceConfig";
import { buildSettingsResourceRows, type SettingsResourceRow } from "./settingsSelectors";

type SettingsExternalResourcesPanelProps = {
  resources: ExternalResource[];
  savingType: ExternalResourceType | null;
  validatingType: ExternalResourceType | null;
  onSave: (
    resourceType: ExternalResourceType,
    input: { path: string; active: boolean }
  ) => Promise<void>;
  onValidate: (resourceType: ExternalResourceType) => Promise<void>;
};

type DraftValue = {
  path: string;
  active: boolean;
};

export function SettingsExternalResourcesPanel({
  resources,
  savingType,
  validatingType,
  onSave,
  onValidate
}: SettingsExternalResourcesPanelProps): ReactElement {
  const rows = useMemo(() => buildSettingsResourceRows(resources), [resources]);
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
        active: current[resourceType]?.active ?? true,
        ...value
      }
    }));
  }

  return (
    <section className="settings-panel">
      <div className="settings-panel-heading">
        <div>
          <h2 className="ui-panel-title">External resources</h2>
          <p>Use local paths during development. Switch to public-drive paths before production use.</p>
        </div>
      </div>

      <div className="settings-resource-group">
        <h3 className="ui-section-title">Shared resources</h3>
        <div className="settings-resource-list">
          {rows.map((row) => (
            <ResourceRow
              draft={drafts[row.resourceType] ?? { path: row.path, active: row.active }}
              key={row.resourceType}
              row={row}
              saving={savingType === row.resourceType}
              validating={validatingType === row.resourceType}
              onDraftChange={(value) => updateDraft(row.resourceType, value)}
              onSave={() => onSave(row.resourceType, drafts[row.resourceType] ?? row)}
              onValidate={() => onValidate(row.resourceType)}
            />
          ))}
        </div>
      </div>

      <div className="settings-resource-group">
        <h3 className="ui-section-title">Local machine paths</h3>
        <div className="settings-local-list">
          {LOCAL_MACHINE_PATH_CONFIGS.map((item) => (
            <article className="settings-local-row" key={item.key}>
              <div>
                <strong>{item.label}</strong>
                <span>{item.expectedKind}</span>
              </div>
              <p>{item.note}</p>
              <span className="settings-status-badge settings-status-neutral">Local setting</span>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function ResourceRow({
  row,
  draft,
  saving,
  validating,
  onDraftChange,
  onSave,
  onValidate
}: {
  row: SettingsResourceRow;
  draft: DraftValue;
  saving: boolean;
  validating: boolean;
  onDraftChange: (value: Partial<DraftValue>) => void;
  onSave: () => void;
  onValidate: () => void;
}): ReactElement {
  const canSave = draft.path.trim().length > 0 && !saving;
  const canValidate = Boolean(row.resource) && !validating;

  return (
    <article className="settings-resource-row">
      <div className="settings-resource-label">
        <strong>{row.label}</strong>
        <span>{row.expectedKind}</span>
      </div>
      <label className="settings-path-field">
        <span>Path</span>
        <input
          aria-label={`${row.label} path`}
          value={draft.path}
          onChange={(event) => onDraftChange({ path: event.target.value })}
          placeholder="Paste local or public-drive path"
        />
      </label>
      <label className="settings-active-toggle">
        <input
          checked={draft.active}
          type="checkbox"
          onChange={(event) => onDraftChange({ active: event.target.checked })}
        />
        <span>Active</span>
      </label>
      <div className="settings-validation-cell">
        <span className={`settings-status-badge settings-status-${row.statusTone}`}>
          {row.statusLabel}
        </span>
        <small>Last checked: {row.lastChecked}</small>
        {row.failureReason && <p>{row.failureReason}</p>}
      </div>
      <div className="settings-row-actions">
        <button
          className="ui-secondary-action"
          disabled={!canSave}
          type="button"
          onClick={onSave}
        >
          {saving ? "Saving" : "Save"}
        </button>
        <button
          className="ui-primary-action"
          disabled={!canValidate}
          type="button"
          onClick={onValidate}
        >
          {validating ? "Checking" : "Validate"}
        </button>
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
        active: row?.active ?? true
      };
      return drafts;
    },
    {} as Record<ExternalResourceType, DraftValue>
  );
}
