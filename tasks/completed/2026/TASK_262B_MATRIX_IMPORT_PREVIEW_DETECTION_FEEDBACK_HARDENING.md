# TASK_262B - Matrix Import Preview Detection Feedback Hardening

## Status

Complete.

## Scope

Harden Matrix import preview detection so non-Matrix tables do not reuse stale preview state or get reported as valid Matrix candidates.

## Goals

- Treat automatic parse failure as a red, non-blocking operator warning.
- Respect user-specified page/table targeting.
- Reject document revision/history tables even when their description cells mention `test group` or `sample qty`.
- Preserve support for real Matrix tables whose group headers are numeric, letters, or alphanumeric tokens.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task because the implementation is a bounded parser hardening and regression-test update with no broad architecture redesign, no new dependencies, and no multi-module workflow expansion.

## Non-Goals

- No Test Record generation changes.
- No Matrix Library changes.
- No equipment, fee, report, or execution persistence changes.
- No UI polish beyond the already approved import-preview feedback behavior.

## Completion Notes

- Parser now excludes revision/history tables before Matrix scoring.
- Matrix likelihood scoring penalizes numeric-only first-column row content, reducing false positives from record tables.
- Added regression coverage for revision-record tables that mention test words.
