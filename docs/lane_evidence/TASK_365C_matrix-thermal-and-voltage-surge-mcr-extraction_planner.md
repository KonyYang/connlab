# TASK_365C Matrix Thermal And Voltage Surge MCR Extraction Planner Evidence

Status: planned_only_queued
Date: 2026-07-19
Role: Planner

## Discovery Decision

The user confirmed three bounded Matrix parser outcomes: Thermal Shock
cycle/dwell duration with 25 hourly Units, empty-only `No damage` defaults for
Thermal Shock and Temperature life, and label-bound Voltage surge Condition
facts. Repository probes confirmed the current missing behavior and proved the
existing Thermal Shock Fee seed already owns the correct `30/hour` authority.

## Serialization

TASK_365B remains the board's current active review lane. TASK_365A and TASK_364B
also await their separate review/acceptance gates. TASK_365C shares the Matrix
extractor with TASK_365A and must remain queued until TASK_365A/B parser hunks
are isolated. No Developer routing is legal from this evidence.

## Scope

TASK_365C is parser/MCR plus focused compatibility tests only. Fee prices/seeds,
frontend/API, persistence/schema, authority lifecycle, existing confirmed data,
real files/databases, TASK_363C/D, TASK_364B, TASK_365A/B behavior, and unrelated
dirty-worktree content are locked.

## Next Gate

Reviewer plan gate after current parser-lane disposition. Product implementation
requires a separate explicit user approval and must not start from this
planned-only evidence.
