import type { ReactElement } from "react";
import { ErrorMessage } from "../../components/common/ErrorMessage";
import { LoadingState } from "../../components/common/LoadingState";
import { useRuntimeProjectionPrototype } from "./useRuntimeProjectionPrototype";

export function RuntimeProjectionPrototypeView(): ReactElement {
  const model = useRuntimeProjectionPrototype();

  if (model.loading && !model.snapshot) {
    return <LoadingState label="Loading runtime projection prototype..." />;
  }

  return (
    <section className="runtime-projection-prototype-page">
      <div className="runtime-projection-prototype-dev-banner" role="note" aria-label="Development prototype notice">
        <span className="runtime-projection-prototype-dev-badge">Dev Prototype</span>
        <span className="runtime-projection-prototype-dev-text">
          This is a read-only development prototype for validating runtime projection API consumption. Not part of production Workbench.
        </span>
      </div>

      <header className="runtime-projection-prototype-header">
        <div>
          <p className="runtime-projection-prototype-eyebrow">Read-only prototype</p>
          <h2>Runtime Projection Consumer</h2>
          <p>
            This prototype consumes the typed runtime projection snapshot API and renders matrix overview plus optional selected step workspace.
          </p>
        </div>
        <button className="ui-secondary-action" type="button" onClick={() => void model.reload()}>
          Refresh snapshot
        </button>
      </header>

      {model.error && <ErrorMessage message={model.error} />}

      {model.snapshot && (
        <div className="runtime-projection-prototype-grid">
          <section className="runtime-projection-prototype-panel">
            <h3>Snapshot Summary</h3>
            <dl className="runtime-projection-prototype-meta">
              <div>
                <dt>Project</dt>
                <dd>{model.snapshot.project_reference}</dd>
              </div>
              <div>
                <dt>Matrix</dt>
                <dd>{model.snapshot.matrix_reference}</dd>
              </div>
              <div>
                <dt>Total Tokens</dt>
                <dd>{model.snapshot.runtime_projection_summary.total_tokens}</dd>
              </div>
              <div>
                <dt>Group Count</dt>
                <dd>{model.snapshot.runtime_projection_summary.group_count}</dd>
              </div>
            </dl>
            <div className="runtime-projection-prototype-warnings">
              <h4>Parser Warnings</h4>
              {model.snapshot.parser_warnings.length === 0 ? (
                <p>None</p>
              ) : (
                <ul>
                  {model.snapshot.parser_warnings.map((warning) => (
                    <li key={warning}>{warning}</li>
                  ))}
                </ul>
              )}
            </div>
          </section>

          <section className="runtime-projection-prototype-panel">
            <h3>Matrix Overview</h3>
            {model.snapshot.matrix_overview.groups.length === 0 ? (
              <p className="runtime-projection-prototype-empty">No projection tokens.</p>
            ) : (
              <div className="runtime-projection-prototype-groups">
                {model.snapshot.matrix_overview.groups.map((group) => (
                  <article className="runtime-projection-prototype-group" key={group.group_identity}>
                    <header>
                      <strong>{group.group_label}</strong>
                      <span>
                        {group.total_tokens} tokens / {group.unique_sequences} sequences
                      </span>
                    </header>
                    <div className="runtime-projection-prototype-token-list">
                      {group.tokens.map((token) => (
                        <button
                          className={`runtime-projection-token${model.selectedTokenReference === token.token_reference ? " is-selected" : ""}`}
                          key={token.token_reference}
                          type="button"
                          onClick={() => model.setSelectedTokenReference(token.token_reference)}
                        >
                          <span className="runtime-projection-token-seq">{token.sequence_number}{token.suffix_note ?? ""}</span>
                          <span className="runtime-projection-token-meta">{token.attention_projection ?? "none"} / {token.stale_projection ?? "unknown"}</span>
                        </button>
                      ))}
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>

          <section className="runtime-projection-prototype-panel">
            <h3>Step Workspace</h3>
            {!model.snapshot.step_workspace ? (
              <p className="runtime-projection-prototype-empty">Select a token to load workspace projection.</p>
            ) : !model.snapshot.step_workspace.found || !model.snapshot.step_workspace.selected_token ? (
              <p className="runtime-projection-prototype-empty">Selected token was not found in current projection snapshot.</p>
            ) : (
              <dl className="runtime-projection-prototype-meta">
                <div>
                  <dt>Token</dt>
                  <dd>{model.snapshot.step_workspace.selected_token.token_reference}</dd>
                </div>
                <div>
                  <dt>Group</dt>
                  <dd>{model.snapshot.step_workspace.group_label}</dd>
                </div>
                <div>
                  <dt>Lifecycle</dt>
                  <dd>{model.snapshot.step_workspace.selected_token.lifecycle_projection ?? "unknown"}</dd>
                </div>
                <div>
                  <dt>Evidence</dt>
                  <dd>{model.snapshot.step_workspace.selected_token.evidence_projection ?? "unknown"}</dd>
                </div>
                <div>
                  <dt>Report Sync</dt>
                  <dd>{model.snapshot.step_workspace.selected_token.report_sync_projection ?? "unknown"}</dd>
                </div>
                <div>
                  <dt>Attention</dt>
                  <dd>{model.snapshot.step_workspace.selected_token.attention_projection ?? "none"}</dd>
                </div>
              </dl>
            )}
          </section>
        </div>
      )}
    </section>
  );
}
