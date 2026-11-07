# Report automation batch 4 — result meaning and scoped adoption

Status: implementation and Developer targeted validation complete; independent review/QA pending. Not accepted or published.

Task: `TASK_REPORT_RESULT_SEMANTICS_20261107`. Batch 3 was accepted and locally closed.
This batch extends the existing retained source → confirmed result → batch preview → working-copy
chain. Real reports, templates and project materials remain read-only. No push or formal release.

## Implementation order

1. Adopt Tools qualitative matrices with their original observations and evidence coverage, without
   inventing one curve per matrix cell or inheriting a Pass decision.
2. Separate specification/revision/authorization facts and bind date changes to an exact Word target.
3. Read electrical IR/DWV measurements with explicit sample/pair/stage/units and missing values.
4. Retain scoped external-result decisions and adopt selected temperature DOCX regions, preserving
   native charts without recalculating temperature data or copying unrelated project identity.
5. Represent multi-stage absolute R and ΔR independently; keep the existing LLCR dataset compatible.

## Safety and acceptance

- Missing measurements remain missing; a blank DWV result is not “no breakdown”.
- Source claims and current-project acceptance are separate. Special acceptance has a project and
  Matrix target, reviewer, reason and retained source/version; it is never a reusable global Pass.
- Multiple measurements belonging to one target are represented together, not silently superseded.
- Identical date text elsewhere in a document is not changed by a targeted date update.
- Only complete, safe selected DOCX regions and their internal relationships may be adopted; unsafe
  content remains unsupported/pending, not silently discarded.
- Existing snapshot hashes, source checks, overlap checks, idempotence and working-copy protection
  continue to apply. Original bytes stay unchanged on success and failure.
- Targeted public API/domain/document tests precede implementation. Independent review, final QA,
  isolated page smoke and Word visual acceptance follow the clean implementation subject.

## Explicitly outside this batch

No temperature calculation changes, generalized workflow engine, database authority migration,
automatic final publication, broad photo matching, template coverage overhaul or deployment work.
Batch 5/6 remain separate. Actual 032B applicability and exceptional acceptance are user decisions in
the product, not assumptions made by this development task.

## Evidence

Implemented public Report Workspace forms, retained API contracts and existing batch/working-copy adapters:

- Tools qualitative matrices retain sample/column observations; source Pass is not a Step outcome.
- Date facts bind to a source role and exact paragraph hash, independently of identical dates elsewhere.
- IR/DWV reads explicit horizontal or vertical cell addresses. Conditions have a source locator;
  missing leakage, breakdown, voltage or duration stays missing. Sheet/label conflicts require human
  comparison; this batch does not claim automated conflict interpretation.
- Scoped reference records retain source/version/location, adopted scope, adverse observations,
  project/Matrix identity and explicit applicability. Customer permission is separate. Exact visible
  adopted text may contain its reference identity; hidden fields/attributes and unrelated report
  sections remain fully audited for old identities and sensitive information.
- Selected DOCX temperature regions preserve tables/native charts/styles through a bounded adapter.
  External workbook charts require explicit frozen-cache permission and complete caches. No external
  file is fetched; no workbook or measurements are invented. Word series titles freeze to `c:v`.
  Source numbering, active content or unresolved styles/fonts/colors fail explicitly. Customer
  conversion reuses the same retained region if its converter removes the internal appendix.
- Multistage resistance supports direct absolute R, recorded ΔR, or explicit absolute-minus-baseline.
  This is not a rewrite of the existing LLCR dataset importer. Voltage/current conversion remains in
  the existing CR path; deduction-current combinations are not newly claimed as supported.

RED/GREEN slices: qualitative writer initially lacked its data summary branch; native region test
initially had no adapter; exact fact targeting initially lacked target lookup. Targeted tests now
cover each public chain, XLSX → confirm → reopen → batch Word, stale adopted source versions,
repeat native region replacement, scoped customer checks and customer native-curve restoration.
Developer targeted results will be recorded after final-byte validation below. Independent QA and
Word/page acceptance are deliberately not claimed here.

### Developer evidence (2026-11-07)

- Context: independent Developer, inherited GPT-6 Astra route; isolated branch
  `codex/report-result-semantics-20261107`, base `8ad205491a542fa9e2f68f22c0d95b51a969478d`.
- Python targeted matrix: 83 passed in 23.69s. Files: `test_report_result_semantics.py`,
  `test_report_authoring_schema.py`, `test_report_tools_package.py`, report_authoring tests
  `test_linked_region.py`, `test_word_facts.py`, `test_results_document.py`,
  `test_tools_results_document.py`, `test_batch_document.py`, `test_customer_audit.py`, and integration
  `test_report_authoring_api.py`, `test_report_semantic_results_api.py`, `test_report_batch_assembly_api.py`.
  Command prefix: `C:\PythonEnvs\connlab\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider`;
  isolated `--basetemp=tmp/batch4-developer-final`.
- After the final unit-suffix change, reran the affected domain and semantic API files: 7 passed in
  4.53s (`--basetemp=tmp/batch4-unit-suffix-final`). The original source string, including `>1000 MΩ`,
  is retained; conflicting cell/selected units are rejected. Unaffected tests above remain applicable.
- UI: `npm.cmd exec vitest -- run` for `ReportEvidenceResults`, `ReportToolsPackageImport`,
  `ReportAuthoringFeatures`, `ReportBatchPreparation`: 26 passed, four files, 1.48s; followed by
  `npm.cmd exec tsc -- --noEmit`, exit 0.
- Existing Python warning only: Starlette TestClient/httpx deprecation; no Office COM or real project
  writes in this Developer matrix. One PowerShell transport syntax retry occurred before command
  execution; no Git or file state changed in that failed invocation.
- Self-review Standards: no unresolved blocker; new adapters are bounded existing-chain modules,
  not a general framework. Spec: all five slices have public form/API/output support. Review risks
  remain native Word rendering on representative reports and independent regression coverage.

Actual 032B reference inspection by the orchestrator found the native curve links an external OLE
workbook, not an embedded one. Frozen caches are complete. The original X-axis title/300-tick visual
overlap remains a source-chart limitation; this task does not redesign or refit the source chart.
