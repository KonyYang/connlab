import { useEffect, useState, type ReactElement } from "react";
import {
  ApiRequestError,
  fetchConfirmedMatrixAuthorityHistory,
  type ConfirmedMatrixAuthorityHistory,
} from "../../api/client";

type AuthorityChangeHistoryPanelProps = {
  projectId: string;
};

type HistoryState = "loading" | "ready" | "error";

export function AuthorityChangeHistoryPanel({
  projectId,
}: AuthorityChangeHistoryPanelProps): ReactElement {
  const [state, setState] = useState<HistoryState>("loading");
  const [history, setHistory] = useState<ConfirmedMatrixAuthorityHistory | null>(null);

  useEffect(() => {
    let active = true;
    setState("loading");
    setHistory(null);
    void fetchConfirmedMatrixAuthorityHistory(projectId)
      .then((response) => {
        if (!active) {
          return;
        }
        setHistory(response);
        setState("ready");
      })
      .catch((error: unknown) => {
        if (!active) {
          return;
        }
        if (error instanceof ApiRequestError && error.status === 404) {
          setHistory({ project_id: projectId, entries: [] });
          setState("ready");
          return;
        }
        console.error("Failed to load authority change history.", error);
        setState("error");
      });
    return () => {
      active = false;
    };
  }, [projectId]);

  return (
    <section
      className="runtime-console-authority-history"
      aria-label="Authority Change History"
    >
      <header>
        <p className="eyebrow">Authority history</p>
        <h4>Authority Change History</h4>
      </header>
      {state === "loading" ? <p className="fine-print">Loading authority history...</p> : null}
      {state === "error" ? (
        <p className="error">Unable to load authority history. Try again later.</p>
      ) : null}
      {state === "ready" && history && history.entries.length === 0 ? (
        <p className="runtime-console-matrix-projection-empty">No confirmed authority history yet.</p>
      ) : null}
      {state === "ready" && history && history.entries.length > 0 ? (
        <ul>
          {history.entries.map((entry) => (
            <li key={entry.confirmed_matrix_id}>
              <div className="runtime-console-authority-history-line">
                <strong>Revision {entry.confirmed_revision}</strong>
                {entry.is_active_authority ? <span>Current authority</span> : <span>Superseded</span>}
              </div>
              <p>{entry.change_summary}</p>
              <small>
                Confirmed by {entry.confirmed_by} at {entry.confirmed_at}
              </small>
              {entry.record_regeneration_recommended ? (
                <em>Record draft may need regeneration.</em>
              ) : null}
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}
