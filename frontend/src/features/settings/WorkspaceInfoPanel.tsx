import { useEffect, useState } from "react";
import { getWorkspaceInfo, type WorkspaceInfo } from "../../api/existingProjects";

export function WorkspaceInfoPanel() {
  const [info, setInfo] = useState<WorkspaceInfo | null>(null);
  const [error, setError] = useState(false);
  const [retry, setRetry] = useState(0);
  const [open, setOpen] = useState(false);
  useEffect(() => {
    if (!open) return;
    let current = true; setError(false);
    void getWorkspaceInfo().then(value => {if (current) setInfo(value);}).catch(() => {if (current) setError(true);});
    return () => {current = false;};
  }, [retry, open]);
  return <section className="settings-panel workspace-info" aria-label="Current data workspace">
    <h2 className="ui-panel-title">Current data workspace</h2>
    <p>Development, packaged and custom workspaces can contain different project lists. View the connected database and program details here. This does not switch or merge databases.</p>
    <button type="button" aria-expanded={open} onClick={() => setOpen(value => !value)}>{open ? "Hide workspace details" : "Show workspace details"}</button>
    {open && (error ? <div role="alert">Workspace information is unavailable. <button type="button" onClick={() => setRetry(x => x+1)}>Retry workspace information</button></div>
      : !info ? <p role="status">Loading workspace information…</p> : <>
        <dl><dt>Program mode</dt><dd>{info.runtime_mode}</dd><dt>Program version</dt><dd>{info.release.version || info.application_version}</dd>
          <dt>Connected database</dt><dd>{info.database_path || "Unavailable"}</dd><dt>Data folder</dt><dd>{info.data_directory}</dd>
          <dt>Configuration file</dt><dd>{info.config_path}</dd><dt>SQLite user_version</dt><dd>{info.sqlite_user_version ?? "Unavailable"}</dd></dl>
        <p>{info.schema_status === "unversioned" ? "No unified schema compatibility version is recorded (user_version = 0)." : "The reported value alone does not establish version compatibility."}</p>
        <p>Development, packaged and custom workspaces can contain different project lists. Keep development and tests on isolated copies. This panel does not switch or merge databases.</p>
        {Object.keys(info.release).length > 0 && <details><summary>Release details</summary><dl>{Object.entries(info.release).map(([key,value]) => <div key={key}><dt>{key}</dt><dd>{value}</dd></div>)}</dl></details>}
      </>)}
  </section>;
}
