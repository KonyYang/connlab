# Project folder creation and whole-folder rebuild

The single Create project folder entry performs read-only package preflight. Directory
readiness is separate from file readiness. A new folder's Application Form remains
waiting until its archived target and provenance can be checked. Preflight is a
point-in-time assessment, not a guarantee against later file locks or input changes.
Unreadable generated files are reported as blocked individually while other file
results remain visible. If the target-tree fingerprint cannot be verified, preflight
returns a start blocker rather than permitting generation with incomplete safety facts.
Existing output byte differences do not block an explicitly selected whole-folder
rebuild. Current inputs, templates, ownership and the reviewed target-tree identity
still must be valid. Resume retains the existing publication-recovery order; after recovery,
required-form conflicts report their actual file reasons rather than a generic stage error.
For multiple outputs of one kind, readiness uses the latest record at the exact target
path; a newer record at another location must not hide that target's provenance.
No historical record is adopted without the existing byte and input-signature checks.

## Output dependencies

| Output | Reuse inputs |
| --- | --- |
| Test Record | Confirmed Matrix identity/revision, Basic Information, resolved document header inputs, template path and SHA-256 |
| Test Status | Confirmed Matrix identity/revision and workbook layout version |
| Fee Form | Confirmed Matrix/Fee/pricing, Basic Information, Fee template/output identity |
| Customer Feedback | Basic Information, confirmed Schedule, template path and SHA-256 |
| Application Form write-back | Selected archived source identity, form data, Basic Information and confirmed Schedule (existing signature) |

Reuse also requires the recorded output identity and matching file bytes. Missing,
untracked or externally modified targets retain existing conflict protections.
Legacy shared Fee signatures cannot prove Test Record/Customer Feedback freshness;
these files may require one controlled update to establish their per-file signature.

## Deliberate batch boundary

The User's September 13 simplification supersedes incremental Create/Update behavior:

- No existing directory: create normally.
- Existing directory: preserve history and rebuild, or delete and rebuild.
- Delete requires a second explicit confirmation, bound to the current preview.
- History is the original folder name plus a space and its original local modification
  timestamp (`yyyyMMddHHmmss`); collisions append `-1`, `-2`, etc.
- There is no new user-facing continue-existing choice. Legacy journal recovery remains
  compatible; interrupted new rebuilds resume their already confirmed operation.
- Old outputs are not reused during whole-folder rebuilding. Per-file signatures above
  remain relevant to standalone generation and publication recovery.
- Inputs within the folder being replaced must first have an independent source copy.
- Overwrite keeps the old folder in operation-private rollback storage until the new
  package completes, then removes it after identity checks. Failed finalization must
  resume, not abandon that pending cleanup. Legacy journals never gain delete authority.
- One status surface shows progress/results/errors with collapsible diagnostics.
  Advanced actions and a permanent readiness panel are not separate UI surfaces.

Per-file readiness no longer hides independent files behind a missing Fee or another
file's template. The operation remains the existing fail-stop execution chain:
preflight does not add partial completion, continue-after-failure or single-item
retry. Existing operation fingerprint checks, recovery journal, deduplication,
explicit rebuild confirmation and protected publication are unchanged.

Validation uses isolated repositories, temporary folders and fake Office adapters.
Real Office/file-lock behavior and packaged deployment require separate acceptance;
no real project folder is rebuilt by this maintenance task.
