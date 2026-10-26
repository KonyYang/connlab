# Report Workspace: evidence-based report updates

Status: five software paths implemented; final acceptance and integration are tracked by the active
task board and exact-subject review/QA evidence. Historical checkpoints below are not final approval.
Task: `TASK_REPORT_CAPABILITIES_3_7_20261026` (one main task, five milestones).

## Baseline and authority

The starting code is `cd6250e189e5ad67f4c005a3f32c3cfc92945884`. The existing local-update fidelity
and LLCR absolute/delta work remains the baseline, not work to repeat. Existing LLCR datasets,
report revisions, publication locks, source fingerprints and local-update protections stay intact.

The product gains deterministic report capabilities, not an AI report generator or a new workflow
engine. Confirmed Matrix remains the test-map authority. External approved documents and project
evidence remain read-only inputs. No historical Pass, unusual acceptance rationale, dates, instrument
calibration or cross-project reuse decision becomes a default for another project.

Development and all verification use an isolated worktree, database and copied or synthetic files.
New authoring operations create independent draft copies; they do not implicitly take the existing
`official` update/publication branch. Final publication and task Close are separate user decisions.

## Milestones and acceptance

### 3. Durable sources and confirmed mappings

- Retain immutable uploaded source identity and bytes, report provenance and project-specific mapping
  decisions beyond the working-draft cache's 24-hour retention period.
- Distinguish a current-project report from a cross-project layout reference. A reference is not
  evidence for the new project's numerical values, result outcomes or acceptance decisions.
- An existing approved report or compatible DOCX template must be usable as the starting draft,
  not merely shown as a reference. Keep its approved structure, reusable narrative and formatting;
  replace project-specific fields through confirmed mappings. Keep the existing fresh-generation
  entry as an alternative, not a mandatory precursor. Never weaken same-project source validation
  to admit a different project's report: reference-based drafting is an explicit copy-only action.
- Present inherited project identities, specification/version/date fields, result values/outcomes,
  photographs and special acceptance text as fields/regions to replace or review. Do not erase
  reusable Purpose/Conclusions sentence structure merely because some embedded facts change.
  Unresolved inherited facts prevent a clean delivery result, not independent drafting work.
- Associate a mapping with its source revision/hash, Matrix identity, Group/Step, source sheet/cells,
  sample identity and confirmation context. Unresolved or conflicting entries remain pending.
- Use revision/CAS checks to reject stale changes. Source or Matrix changes invalidate affected
  decisions without discarding unrelated work. Reloading the page or restarting the process retains
  confirmed facts. Project IDs isolate every read, change and download.
- Preserve old LLCR deserialization: it currently assumes an LLCR payload, so heterogeneous records
  cannot be inserted into that path without an explicit compatible typed implementation.

### 4. Temperature-rise and contact-resistance results

- Reuse existing temperature preparation and calculation modules. Keep measured and fitted values,
  Max and Avg of Max, actual current and CR absolute/delta quantities distinct.
- Preview source-backed values before updating the relevant result region and full measurement
  table/curve in a draft. Do not infer a Pass from an old report or an unconfirmed requirement.
- Verify calculations with independent numerical examples and trace each reported value to its
  confirmed source/selection. Keep all unrelated document regions unchanged.
- Result text can change height and reflow downstream pages. In newly generated result copies only,
  recognized Group headings are kept with their adjacent result table header and first data row.
  This bounded pagination safeguard may alter those non-target pagination properties, but not their
  text, fonts, images, global styles or later data rows. Preserve existing explicit page breaks; do
  not claim byte-identical pagination properties or fixed page counts after content-length changes.

### 5. Mechanical summary and appendices

- Import Mechanical Force Summary workbooks through explicit, retained column/sample mappings;
  keep sample SN distinct from instrument record ID and retain sample colour and units.
- Distinguish mating/withdrawal/retention, peak force and timed hold results. A six-second hold
  cannot be substituted by a peak. Derive appendix labels from confirmed measurement meaning.
- Keep PDFs as supporting evidence; this task does not require a universal instrument-PDF parser.
- Mixed-colour data must not retain a single-colour inherited heading. Updating results and the
  corresponding appendix must agree and must preserve other content and layout.

