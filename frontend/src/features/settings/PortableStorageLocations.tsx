import { useState } from "react";
import { requestJson } from "../../api/client";
import type { StoragePurpose } from "../../runtimeEnvironment";
import { ErrorMessage } from "../../components/common/ErrorMessage";

const purposes: StoragePurpose[] = ["Projects", "Library", "TemporaryProjects", "Template"];
const labels = { Projects: "Projects", Library: "Materials library", TemporaryProjects: "Temporary projects", Template: "Templates" };

export function PortableStorageLocations({ locations, root, warnings }: {
  locations: Record<StoragePurpose, string>;
  root?: string | null;
  warnings: string[];
}) {
  const [error, setError] = useState("");
  function openButton(purpose: StoragePurpose | "Root", path: string) {
    return <button className="ui-secondary-action" type="button" aria-label={`Open folder: ${path}`}
      onClick={async () => {
        setError("");
        try {
          await requestJson(`/api/runtime-storage/open/${purpose}`, { method: "POST" });
        } catch (cause) {
          setError(cause instanceof Error ? cause.message : `Could not open ${path}`);
        }
      }}>Open folder</button>;
  }

  return <section className="settings-panel settings-storage" aria-label="Business files">
    <h2 className="ui-panel-title">Business files</h2>
    {root
      ? <div className="settings-storage-line"><span>{root}</span>{openButton("Root", root)}</div>
      : <details><summary>View folder locations</summary>
          {purposes.map(purpose => <div className="settings-storage-line" key={purpose}>
            <span><strong>{labels[purpose]}</strong> {locations[purpose]}</span>
            {locations[purpose] && openButton(purpose, locations[purpose])}
          </div>)}
        </details>}
    {warnings.length > 0 && <div role="alert"><strong>Storage needs attention</strong>
      <ul>{warnings.map(warning => <li key={warning}>{warning}</li>)}</ul></div>}
    {error && <ErrorMessage message={error} />}
  </section>;
}
