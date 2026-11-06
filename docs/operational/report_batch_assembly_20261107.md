# Report preparation and batch assembly (batch 3)

Status: implementation and isolated acceptance in progress; not yet accepted or released.
The retained [complete implementation plan](report_automation_plan_20261107.md) is the scope
reference. This batch connects existing result types; batches 4–6 are not implicitly activated.

## Intended user path

In Report Workspace, choose the working report, then **Prepare report batch**:

1. **Inspect materials and coverage** lists candidates from the controlled project directory and
   shows evidence against the confirmed Matrix. Missing folder access does not disable manual uploads.
2. Retain chosen sources with an explicit role. Inspection alone neither adopts a newer file nor
   changes an existing confirmation. Existing result import/confirmation remains available.
3. Select confirmed facts, results and existing photo assignments. LLCR uses its confirmed dataset
   as one unit because its entries share Appendix A; it is not recalculated as generic CR data.
4. **Preview selected updates** saves one exact plan, showing replacements, report destinations,
   omitted steps, unresolved decisions and conflicts. Unique Group/Step targets are resolved
   automatically; ambiguous or previously populated evidence regions require an explicit choice.
5. **Generate one working copy** applies the reviewed plan. It never overwrites the original,
   changes the formal current-report pointer, or interprets a generated file as formal approval.

Existing individual update controls remain under **Advanced individual updates**. Tools continue
to work independently of projects and retain their existing temperature calculations.

## Implementation boundaries

- Reuse Project Library ownership/member/path checks; no arbitrary client-supplied root or recursive
  ingestion of archives, caches, symlinks or junctions. Scanning uses bounded file metadata; adopting
  a selected file verifies its identity, exact bytes and role. Sources retain their relative origin.
- A source family is role + case-insensitive file name + relative origin. Two different directories
  cannot silently replace one another. Selecting A after B records a new source version even when
  the asset bytes already exist. Prior confirmations do not silently revive.
- Validate every selected source before saving one authoring revision. Partial validation failure
  must not leave half of a multi-source selection registered.
- Coverage separates available evidence, engineering decisions and evidence actually present in
  the chosen working copy. Only current valid applied results can satisfy a row; historic Pass,
  an invalidated result or a pending decision cannot establish completeness.
- A saved plan binds the exact working copy, actual selected source/mapping/dataset versions,
  Matrix context and resolved Word regions. Unrelated source additions do not invalidate it.
- Resolve all ordinary Word targets against the original tree before editing. Reject overlapping
  result cells, appendix identities, photographs and fact replacements. LLCR reserves Appendix A
  and reuses the established section writer. Batch table pagination changes stay within selected
  tables. If changed content reflows later Group headings in the same page-flow segment, only
  previously unspecified heading-to-table linkage is added; explicit pagination choices, page and
  section boundaries, and downstream table contents are preserved. The preview lists this change.
- One existing project write slot serializes writes. Intermediate edits are private; only one
  successful output is registered. No new workflow engine, DB schema or formal publishing route.
- A deterministic plan identity and atomic revision record allow a completed file to survive a
  database-registration gap. Retry verifies plan/source/Matrix/project/output before reusing it.
  Ordinary download expiry does not invalidate unregistered batch recovery evidence. Such records
  remain conservatively retained; this batch does not introduce a general cleanup policy.
- Incomplete or unowned output cannot be overwritten on retry. The previous successful working
  copy and retained source history remain unchanged on failure.

## Acceptance obligations

Use disposable databases and source copies only. Required checks include multi-source validation
failure, same-name different origins, A→B→A adoption, stale and unrelated dependencies, valid
applied-result coverage, pending outcomes, duplicate/overlapping targets, table-index movement,
LLCR/Appendix A coexistence, database gaps, cross-day recovery and duplicate requests.

Exercise actual API and Report UI paths, download the single assembled copy, and inspect its values,
lineage and unchanged sources. Render representative report copies in Microsoft Word and review
their pages; automated XML checks alone are not visual acceptance. Final test counts, browser and
Word evidence are recorded only after the reviewed implementation is stable.

Not included: new IR/DWV or qualitative adapters, multi-stage LLCR redesign, automatic photo
classification, cross-project result acceptance, automatic formal release, real-folder rebuilding,
or GitHub publication. Missing categories remain visible coverage gaps.

## Acceptance evidence

- Focused implementation checks cover source adoption, Matrix coverage, exact preview, overlap,
  LLCR coexistence, persisted output recovery and replay. The complete final matrix is run only
  after the reviewed code and tests are frozen.
- Browser acceptance uses a disposable server/database on ports 8797/5187, not the live development
  project. Pending LLCR and CR inputs are synthetic and cannot establish an engineering Pass.
- Native Word acceptance uses isolated Cable 031 and Soft Busbar 032 copies under
  `D:/PythonProject/connlab/tmp/report_batch_visual_20261107/acceptance_v2/`. Both assembled documents
  contain 20 pages (19-page baseline plus the newly selected CR appendix). All 40 pages were
  visually inspected; the Cable heading reflow finding was fixed and its affected pages rechecked.
  This is layout acceptance, not approval of historic or synthetic test values.
- Original reference hashes and all untouched package parts (58 for Cable, 55 for Soft Busbar)
  match. Real reports, project materials and templates were not written. A separate actual browser
  download is also rendered in Word before final delivery.
