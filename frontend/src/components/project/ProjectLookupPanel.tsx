import { useEffect, useState, type FormEvent, type ReactElement } from "react";
import {
  getSampleSummary,
  getTestingSummary,
  lookupProjects,
  type ProjectLookupRow,
  type SampleSummary,
  type TestingSummary
} from "../../api/client";

type ProjectLookupPanelProps = {
  projectId: string;
};

export function ProjectLookupPanel({ projectId }: ProjectLookupPanelProps): ReactElement {
  const [sampleSummary, setSampleSummary] = useState<SampleSummary | null>(null);
  const [testingSummary, setTestingSummary] = useState<TestingSummary | null>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<ProjectLookupRow[]>([]);
  const [lookupError, setLookupError] = useState<string | null>(null);

  useEffect(() => {
    void loadSummaries();
  }, [projectId]);

  async function loadSummaries(): Promise<void> {
    try {
      const [samples, testing] = await Promise.all([
        getSampleSummary(projectId),
        getTestingSummary(projectId)
      ]);
      setSampleSummary(samples);
      setTestingSummary(testing);
      setLookupError(null);
    } catch (error) {
      setLookupError(error instanceof Error ? error.message : "Lookup summary failed.");
    }
  }

  async function runLookup(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    const text = query.trim();
    if (!text) {
      setResults([]);
      return;
    }
    try {
      setResults(await lookupProjects(text));
      setLookupError(null);
    } catch (error) {
      setLookupError(error instanceof Error ? error.message : "Project lookup failed.");
    }
  }

  return (
    <section className="project-lookup-panel" aria-label="Project lookup and summaries">
      <div className="lookup-panel-heading">
        <div>
          <p className="eyebrow">Read-only lookup</p>
          <h3>Project evidence and testing summary</h3>
        </div>
        <form className="lookup-search-form" onSubmit={runLookup}>
          <input
            aria-label="Search projects"
            placeholder="Search LTR, part, product, requestor"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <button className="secondary-action" type="submit">Search</button>
        </form>
      </div>

      {lookupError && <p className="blocking-copy">{lookupError}</p>}

      <div className="lookup-summary-grid">
        <section className="lookup-summary-section">
          <div className="lookup-section-heading">
            <span>Sample summary</span>
            <strong>{sampleSummary?.samples.length ?? 0} samples</strong>
          </div>
          <div className="lookup-table-wrap">
            <table className="lookup-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Part</th>
                  <th>Revision</th>
                  <th>Lot</th>
                  <th>Qty</th>
                </tr>
              </thead>
              <tbody>
                {(sampleSummary?.samples ?? []).map((sample) => (
                  <tr key={sample.sample_id}>
                    <td>{sample.product_name}</td>
                    <td>{sample.part_number}</td>
                    <td>{sample.revision ?? "Not recorded"}</td>
                    <td>{sample.lot_or_traceability ?? "Not recorded"}</td>
                    <td>{sample.quantity ?? "Not recorded"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="lookup-summary-section">
          <div className="lookup-section-heading">
            <span>Testing condition and method</span>
            <strong>{testingSummary?.test_type ?? "Review required"}</strong>
          </div>
          <dl className="lookup-facts">
            <div>
              <dt>Requested testing</dt>
              <dd>{testingSummary?.requested_testing ?? "Not recorded"}</dd>
            </div>
            <div>
              <dt>Sample condition</dt>
              <dd>{testingSummary?.sample_condition ?? "Not recorded"}</dd>
            </div>
            <div>
              <dt>Completion date</dt>
              <dd>{testingSummary?.requested_completion_date ?? "Not recorded"}</dd>
            </div>
            <div>
              <dt>Lab / personnel</dt>
              <dd>{[testingSummary?.lab, testingSummary?.assigned_personnel].filter(Boolean).join(" / ") || "Not recorded"}</dd>
            </div>
            <div>
              <dt>Specifications</dt>
              <dd>{testingSummary?.applicable_specifications.join(", ") || "Not recorded"}</dd>
            </div>
          </dl>
        </section>
      </div>

      {results.length > 0 && (
        <div className="lookup-results">
          {results.map((row) => (
            <article key={row.project_id}>
              <strong>{row.ltr_numbers[0] ?? row.project_no ?? row.project_id}</strong>
              <span>{row.product_name} · {row.requestor} · {row.status}</span>
              <em>Matched: {row.matched_fields.join(", ")}</em>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
