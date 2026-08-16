import { useEffect, useState, type ReactElement } from "react";
import {
  listExternalResources,
  saveExternalResource,
  validateExternalResource,
  type ExternalResource,
  type ExternalResourceType
} from "../api/client";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingState } from "../components/common/LoadingState";
import {
  hasDesktopPathPickerBridge,
  pickExternalResourcePathFromDesktop
} from "../desktop/pathPickerBridge";
import { SettingsExternalResourcesPanel } from "../features/settings/SettingsExternalResourcesPanel";
import "../settings.css";

function settingsPathValidationMessage(reason: string | null): string {
  if (reason?.startsWith("Expected an existing file:")) {
    return "File does not exist.";
  }
  return reason ?? "Invalid path";
}

export function SettingsPage(): ReactElement {
  const [resources, setResources] = useState<ExternalResource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [savingType, setSavingType] = useState<ExternalResourceType | null>(null);
  const [pathValidationMessages, setPathValidationMessages] = useState<
    Record<ExternalResourceType, string | null>
  >({} as Record<ExternalResourceType, string | null>);

  useEffect(() => {
    void refreshResources();
  }, []);

  async function refreshResources(): Promise<void> {
    setLoading(true);
    try {
      const currentResources = await listExternalResources();
      setResources(currentResources);
      setPathValidationMessages((current) => {
        const next: Record<ExternalResourceType, string | null> = {
          ...current
        };
        for (const resource of currentResources) {
          next[resource.resource_type] = resource.validation_status === "invalid"
            ? settingsPathValidationMessage(resource.validation_failure_reason)
            : null;
        }
        return next;
      });
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSave(
    resourceType: ExternalResourceType,
    input: { path: string; active: boolean; worksheet_name?: string | null }
  ): Promise<void> {
    if (input.path.trim().length === 0) {
      setError("Please enter a path.");
      return;
    }
    setSavingType(resourceType);
    setError(null);
    setPathValidationMessages((current) => ({ ...current, [resourceType]: null }));
    try {
      const saved = await saveExternalResource(resourceType, {
        path: input.path.trim(),
        active: input.active,
        ...(Object.prototype.hasOwnProperty.call(input, "worksheet_name")
          ? { worksheet_name: input.worksheet_name }
          : {})
      });
      upsertResource(saved);
      const validated = await validateExternalResource(resourceType);
      setPathValidationMessages((current) => ({
        ...current,
        [resourceType]:
          validated.validation_status === "invalid"
            ? settingsPathValidationMessage(validated.validation_failure_reason)
            : null
      }));
    } catch (err) {
      setError((err as Error).message);
      setPathValidationMessages((current) => ({
        ...current,
        [resourceType]: (err as Error).message
      }));
      return;
    } finally {
      setSavingType(null);
    }
  }

  function upsertResource(next: ExternalResource): void {
    setResources((current) => {
      const exists = current.some((item) => item.resource_type === next.resource_type);
      if (!exists) {
        return [...current, next];
      }
      return current.map((item) =>
        item.resource_type === next.resource_type ? next : item
      );
    });
  }

  async function handleBrowse(
    resourceType: ExternalResourceType
  ): Promise<string | null> {
    setError(null);
    if (hasDesktopPathPickerBridge()) {
      return pickExternalResourcePathFromDesktop(resourceType);
    }
    return null;
  }

  return (
    <section className="settings-page">
      <div className="settings-header">
        <div>
          <h1>File Locations</h1>
        </div>
      </div>

      {loading && <LoadingState label="Loading settings" />}
      {error && <ErrorMessage message={error} />}

      {!loading && (
        <SettingsExternalResourcesPanel
          resources={resources}
          savingType={savingType}
          onSave={handleSave}
          browseEnabled={hasDesktopPathPickerBridge()}
          onBrowse={handleBrowse}
          pathValidationMessages={pathValidationMessages}
          onPathChange={(resourceType) =>
            setPathValidationMessages((current) => ({
              ...current,
              [resourceType]: null
            }))
          }
        />
      )}
    </section>
  );
}