### 6. Approved-layout photo slots

- Show identifiable existing slots and captions; replace the selected slot, not every occurrence
  of a shared media relationship. Preserve dimensions, crop, anchor, caption, pagination and
  independent arrow objects. Do not insert all discovered photographs automatically.
- Unsupported or ambiguous compound drawings remain explicitly unresolved instead of being
  flattened, moved or silently reflowed. Repeated identical replacements are no-ops.

### 7. Customer copy and delivery checks

- Extend the existing customer conversion/download path rather than create another publication
  system. Generate independent copies and retain required temperature tables and curves.
- Do not label metal or unknown housings as resin. Use explicit supported material rules and show
  unresolved classifications. Check the generated package, not merely the pre-save document model.
- Cover body, headers/footers, comments/revisions, properties and embedded content as applicable.
  Uninspectable content cannot receive an unconditional clean/pass result. Report concrete issues.
- A successful conversion is not formal issuance or proof that engineering outcomes are accepted.

## Reference regressions

The latest review in reference thread `01a173db-15c6-7dd2-9f4c-481fee2b1823` found:

1. GS-12-2181 Rev.2's revision-history date was 2026-06-18, not the 2025-12-18 authorization date
   in a page header. Record the source location and date role; do not infer revision dates from headers.
2. Appendix B's inherited `Orange` heading covered Orange and Black samples.
3. Appendix C's inherited `Mating` label described Retention Force data.

These are regression scenarios, not instructions to edit the actual 032 reports. Project-specific
MFG corrosion acceptance, qualitative Pass decisions and 032B reuse approval are not general rules.

## Verification and delivery

Developer feedback tests cover public behavior using isolated storage. Independent review examines
the exact implementation against this task and repository standards. Independent QA runs the final
risk-proportionate matrix once on the reviewed subject; later changes rerun affected checks.

Required evidence before completion:

- Persistence across sessions/cache expiry, backward compatibility, CAS and project isolation.
- Real Report Workspace/API upload, mapping, confirmation, preview, copy generation and download.
- Numerical and semantic checks, pending-decision behavior and the three reference regressions.
- DOCX non-target preservation, photo relationship/crop/anchor checks and customer-copy audits.
- Browser checks on an isolated backend and Word-rendered representative copies with page-by-page
  visual inspection. A file opening successfully is not sufficient evidence of layout fidelity.
- Hash checks proving authoritative source reports/templates/project files were not modified.

Exact-subject completion evidence is retained in the task's review/QA records. Unverified milestones
remain open; green narrow tests must not be reported as proof of the entire five-milestone objective.

### User path and supported boundary

In Report Workspace, open **Prepare report from an approved source**, retain either this project's
original or an explicitly selected approved layout reference, then choose **Use as report base**.
The existing fresh-report generation remains available. This path supports the existing E-3707
report structure, not an arbitrary Word-template layout language. Blank project-number templates
require confirmed identity replacement before customer delivery checks can pass.

Retain measurement workbooks and photos, confirm their source/column/Group/Step mappings, preview
the intended changes and produce a new working copy. Confirmed facts and source identities survive
reloads. Customer conversion produces a review copy with explicit outstanding disclosure/content
checks; it does not approve the engineering outcome or issue the report. Original inputs are never
overwritten by these authoring actions.

### Implementation checkpoint (not final acceptance)

The five paths now have initial application/API/UI implementations. They remain under independent
review; no production report has been changed and no final QA or integration claim is made.

- Photo adapter: 11 isolated tests; shared-image occurrences, crop/rotation decisions, EXIF no-op,
  tracked moved/deleted pictures and non-target package preservation are covered.
- Customer package inspection: 9 isolated tests. XML text, revisions, comments, external fields
  (including simple fields), external relationships and inactive media are inspected. Thumbnails,
  HTML/RTF alternate content and other opaque parts require an explicit exact-byte review. Such a
  review cannot approve executable Office content. Unknown housing material is preserved, not
  relabeled as resin and not thereby approved for disclosure (46 existing gateway tests passed).
- Temperature chart: 3 isolated tests, including negative measured baselines and OOXML mutually
  exclusive fills. Measured points and fitted curves have separate series; the embedded workbook
  retains actual currents and labels a synthetic origin as not measured. Domain formulas are reused.
