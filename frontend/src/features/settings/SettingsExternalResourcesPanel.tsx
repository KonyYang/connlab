import {
  useEffect,
  useMemo,
  useState,
  type ReactElement
} from "react";
import type { ExternalResource, ExternalResourceType } from "../../api/client";
import { SHARED_RESOURCE_CONFIGS } from "./settingsResourceConfig";
import { buildSettingsResourceRows, type SettingsResourceRow } from "./settingsSelectors";

type SettingsExternalResourcesPanelProps = {
  resources: ExternalResource[];
  savingType: ExternalResourceType | null;
  browseEnabled: boolean;
  pathValidationMessages: Record<ExternalResourceType, string | null>;
  onPathChange: (resourceType: ExternalResourceType) => void;
  onSave: (
    resourceType: ExternalResourceType,
    input: { path: string; active: boolean }
  ) => Promise<void>;
  onBrowse: (resourceType: ExternalResourceType) => Promise<string | null>;
};

type DraftValue = {
  path: string;
};

export function SettingsExternalResourcesPanel({
  resources,
  savingType,
  browseEnabled,
  pathValidationMessages,
  onPathChange,
  onSave,
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
                  draft={drafts[row.resourceType] ?? { path: row.path }}
                  key={row.resourceType}
                  row={row}
                  saving={savingType === row.resourceType}
                  browseEnabled={browseEnabled}
                  validationMessage={pathValidationMessages[row.resourceType] ?? null}
                  onDraftChange={(value) => updateDraft(row.resourceType, value)}
                  onPathChange={() => onPathChange(row.resourceType)}
                  onSave={(nextPath) =>
                    onSave(row.resourceType, {
                      path: nextPath,
                      active: true
                    })
                  }
                  onBrowse={() => onBrowse(row.resourceType)}
                />
              ))}
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
  onSave: (path: string) => void;
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
    void onSave(normalized);
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
    </article>
  );
}

function initialDrafts(rows: SettingsResourceRow[]): Record<ExternalResourceType, DraftValue> {
  return SHARED_RESOURCE_CONFIGS.reduce(
    (drafts, config) => {
      const row = rows.find((item) => item.resourceType === config.resourceType);
      drafts[config.resourceType] = {
        path: row?.path ?? ""
      };
      return drafts;
    },
    {} as Record<ExternalResourceType, DraftValue>
  );
}
