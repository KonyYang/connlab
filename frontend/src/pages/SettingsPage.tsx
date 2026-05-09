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
import { SettingsExternalResourcesPanel } from "../features/settings/SettingsExternalResourcesPanel";
import "../settings.css";

export function SettingsPage(): ReactElement {
  const [resources, setResources] = useState<ExternalResource[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [savingType, setSavingType] = useState<ExternalResourceType | null>(null);
  const [validatingType, setValidatingType] = useState<ExternalResourceType | null>(null);

  useEffect(() => {
    void refreshResources();
  }, []);

  async function refreshResources(): Promise<void> {
    setLoading(true);
    try {
      setResources(await listExternalResources());
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSave(
    resourceType: ExternalResourceType,
    input: { path: string; active: boolean }
  ): Promise<void> {
    setSavingType(resourceType);
    setError(null);
    setMessage(null);
    try {
      const saved = await saveExternalResource(resourceType, {
        path: input.path.trim(),
        active: input.active
      });
      upsertResource(saved);
      setMessage("Resource path saved. Validate it before using it in project work.");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSavingType(null);
    }
  }

  async function handleValidate(resourceType: ExternalResourceType): Promise<void> {
    setValidatingType(resourceType);
    setError(null);
    setMessage(null);
    try {
      const validated = await validateExternalResource(resourceType);
      upsertResource(validated);
      setMessage(
        validated.validation_status === "valid"
          ? "Resource path is valid."
          : "Resource path needs attention."
      );
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setValidatingType(null);
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

  return (
    <section className="settings-page">
      <div className="settings-header">
        <div>
          <span className="settings-eyebrow">Configuration</span>
          <h1>Settings</h1>
          <p>Control the paths ConnLab checks before shared workbook and folder workflows.</p>
        </div>
      </div>

      {loading && <LoadingState label="Loading settings" />}
      {error && <ErrorMessage message={error} />}
      {message && <p className="settings-message">{message}</p>}

      {!loading && (
        <SettingsExternalResourcesPanel
          resources={resources}
          savingType={savingType}
          validatingType={validatingType}
          onSave={handleSave}
          onValidate={handleValidate}
        />
      )}
    </section>
  );
}