- Actual Microsoft Word rendered the synthetic updated chart successfully after fixing a simultaneous
  `noFill`/`solidFill` incompatibility that unit package checks initially missed. The inspected PDF
  shows all four legend entries, matching marker/curve colors and intact non-target text/header.
  This is adapter-level evidence, not complete Report Workspace end-to-end visual acceptance.

Local isolated evidence is under `C:/Users/White/Documents/Codex/report_goal_20261026/`:
`reference_manifest.json`, `renders/baseline021.json`, `renders/baseline031.json`, and
`renders/temperature-chart-layout.{json,pdf,png}`. The Word JSON records renderer, output hashes,
read-only input hashes and the separately identified process. Authoritative originals are only read;
baseline copies are unchanged. Do not commit confidential reference copies or rendered reports.

Remaining gates: final exact-diff review and fixes; independent QA on a stable reviewed subject;
isolated browser/API user flows; page-by-page Word inspection of integrated representative updates
and customer copies; source-hash recheck and serial integration. Unknown business outcomes must
remain pending rather than inherit an old Pass.

Further representative Word checks found and fixed a product issue: the 031 reference has its
existing temperature measurement table, curve and derived-current conclusion inside Group C, not
an Appendix. Merely adding a new Appendix leaves contradictory old evidence in the body and then
in the customer conversion. Acceptance requires an explicit, SHA-bound selection/replacement of
that existing evidence region, preserving the adjacent setup photo/caption and next Group. Generic
content review must not waive this contradiction. The selected original table, curve and obsolete
derived-current conclusion are now replaced together. Partial and cross-Group selections are rejected;
only exclusively orphaned resources from that region are removed, shared resources remain.

The 021 single-photo replacement was rendered through Word: 19 pages before and after, only page 2
changed, and the other 18 rendered pages are pixel-identical. Page 2 visually retains the other photo,
Mated/Unmated annotation objects, caption and layout. Evidence: local
`renders/photo021-visual-acceptance.json`. The real E-4515 converter also generated and rendered a
031 customer copy from isolated inputs with unchanged source/template hashes.

The explicit 031 region candidate rendered to 19 pages: only result page 10 and evidence page 11
changed; the other 17 pages were pixel-identical. The adjacent setup photo/Figure 14, Group D and
all other body blocks were unchanged; the obsolete 496.9 A conclusion disappeared. Evidence:
`renders/temperature031-region-acceptance.json`. This candidate predates the result-copy
pagination protection described above and is not evidence that every future update keeps 17 pages
identical.

The real E-4515 customer conversion produced one complete measured-temperature region, not a
duplicate appendix, and no obsolete 496.9 A conclusion. Its 17 pages were inspected after the
customer-copy pagination safeguard: Group headings/table starts stay together, table/curve is intact.
Evidence: `renders/customer031-pagination-acceptance.json`. These are synthetic QA results, not
approved engineering outcomes or customer release authorization.

Reference-based drafting additionally checks blank project-number templates and Word-split project
identifiers. A compatible E-3707 layout reference may have no old DL; it must not insert the current
DL into arbitrary text. Identity placeholders are updated through confirmed mappings, and missing
identity remains unresolved. Same-project originals retain their strict project identity check.

Final adapter visual candidates (before independent software QA):

- `temperature031-final`: 19 pages; pixel-identical to the inspected region-replacement candidate
  after the bounded pagination safeguard was added.
- `mechanical-cr031-final`: 20 pages; a mixed Orange/Black six-second retention hold replaces the
  selected Appendix C and result, and absolute CR with actual current/voltage goes into Appendix D.
  All pages were inspected; the shortened result's downstream orphan Group B heading was fixed.
  Pending outcomes leave the target Pass blank. Other tests' results are deliberately untouched.
- `customer031-final`: 17 pages; pixel-identical to the inspected customer pagination candidate.
  New temperature table and native editable chart occur once. Source/template hash checks passed.

These files and their hash/renderer JSON are task-local under `visual_candidates/` and `renders/`.
They contain synthetic data and are not deliverable project reports. The retained raw reference
files, source spreadsheets and actual project documents have not been edited.
