import { useEffect, useMemo, useState, type ReactElement } from "react";
import {
  ApiRequestError,
  fetchConfirmedMatrixTestRecordPreview,
  type ConfirmedMatrixTestRecordPreview,
} from "../../api/client";
import {
  buildMatrixProjectionViewModel,
  findMatrixProjectionToken,
  type MatrixProjectionTokenCell,
  toVisibleMatrixProjectionStatusTone,
  type MatrixProjectionVisibleStatusTone,
} from "./projectWorkbenchMatrixProjectionSelectors";

type PreviewState = "loading" | "ready" | "empty" | "not_ready" | "error";

type ProjectWorkbenchMatrixProjectionPanelProps = {
  projectId: string;
  onTokenSelect?: (token: MatrixProjectionTokenCell | null) => void;
};

const STATUS_LABELS: Record<MatrixProjectionVisibleStatusTone, string> = {
  not_started: "Not started",
  in_progress: "In progress",
  passed: "Pass",
  failed: "Failed",
};

export function ProjectWorkbenchMatrixProjectionPanel({
  projectId,
  onTokenSelect,
}: ProjectWorkbenchMatrixProjectionPanelProps): ReactElement {
  const [state, setState] = useState<PreviewState>("loading");
  const [preview, setPreview] = useState<ConfirmedMatrixTestRecordPreview | null>(
    null
  );
  const [selectedTokenReference, setSelectedTokenReference] = useState<
    string | null
  >(null);

  useEffect(() => {
    let active = true;
    setState("loading");
    setPreview(null);
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
    };
  }, [onTokenSelect, projectId]);

  const viewModel = useMemo(
    () =>
      preview && preview.preview_status === "ready"
        ? buildMatrixProjectionViewModel(preview)
        : null,
    [preview]
  );
  const selectedToken = useMemo(
    () =>
      viewModel
        ? findMatrixProjectionToken(viewModel, selectedTokenReference)
        : null,
    [selectedTokenReference, viewModel]
  );

  return (
    <section className="runtime-console-matrix-projection" aria-label="Matrix Projection">
      <p className="runtime-console-matrix-projection-note">Read-only authority view</p>

      {state === "loading" ? <p className="fine-print">Loading Matrix projection...</p> : null}
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
          <div className="runtime-console-matrix-projection-legend" aria-label="Status color legend">
            {Object.entries(STATUS_LABELS).map(([tone, label]) => (
              <span className={`runtime-console-matrix-token-status-${tone}`} key={tone}>
                {label}
              </span>
            ))}
          </div>
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
                    <td key={`status:${group.groupKey}`}>Pending execution data</td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
          {selectedToken ? (
            <p className="runtime-console-matrix-projection-selection">
              Selected token: {selectedToken.groupLabel} / {selectedToken.rawToken}
            </p>
          ) : null}
        </>
      ) : null}
    </section>
  );
}
