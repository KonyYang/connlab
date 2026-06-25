# TASK_334H_LTR_WORKBOOK_LOOKUP_PERFORMANCE_OPTIMIZATION

Status: Completed
Created: 2026-06-25
Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Depends on: TASK_334F_LTR_WORKBOOK_READONLY_OPEN_AT_EXACT_DL_MATCH, TASK_333C_LTR_WORKBOOK_ON_DEMAND_PREVIEW_AND_EXACT_DL_MATCH
Plan: ../docs/TASK_334H_LTR_WORKBOOK_LOOKUP_PERFORMANCE_OPTIMIZATION_PLAN.md

## User Request

Optimize the LTR workbook lookup/open flow in three gradual tiers because the current search is slow.

## Problem

The Workbench LTR update preview and read-only workbook open paths still pay avoidable Excel COM cost:

- The exact DL lookup can read the full annual `A:Q` row range before the target row is known.
- The read-only open action can repeat heavier preview-oriented work when it only needs the exact DL row location.
- Repeated operations for the same unchanged workbook and DL number can rescan workbook content.

## Goal

Make LTR workbook preview/open lookup faster while preserving all safety requirements from the existing LTR sync and read-only open tasks.

## Scope

Implement the optimization in three reviewable tiers:

1. Tier 1: locate the exact DL row by scanning only the DL column, then read only the target row values needed for preview.
2. Tier 2: make read-only open reuse the lightweight exact-DL locator path instead of rebuilding a full preview.
3. Tier 3: add a guarded row-locator cache for repeated operations against an unchanged workbook, with exact-cell validation before use.

## Out Of Scope

- No LTR workbook append/new-registration behavior changes.
- No Basic Information schema, editor, or persistence changes.
- No LTR write-column mapping changes.
- No Report generation.
- No StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.
- No broad Project Workbench UI redesign.

## Safety Requirements

- DL matching must remain exact. `DL-2026-05-011` must not match `DL-2026-05-011A`.
- Duplicate exact DL rows must continue to block preview/update/open.
- Preview must remain read-only and must not save, back up, append, or mutate the workbook.
- Commit must continue to revalidate the preview target before writing.
- Read-only open must continue to open the workbook read-only, clear filters/unhide rows and columns for viewing, and select the exact DL cell.
- Cached row locations, if implemented, must be invalidated by workbook file signature changes and must still validate the target DL cell before use.
- Cached row locations may only be trusted when they come from a completed exact-DL uniqueness scan for the same workbook signature. Duplicate exact DL rows must still block preview/update/open; cache use must not degrade duplicate detection into a single-cell check.

## Acceptance Criteria

- LTR preview no longer reads full `A:Q` workbook data to find the DL row.
- LTR preview reads only the DL column for lookup and only the exact target row for comparison values.
- Read-only open resolves the exact DL row through the fast locator path.
- Duplicate exact DL rows and missing exact DL rows are still reported correctly.
- A prefix-only row such as `DL-2026-05-011A` does not satisfy a lookup for `DL-2026-05-011`.
- No-op update protection remains intact.
- Performance validation records objective evidence that the slow path was removed, such as fake-gateway call assertions proving preview does not request full `A:Q` data plus a manual or service-level timing note for preview/open before and after the change.
- Existing LTR sync and read-only open tests pass, with new tests covering the faster lookup behavior.

## Approval Gate

Implementation was explicitly approved and completed on 2026-06-25.

## Completion Notes

- LTR workbook preview locates the exact DL row by reading only the DL column and then reads only the matched `A:Q` target row for comparison values.
- Read-only workbook open resolves the exact DL row through the same lightweight locator instead of rebuilding full preview data.
- Repeated unchanged workbook/DL lookups use a guarded workbook-signature cache only after a completed exact-DL uniqueness scan, with exact D-cell validation before each cache hit is trusted.
- Duplicate exact DL rows and missing exact DL rows still block the flow; prefix rows such as `DL-2026-05-011A` do not match `DL-2026-05-011`.
- No-op update protection remains intact.

## Validation

- `py -m pytest tests\unit\test_ltr_workbook_basic_information_sync_service.py tests\unit\test_excel_com_ltr_workbook_gateway.py tests\unit\test_ltr_workbook_readonly_open_gateway.py` (`35 passed`)
