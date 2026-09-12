# Project Folder single entry

2026-09-12. Scope: operator entry points, not a generation-engine rewrite.

## Behavior

- Create/Update project folder is the normal entry. It reads the latest operation and a fresh preview.
- A confirmed existing workspace defaults to continue_existing; existence alone is not ownership proof.
- An unchanged interrupted operation resumes. Changed inputs require the existing can_restart guard;
  otherwise publication must be reconciled first. Backend write guards remain authoritative.
- A pending destructive rebuild is not silently resumed by a normal update. A safely replaceable
  operation may become a fresh non-destructive update; otherwise explicit continuation is required.
- Unknown/existing-folder conflicts still require a reviewed choice. Advanced folder actions exposes
  rebuilding, and the dialog keeps backup/overwrite behind Advanced rebuild options.
- Confirmation binds the operation identity and preview token. Stale confirmation makes no write.
- Resume generation, Start new generation and Refresh generation preview are no longer separate UI
  commands. Error causes and diagnostic references remain visible.

## Implementation and safety

The existing generation preview adds read-only recovery facts: operation identity, input equality and
whether a previous rebuild still has unfinished workspace work. These facts do not authorize a write;
the existing start/resume endpoints revalidate identity, context, locks and publication ownership.
No journal format, database migration, publication algorithm, or overwrite policy changes.

The typed frontend hook owns routing and duplicate-click prevention. The model forwards it; the
layout displays results and reviewed choices. Existing legacy hook calls remain compatible with other
callers. Preview failure and project navigation cannot cause an old or unreviewed write.

## Acceptance

1. A managed existing folder updates without a routine three-option prompt.
2. New/unchanged/changed/interrupted input cases use the correct existing endpoint.
3. Uncheckpointed publication cannot be replaced; destructive continuation requires confirmation.
4. Advanced rebuild selection is explicit; cancellation has no write side effect.
5. Stale previews, operation drift, duplicate clicks and project switching do not cause extra writes.
6. Existing recovery regression tests remain passing; browser verification does not generate or
   rebuild real operator project files.

This change does not implement per-file partial completion or selective retry. Those remain separate
generation-chain work and must not be inferred from the unified button.
