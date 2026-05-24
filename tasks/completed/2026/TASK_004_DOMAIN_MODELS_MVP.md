# TASK 004 — MVP Domain Models

## Goal

Implement pure domain models and enums for the MVP.

## Scope

Create domain classes only. No database, API, or Office parsing.

## Required Models

- Project
- ApplicationForm
- SampleInfo
- PrecheckResult
- PrecheckIssue
- LtrRecord
- ProjectFolderRecord
- FileAsset

## Required Enums

- ProjectStatus
- PrecheckStatus
- IssueLevel
- IssueCategory
- LtrStatus
- FileAssetType

## Rules

- Domain layer must be pure Python.
- Use dataclasses or Pydantic models, but do not depend on SQLAlchemy.
- Add simple invariant methods where useful, e.g. `Project.can_generate_folder()`.

## Tests

- Test enum values.
- Test basic domain construction.
- Test project status transition helper if implemented.

## Acceptance Criteria

- Domain models import without infrastructure dependencies.
- Tests pass.
