# Project folder preflight and reuse (Phase 1)

The existing Create/Update entry exposes read-only package preflight. Directory
readiness is separate from file readiness. A new folder's Application Form remains
waiting until its archived target and provenance can be checked. Preflight is a
point-in-time assessment, not a guarantee against later file locks or input changes.
Unreadable generated files are reported as blocked individually while other file
results remain visible. If the target-tree fingerprint cannot be verified, preflight
returns a start blocker rather than permitting generation with incomplete safety facts.
File conflicts are also exposed before a new operation starts, with file labels and
reasons. Resume retains the existing publication-recovery order; after recovery,
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

Per-file readiness no longer hides independent files behind a missing Fee or another
file's template. The operation remains the existing fail-stop execution chain:
preflight does not add partial completion, continue-after-failure or single-item
retry. Existing operation fingerprint checks, recovery journal, deduplication,
explicit rebuild confirmation and protected publication are unchanged.

Validation uses isolated repositories, temporary folders and fake Office adapters.
Real Office/file-lock behavior and packaged deployment require separate acceptance;
no real project folder is rebuilt by this maintenance task.
