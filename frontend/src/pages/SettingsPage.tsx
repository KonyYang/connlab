import {getRuntimeEnvironment} from "../runtimeEnvironment";
import { useState, type ReactElement } from "react";
import {
  downloadSupportDiagnosticBundle,
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
import { ReceiveSaveLocation } from "../features/settings/ReceiveSaveLocation";
import "../settings.css";
import { useSettingsResources } from "../features/settings/useSettingsResources";

export function SettingsPage(): ReactElement {
  const runtime = getRuntimeEnvironment();
  const storageWarnings = runtime?.storage_warnings ?? [];
  const showDefaultLocations = runtime?.environment === "release" && !runtime.storage_locations;
  const {resources, loading, error, setError, savingType, pathValidationMessages, handleSave, handlePathChange} = useSettingsResources(showDefaultLocations);
  const [exportingDiagnostics, setExportingDiagnostics] = useState(false);
  const [diagnosticsMessage, setDiagnosticsMessage] = useState<string | null>(null);

  async function handleBrowse(
    resourceType: ExternalResourceType
  ): Promise<string | null> {
    setError(null);
    if (hasDesktopPathPickerBridge()) {
      return pickExternalResourcePathFromDesktop(resourceType);
    }
    return null;
  }

  async function handleExportDiagnostics(): Promise<void> {
    setExportingDiagnostics(true);
    setDiagnosticsMessage(null);
    try {
      const result = await downloadSupportDiagnosticBundle();
      const objectUrl = window.URL.createObjectURL(result.blob);
      const anchor = document.createElement("a");
      anchor.href = objectUrl;
      anchor.download = result.fileName ?? "ConnLab_Diagnostics.zip";
      anchor.click();
      window.URL.revokeObjectURL(objectUrl);
      setDiagnosticsMessage("Diagnostic package downloaded.");
    } catch (err) {
      setDiagnosticsMessage(`Unable to export diagnostics: ${(err as Error).message}`);
    } finally {
      setExportingDiagnostics(false);
    }
  }

  return (
    <section className="settings-page">
      <div className="settings-header">
        <div>
          <h1>File Locations</h1>
        </div>
      </div>

      {storageWarnings.length > 0 && (
        <div className="settings-panel settings-storage" role="alert">
          <strong>Storage needs attention</strong>
          <ul>{storageWarnings.map(warning => <li key={warning}>{warning}</li>)}</ul>
        </div>
      )}
      {loading && <LoadingState label="Loading settings" />}
      {error && <ErrorMessage message={error} />}

      {!loading && (
        <SettingsExternalResourcesPanel
          showDefaultLocations={showDefaultLocations}
          receiveLocation={showDefaultLocations && <ReceiveSaveLocation />}
          resources={showDefaultLocations ? withDefaultLocations(resources) : resources}
          savingType={savingType}
          onSave={handleSave}
          browseEnabled={hasDesktopPathPickerBridge()}
          onBrowse={handleBrowse}
          pathValidationMessages={pathValidationMessages}
          onPathChange={handlePathChange}
        />
      )}

      <section className="settings-panel settings-support-panel">
        <div className="settings-panel-heading">
          <div>
            <h2 className="ui-panel-title">Support diagnostics</h2>
            <p>
              Export recent application logs and release details for troubleshooting.
              Project files, the database, and settings files are not included.
            </p>
          </div>
          <button
            type="button"
            className="ui-secondary-action"
            disabled={exportingDiagnostics}
            onClick={() => void handleExportDiagnostics()}
          >
            {exportingDiagnostics ? "Exporting..." : "Export diagnostic package"}
          </button>
        </div>
        {diagnosticsMessage && (
          <p className="settings-support-message" role="status">
            {diagnosticsMessage}
          </p>
        )}
      </section>
    </section>
  );
}

function withDefaultLocations(resources: ExternalResource[]):ExternalResource[]{
 const defaults=getRuntimeEnvironment()?.default_output_paths;
 if(!defaults)return resources;
 const rows=[...resources];
 for(const [resource_type,purpose] of [["project_output_root","Projects"],["temporary_materials_root","TemporaryMaterials"]] as const){
  if(!rows.some(row=>row.resource_type===resource_type)) rows.push({resource_id:`default-${resource_type}`,resource_type,path:defaults[purpose],active:true,validation_status:"not_validated",last_validated_at:null,validation_failure_reason:null,worksheet_name:null});
 }
 return rows;
}
