import { useEffect, useMemo, useState, type ReactElement } from "react";
import {
  ApiRequestError,
  fetchConfirmedMatrixTestRecordPreview,
  type ConfirmedMatrixTestRecordPreview
} from "../../api/client";

type PreviewState = "loading" | "ready" | "empty" | "not_ready" | "error";

type TestRecordPreviewSmokePanelProps = {
  projectId: string;
};

export function TestRecordPreviewSmokePanel({
  projectId
}: TestRecordPreviewSmokePanelProps): ReactElement {
  const [state, setState] = useState<PreviewState>("loading");
  const [preview, setPreview] = useState<ConfirmedMatrixTestRecordPreview | null>(null);

  useEffect(() => {
    let active = true;
    setState("loading");
    setPreview(null);
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
        console.error("Failed to load confirmed matrix test record preview.", error);
        setState("error");
      });
    return () => {
      active = false;
    };
  }, [projectId]);

  const groupCount = preview?.groups.length ?? 0;
  const totalSteps = useMemo(
    () => (preview ? preview.groups.reduce((sum, group) => sum + group.step_count, 0) : 0),
    [preview]
  );

  return (
    <section className="runtime-console-test-record-preview" aria-label="Test Record Preview">
      <header className="runtime-console-test-record-preview-header">
        <div>
          <p className="eyebrow">Derived output smoke</p>
          <h3>Test Record Preview</h3>
        </div>
        <span className="runtime-console-test-record-preview-mode">Confirmed authority, read-only</span>
      </header>

      {state === "loading" ? <p className="fine-print">Loading Test Record preview...</p> : null}
      {state === "not_ready" ? (
        <p className="runtime-console-test-record-preview-empty">
          No active confirmed matrix yet. Confirm Matrix authority first.
        </p>
      ) : null}
      {state === "empty" ? (
        <p className="runtime-console-test-record-preview-empty">
          Active confirmed matrix found, but no previewable steps are available.
        </p>
      ) : null}
      {state === "error" ? (
        <p className="error">Unable to load Test Record preview. Try again after confirming Matrix authority.</p>
      ) : null}
      {state === "ready" && preview ? (
        <>
          <div className="runtime-console-test-record-preview-summary">
            <span>Confirmed: {preview.confirmed_matrix_id}</span>
            <span>Groups: {groupCount}</span>
            <span>Steps: {totalSteps}</span>
          </div>
          <div className="runtime-console-test-record-preview-groups">
            {preview.groups.map((group) => (
              <article className="runtime-console-test-record-preview-group" key={group.group_key}>
                <header>
                  <strong>
                    {group.group_label} ({group.group_key})
                  </strong>
                  <span>Samples: {group.sample_quantity_expression || "-"}</span>
                  <span>Steps: {group.step_count}</span>
                </header>
                <table>
                  <thead>
                    <tr>
                      <th>Seq</th>
                      <th>Token</th>
                      <th>Test item</th>
                      <th>Section</th>
                      <th>Method</th>
                      <th>Condition</th>
                      <th>Requirement</th>
                    </tr>
                  </thead>
                  <tbody>
                    {group.steps.map((step, index) => (
                      <tr key={`${group.group_key}:${step.raw_token}:${index}`}>
                        <td>{step.sequence}</td>
                        <td>{step.raw_token}</td>
                        <td>{step.test_item}</td>
                        <td>{step.section}</td>
                        <td>{step.method || "-"}</td>
                        <td>{step.condition || "-"}</td>
                        <td>{step.requirement || "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </article>
            ))}
          </div>
        </>
      ) : null}
    </section>
  );
}
