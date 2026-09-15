# Project customer report background progress

## Boundary

Report Workspace uses project-scoped background jobs for Customer report generation. The legacy
synchronous API remains available. `/tools` retains its standalone workflow and shares only the stage
presentation and existing isolated Word runner; it does not inherit project authority rules.

`ProjectCustomerReportJobService` owns task identity, per-project concurrency, result retention and
download leases. `ProjectCustomerReportRunner` acquires the existing project filesystem lock before
opening an independent database session and selecting the source. It rechecks registry/folder workflow
state. The short bounded lock wait accommodates the start request's registry guard teardown.

`CustomerReportProjectionService` still owns Internal Report selection, approved-template selection
inputs, fingerprints, missing-target confirmation and official publication through
`ReportPublicationGateway`. Background execution does not publish directly. Source identity is checked
again after generation. The existing staged write, archive and atomic replacement rules remain intact.

## API and UI

Base: `/api/projects/{project_id}/report-workspace/current-customer-report/jobs`.

- `POST`: submit the existing expected Internal Report and Customer report SHA-256 fingerprints.
- `GET /latest`: recover the current retained project task, or `null`.
- `GET /{operation_id}`: read status, real stage, elapsed seconds, error code and result metadata.
- `GET /{operation_id}/download`: download a retained managed copy without generating again.

All operation lookups verify project ownership. Unknown/expired operations return 410. Jobs are
process-local: restart does not claim to resume an interrupted Word operation. A browser recovery hint
helps explain a disappeared task; the server is always the authority.

Frontend states distinguish start uncertainty, generation/publication failure, temporary polling
failure and download failure. A lost start response requires a status check before another submission.
Polling failures retain the last known task and do not mark it failed. Returning to the page recovers
progress/results without automatically downloading again. Only the page that submitted a managed job
automatically attempts the download once; a retained result supports manual retry.

Elapsed time is the server's measured duration, with local wall-clock advancement between successful
polls. Stage labels come from actual backend events; there is no simulated percentage.

The missing-after-preview code continues to open the existing explicit regeneration confirmation.
Cancelling does not recreate a missing report. A failed job can be retried explicitly after reviewing
the current report and its fingerprints.

## Resource policy and limits

Terminal job metadata and managed download artifacts are retained for one hour. Download leases
prevent expiration from deleting an in-flight response. Cleanup is restricted to operation-owned
temporary storage; official reports and History files are never cleanup targets. The same project lock
serializes publication with registry moves, folder generation and legacy synchronous mutations.

Word runs through the existing isolated child entrypoint with its existing stage-stall and absolute
timeout limits. Sessions, child processes and response leases must be released on both success and
failure. Server restarts invalidate task IDs; users should review the current official report before
starting again, because publication may have finished just before a lost response.

## Regression and acceptance

Developer RED/GREEN covers per-project deduplication, real progress, session/lock ownership, source
identity changes, failure classification, temporary polling failure, lost start responses, retained
download retries and refresh/reentry recovery. Existing report publication, projection, Word-runner,
legacy report API and Tools tests remain compatibility protection.

Final QA must run the affected backend/frontend matrix, production build and isolated browser smoke.
Official-file smoke must use a temporary fixture or copied project, never an existing business report.
Development/frozen child dispatch tests do not by themselves constitute testing a built release package.

### Open review boundary

At the current implementation checkpoint, forced timeout stops the isolated Python child, but cannot
prove termination of its separate Word COM server: killing Python bypasses the child's normal `Quit`
cleanup. A safe extension must publish the task-owned Word PID and creation identity, verify ownership,
and terminate only that process; never terminate all Word instances or infer ownership from a process
list difference. The gateway/child changes for that extension await explicit scope approval. Do not
claim complete Office timeout cleanup or final acceptance until this boundary is resolved or accepted.

The host permits four retained agent contexts. Planner/QA and Reviewer/Integrator are reused contexts,
each separate from implementation; this is not a five-independent-context execution.

### Verified checkpoint (2026-09-15)

- Backend QA: 89 passing tests across 14 relevant files, including development/frozen child dispatch.
- Frontend QA: 39 passing tests across Workspace, lifecycle hook, workspace model and Tools.
- Production build passed (160 modules). Two test-only constructor typing omissions were fixed;
  the affected 10 hook tests and build were rerun successfully.
- Main-agent in-app browser smoke against an isolated loopback service verified managed generation,
  real event/elapsed display, running-task refresh recovery, automatic initial download, retained repeat
  download, and official replacement with History. The old customer file's SHA-256 matched its archive,
  and all database sessions were returned. Tools UI was inspected; Tools generation has automated coverage.
- The browser harness used a controlled DOCX writer, with real API/jobs/runner/publication and temporary
  SQLite/files. It did not exercise Word COM or an actual release EXE, and did not modify business reports.
- Reviewer findings on expired-download guidance, cancelled-job cleanup, and target changes during
  pre-publication source verification were fixed and regression-protected.

The task remains running pending the Word ownership decision above; this checkpoint is not final
acceptance or `ready_for_close`.
