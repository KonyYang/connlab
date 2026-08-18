# TASK_283B_CONN_LAB_METHOD_TEMPLATE_LIBRARY

## Status

Complete (2026-05-31).

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Objective

Create a ConnLab-owned deterministic Method Template Library that replaces the old external `template_data.py` concept with maintainable, tested project data.

The library should help format and fill common Method/Condition/Requirement rows when specification section extraction is partial, especially for stable laboratory conventions such as Visual Examination, LLCR, Durability, MFG, Vibration, and Shock.

This task is fallback-only. It must never become a second authority source that overrides confident section extraction.

## Business Context

Current operator workflow expects Matrix import to prefill row-level Method/Condition/Requirement as much as possible, then allow human review/correction before `Confirm Matrix`.

`TASK_283A` improved section-driven extraction quality. `TASK_283B` adds deterministic template fallback and formatting support for known stable families so manual editing load is reduced without introducing AI or hidden heuristics.

## Scope

### In Scope

1. Define a small internal template data shape for:
   - canonical test item family.
   - aliases.
   - optional default method.
   - condition template.
   - requirement template.
   - source/provenance notes.
2. Port only approved content from the reference `template_data.py` into ConnLab test-covered data.
3. Use templates as fallback/formatting support only.
4. Preserve specification-section extraction as the primary source.
5. Add unit tests for alias matching, fallback behavior, and non-override guard behavior.
6. Keep row-level `method` / `condition` / `requirement` distinct from existing step-level summary fields.
7. Keep parser and extractor modules under AGENTS line-count limits.

### Out Of Scope

- No UI for editing templates.
- No historical Test Report import.
- No AI or fuzzy semantic learning.
- No report generation expansion.
- No StepInstance or execution persistence.

## Acceptance Criteria

1. Template alias matching is deterministic and tested.
2. Templates do not override confidently extracted specification values.
3. Templates can fill stable fallback values only when the task plan explicitly allows that field/test family.
4. Matrix Editor still presents all values as editable and user-confirmed.
5. Existing TASK_283A extraction behavior remains intact.
6. No AI/LLM inference is introduced; only deterministic rules and curated template data are used.
7. No frontend architecture expansion is introduced in this task.

## Delivery Boundaries

1. Backend-only implementation slice:
   - `backend/modules/test_plan/*` deterministic parser/extractor/template logic.
   - Tests under `tests/unit/*` and any strictly required integration smoke updates.
2. Do not add new database tables unless explicitly required by approved plan; prefer in-repo static template data for this task.
3. If a required parser update risks line-limit violations, split helpers into support modules instead of growing one file.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for execution because the task is a bounded data-shape and deterministic matching implementation with tests.

## Stop Rule

Create a separate implementation plan before coding.
