import { useEffect, useMemo, useRef, useState, type ReactElement } from "react";
import {
  ApiRequestError,
  fetchConfirmedMatrixTestRecordPreview,
  getGroupCompletion,
  getProjectLifecycle,
  updateGroupCompletion,
  type GroupCompletion,
  type ConfirmedMatrixTestRecordPreview,
} from "../../api/client";
import {
  buildMatrixProjectionViewModel,
  type MatrixProjectionTokenCell,
  toVisibleMatrixProjectionStatusTone,
} from "./projectWorkbenchMatrixProjectionSelectors";

type PreviewState = "loading" | "ready" | "empty" | "not_ready" | "error";

type ProjectWorkbenchMatrixProjectionPanelProps = {
  projectId: string;
  onTokenSelect?: (token: MatrixProjectionTokenCell | null) => void;
};

export function ProjectWorkbenchMatrixProjectionPanel({
  projectId,
  onTokenSelect,
}: ProjectWorkbenchMatrixProjectionPanelProps): ReactElement {
  const [state, setState] = useState<PreviewState>("loading");
  const [completion, setCompletion] = useState<GroupCompletion | null>(null);
  const [completionError, setCompletionError] = useState<string | null>(null);
  const [completionBusy, setCompletionBusy] = useState(false);
  const [canEdit, setCanEdit] = useState(false);
  const epoch = useRef(0);
  const [preview, setPreview] = useState<ConfirmedMatrixTestRecordPreview | null>(
    null
  );
  const [selectedTokenReference, setSelectedTokenReference] = useState<
    string | null
  >(null);

  useEffect(() => {
    const current = ++epoch.current;
    let active = true;
    setState("loading");
    setPreview(null);
    setCompletion(null);
    setCompletionBusy(false);
    setCanEdit(false);
    setCompletionError(null);
    void getGroupCompletion(projectId).then((value) => { if (active) setCompletion(value); }).catch((error: unknown) => { if (active && !(error instanceof ApiRequestError && error.status === 404)) setCompletionError("Group completion is unavailable."); });
    void getProjectLifecycle(projectId).then((value) => { if (active) setCanEdit(!value.readonly && (!value.registry_state || value.registry_state === "active")); }).catch(() => { if (active) setCanEdit(false); });
    setSelectedTokenReference(null);
    onTokenSelect?.(null);
    void fetchConfirmedMatrixTestRecordPreview(projectId)
      .then((response) => {
        if (!active) {
          return;
        }
        setPreview(response);
        setState(response.preview_status === "empty" ? "empty" : "ready");
      })
      .catch((error: unknown) => {
        if (!active) {
          return;
        }
        if (error instanceof ApiRequestError && error.status === 404) {
          setState("not_ready");
          return;
        }
        console.error("Failed to load confirmed Matrix projection.", error);
        setState("error");
      });
    return () => {
      active = false;
      if (epoch.current === current) epoch.current++;
    };
  }, [onTokenSelect, projectId]);

  const viewModel = useMemo(
    () =>
      preview && preview.preview_status === "ready"
        ? buildMatrixProjectionViewModel(preview)
        : null,
    [preview]
  );
  function renderCompletion(item: GroupCompletion["groups"][number]): ReactElement {
    const current = epoch.current;
    return <label key={item.group_key}><input type="checkbox" aria-label={`${item.group_label} completed`}
      checked={item.completed} disabled={!canEdit || completionBusy} onChange={(event) => {
        if (!completion) return;
        setCompletionBusy(true); setCompletionError(null);
        void updateGroupCompletion(projectId, item.group_key, completion.confirmed_matrix_id, event.target.checked)
          .then((value) => { if (epoch.current === current) setCompletion(value); })
          .catch(() => { if (epoch.current === current) setCompletionError("Unable to update group completion. Refresh the project and try again."); })
          .finally(() => { if (epoch.current === current) setCompletionBusy(false); });
      }} /> {item.needs_review ? "Review needed" : "Completed"}</label>;
  }
  useEffect(() => {
    if (state !== "ready" || !viewModel || selectedTokenReference) {
      return;
    }
    const firstToken = findFirstProjectionToken(viewModel);
    if (!firstToken) {
      return;
    }
    setSelectedTokenReference(firstToken.tokenReference);
    onTokenSelect?.(firstToken);
  }, [onTokenSelect, selectedTokenReference, state, viewModel]);
  return (
    <section className="runtime-console-matrix-projection" aria-label="Matrix Projection">
      {completionError ? <p className="error" role="alert">{completionError}</p> : null}
      {completion && viewModel && completion.confirmed_matrix_id !== viewModel.confirmedMatrixId ? <p role="alert">Matrix changed. Refresh the project to update group completion.</p> : null}
      {completion && (!viewModel || completion.confirmed_matrix_id === viewModel.confirmedMatrixId) && completion.groups.some((item) => !viewModel?.groupColumns.some((group) => group.groupKey === item.group_key)) ? (
        <div aria-label="Other groups">{completion.groups.filter((item) => !viewModel?.groupColumns.some((group) => group.groupKey === item.group_key)).map((item) => <div key={item.group_key}>{item.group_label}: {renderCompletion(item)}</div>)}</div>
      ) : null}
      {state === "not_ready" ? (
        <p className="runtime-console-matrix-projection-empty">
          No active confirmed matrix yet. Confirm Matrix authority first.
        </p>
      ) : null}
      {state === "empty" ? (
        <p className="runtime-console-matrix-projection-empty">
          Active confirmed matrix found, but no previewable Matrix tokens are available.
        </p>
      ) : null}
      {state === "error" ? (
        <p className="error">Unable to load Matrix projection. Try again after confirming Matrix authority.</p>
      ) : null}

      {state === "ready" && viewModel ? (
        <>
          <div className="runtime-console-matrix-projection-table-wrap">
            <table className="runtime-console-matrix-projection-table">
              <thead>
                <tr>
                  <th>Test item</th>
                  {viewModel.groupColumns.map((group) => (
                    <th key={group.groupKey}>{group.groupLabel}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {viewModel.rows.map((row) => (
                  <tr key={row.rowKey}>
                    <th scope="row">{row.testItem}</th>
                    {viewModel.groupColumns.map((group) => {
                      const cells = row.cellsByGroupKey[group.groupKey] ?? [];
                      return (
                        <td key={`${row.rowKey}:${group.groupKey}`}>
                          {cells.length > 0 ? (
                            <div className="runtime-console-matrix-token-stack">
                              {cells.map((cell) => {
                                const visibleStatusTone = toVisibleMatrixProjectionStatusTone(
                                  cell.statusTone
                                );
                                return (
                                  <button
                                    className={`runtime-console-matrix-token runtime-console-matrix-token-status-${visibleStatusTone}${
                                    selectedTokenReference === cell.tokenReference
                                      ? " is-selected"
                                      : ""
                                    }`}
                                    key={cell.tokenReference}
                                    type="button"
                                    onClick={() => {
                                      setSelectedTokenReference(cell.tokenReference);
                                      onTokenSelect?.(cell);
                                    }}
                                  >
                                    {cell.rawToken}
                                  </button>
                                );
                              })}
                            </div>
                          ) : (
                            <span className="runtime-console-matrix-empty-cell">-</span>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
                <tr className="runtime-console-matrix-meta-row">
                  <th scope="row">Sample sizes</th>
                  {viewModel.groupColumns.map((group) => (
                    <td key={`sample:${group.groupKey}`}>
                      {group.sampleQuantityExpression || "-"}
                    </td>
                  ))}
                </tr>
                <tr className="runtime-console-matrix-meta-row">
                  <th scope="row">Estimated completion date</th>
                  {viewModel.groupColumns.map((group) => (
                    <td key={`eta:${group.groupKey}`}>Not scheduled</td>
                  ))}
                </tr>
                <tr className="runtime-console-matrix-meta-row">
                  <th scope="row">Status</th>
                  {viewModel.groupColumns.map((group) => (
                    <td key={`status:${group.groupKey}`}>
                      {completion?.confirmed_matrix_id === viewModel.confirmedMatrixId && completion.groups.find((item) => item.group_key === group.groupKey) ? (() => {
                        const item = completion.groups.find((entry) => entry.group_key === group.groupKey)!;
                        return renderCompletion(item);
                      })() : "Unavailable"}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </>
      ) : null}
    </section>
  );
}

function findFirstProjectionToken(
  viewModel: ReturnType<typeof buildMatrixProjectionViewModel>
): MatrixProjectionTokenCell | null {
  for (const row of viewModel.rows) {
    for (const group of viewModel.groupColumns) {
      const firstCell = row.cellsByGroupKey[group.groupKey]?.[0];
      if (firstCell) {
        return firstCell;
      }
    }
  }
  return null;
}
