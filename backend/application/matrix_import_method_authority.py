"""Pure Method authority resolution for Import Matrix Replace."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from datetime import UTC, datetime
import json
from typing import Callable, Protocol

from backend.application.external_excel_read_service import StandardRecordReadResult
from backend.application.external_resource_service import effective_standard_worksheet_name
from backend.application.source_matrix_import_builder import (
    canonical_json,
    canonical_windows_path,
    fingerprint,
    fingerprint_source_rows,
    fingerprint_source_snapshot,
)
from backend.domain import (
    ExternalResource,
    ExternalResourceType,
    ProjectMatrixDraftSnapshot,
    SourceMatrixImportRecord,
    SourceMatrixSnapshot,
)
from backend.modules.test_plan.standard_method_version_parser import (
    build_method_proposal,
    parse_catalog_method,
    parse_matrix_method,
)


class MatrixImportMethodAuthorityError(ValueError):
    """Raised when the Standard authority cannot safely resolve import Methods."""


class MatrixImportMethodAuthorityConflictError(MatrixImportMethodAuthorityError):
    """Raised when persisted import authority no longer matches current facts."""


class ResourceStore(Protocol):
    def get_by_type(self, resource_type: ExternalResourceType) -> ExternalResource | None: ...


class CatalogReader(Protocol):
    def read_standard_records(self) -> StandardRecordReadResult: ...


class CachedStandardResourceStore:
    """Keep one request-scoped Standard resource fact for reader and resolver."""

    def __init__(self, delegate: ResourceStore) -> None:
        self._delegate = delegate
        self._loaded = False
        self._resource: ExternalResource | None = None

    def get_by_type(self, resource_type: ExternalResourceType) -> ExternalResource | None:
        if resource_type is not ExternalResourceType.STANDARD_RECORD_EXCEL:
            return self._delegate.get_by_type(resource_type)
        if not self._loaded:
            self._resource = self._delegate.get_by_type(resource_type)
            self._loaded = True
        return self._resource


@dataclass(frozen=True, slots=True)
class MatrixImportMethodAuthorityRow:
    stable_source_row_key: str
    row_order: int
    test_item: str
    current_method: str | None
    status: str
    resulting_method: str | None
    matched_standard_code: str | None
    source_row_number: int | None
    reason: str | None
    applied: bool


@dataclass(frozen=True, slots=True)
class MatrixImportMethodAuthoritySummary:
    status: str
    updated_count: int
    current_count: int
    review_count: int
    standard_resource_id: str
    effective_worksheet_name: str
    catalog_fingerprint: str
    context_fingerprint: str
    rows: tuple[MatrixImportMethodAuthorityRow, ...]


@dataclass(frozen=True, slots=True)
class MatrixImportMethodAuthorityResult:
    draft: ProjectMatrixDraftSnapshot
    summary: MatrixImportMethodAuthoritySummary
    context_json: str


class MatrixImportMethodAuthorityResolver:
    """Read one Standard catalog and resolve an imported draft without persistence."""

    def __init__(
        self,
        *,
        resource_store: ResourceStore,
        catalog_reader: CatalogReader,
        now: Callable[[], str] | None = None,
    ) -> None:
        self._resources = resource_store
        self._catalog = catalog_reader
        self._now = now or (lambda: datetime.now(UTC).isoformat())

    def resolve(
        self,
        *,
        draft: ProjectMatrixDraftSnapshot,
        source_snapshot: SourceMatrixSnapshot,
        project_id: str,
        source_import_id: str,
        source_snapshot_id: str,
        task261_commit_fingerprint: str,
        source_locator_fingerprint: str,
        payload_fingerprint: str,
        selected_group_fingerprint: str,
        source_root_fingerprint: str,
        source_row_fingerprint: str,
    ) -> MatrixImportMethodAuthorityResult:
        resource = self._load_resource()
        worksheet = effective_standard_worksheet_name(resource) or "认可标准"
        try:
            catalog = self._catalog.read_standard_records()
        except Exception as exc:
            raise MatrixImportMethodAuthorityError(
                f"Standard record catalog could not be read: {exc}"
            ) from exc
        resource_path = canonical_windows_path(str(resource.path))
        returned_path = canonical_windows_path(catalog.resource_path)
        if returned_path != resource_path:
            raise MatrixImportMethodAuthorityError(
                "Standard record catalog path does not match the configured resource path."
            )
        if catalog.matched_sheets != (worksheet,):
            raise MatrixImportMethodAuthorityError(
                "Standard record catalog worksheet does not match the configured worksheet."
            )
        candidates = tuple(
            parse_catalog_method(row.standard_code, source_row_number=row.source_row_number)
            for row in catalog.rows
        )
        decisions, transformed = _resolve_rows(draft, source_snapshot, candidates)
        catalog_fingerprint = fingerprint(
            {
                "source": [resource.resource_id, resource_path, worksheet],
                "rows": [
                    [
                        row.source_row_number,
                        row.standard_code,
                        row.test_item,
                        row.sample_description,
                        row.source_sheet,
                    ]
                    for row in catalog.rows
                ],
            }
        )
        pre_method_fingerprint = fingerprint_draft_methods(draft, source_snapshot)
        post_method_fingerprint = fingerprint_draft_methods(transformed, source_snapshot)
        proposal_fingerprint = fingerprint([_row_identity(row) for row in decisions])
        result_fingerprint = fingerprint_draft_snapshot(transformed, source_snapshot)
        context = {
            "schema": "matrix-import-method-sync:v1",
            "mode": "replace_import",
            "project_id": project_id,
            "source_import_id": source_import_id,
            "source_snapshot_id": source_snapshot_id,
            "project_matrix_draft_id": transformed.record.project_matrix_draft_id,
            "task261_commit_fingerprint": task261_commit_fingerprint,
            "source_locator_fingerprint": source_locator_fingerprint,
            "payload_fingerprint": payload_fingerprint,
            "selected_group_fingerprint": selected_group_fingerprint,
            "source_root_fingerprint": source_root_fingerprint,
            "source_row_fingerprint": source_row_fingerprint,
            "standard_resource_id": resource.resource_id,
            "standard_resource_path": resource_path,
            "effective_worksheet_name": worksheet,
            "matched_worksheet_name": worksheet,
            "catalog_fingerprint": catalog_fingerprint,
            "pre_method_fingerprint": pre_method_fingerprint,
            "proposal_fingerprint": proposal_fingerprint,
            "post_method_fingerprint": post_method_fingerprint,
            "result_fingerprint": result_fingerprint,
            "applied_at": self._now(),
            "row_results": [_row_context(row) for row in decisions],
        }
        context["context_identity_fingerprint"] = _context_identity(context)
        context_json = canonical_json(context)
        transformed = replace(
            transformed,
            record=replace(transformed.record, method_sync_context_json=context_json),
        )
        review_count = sum(not row.applied and row.status != "current" for row in decisions)
        return MatrixImportMethodAuthorityResult(
            draft=transformed,
            context_json=context_json,
            summary=MatrixImportMethodAuthoritySummary(
                status="review_required" if review_count else "synchronized",
                updated_count=sum(row.applied for row in decisions),
                current_count=sum(row.status == "current" for row in decisions),
                review_count=review_count,
                standard_resource_id=resource.resource_id,
                effective_worksheet_name=worksheet,
                catalog_fingerprint=catalog_fingerprint,
                context_fingerprint=context["context_identity_fingerprint"],
                rows=decisions,
            ),
        )

    def _load_resource(self) -> ExternalResource:
        resource = self._resources.get_by_type(ExternalResourceType.STANDARD_RECORD_EXCEL)
        if resource is None or not resource.active:
            raise MatrixImportMethodAuthorityError(
                "Active Standard record Excel resource is not configured."
            )
        return resource


def verify_reusable_method_authority(
    *,
    current: MatrixImportMethodAuthorityResult,
    existing_import: SourceMatrixImportRecord,
    existing_source: SourceMatrixSnapshot,
    existing_draft: ProjectMatrixDraftSnapshot,
) -> MatrixImportMethodAuthoritySummary:
    """Fail closed unless a persisted TASK_261 import exactly matches current authority."""
    raw = existing_draft.record.method_sync_context_json
    try:
        existing = json.loads(raw or "")
        current_context = json.loads(current.context_json)
    except (TypeError, json.JSONDecodeError) as exc:
        raise MatrixImportMethodAuthorityConflictError(
            "Existing Matrix import Method authority context is missing or malformed."
        ) from exc
    if not isinstance(existing, dict) or not isinstance(current_context, dict):
        raise MatrixImportMethodAuthorityConflictError(
            "Existing Matrix import Method authority context is invalid."
        )
    if existing.get("context_identity_fingerprint") != _context_identity(existing):
        raise MatrixImportMethodAuthorityConflictError(
            "Existing Matrix import Method authority context fingerprint is invalid."
        )
    stored_locator = fingerprint(
        {
            "path": canonical_windows_path(existing_import.source_document_path),
            "name": existing_import.source_document_name.strip(),
            "format": existing_import.source_format.strip().casefold(),
        }
    )
    stored_payload = existing_import.source_preview_payload
    stored_facts = {
        "task261_commit_fingerprint": existing_import.task261_commit_fingerprint,
        "source_locator_fingerprint": stored_locator,
        "payload_fingerprint": fingerprint(stored_payload) if stored_payload else None,
        "selected_group_fingerprint": fingerprint(
            list(existing_import.selected_group_keys_at_import)
        ),
    }
    if any(existing.get(key) != value for key, value in stored_facts.items()):
        raise MatrixImportMethodAuthorityConflictError(
            "Existing Source Matrix import facts diverge from Method authority context."
        )
    expected_ids = {
        "project_id": existing_draft.record.project_id,
        "source_import_id": existing_import.import_id,
        "source_snapshot_id": existing_source.snapshot_id,
        "project_matrix_draft_id": existing_draft.record.project_matrix_draft_id,
    }
    if any(existing.get(key) != value for key, value in expected_ids.items()):
        raise MatrixImportMethodAuthorityConflictError(
            "Existing Matrix import lineage does not match its Method authority context."
        )
    if (
        existing_source.import_id != existing_import.import_id
        or existing_source.project_id != existing_import.project_id
        or existing_draft.record.source_import_id != existing_import.import_id
        or existing_draft.record.source_snapshot_id != existing_source.snapshot_id
    ):
        raise MatrixImportMethodAuthorityConflictError(
            "Existing Source Matrix and editable draft lineage is inconsistent."
        )
    ignored = {*expected_ids, "context_identity_fingerprint", "applied_at"}
    if {
        key: value for key, value in existing.items() if key not in ignored
    } != {
        key: value for key, value in current_context.items() if key not in ignored
    }:
        raise MatrixImportMethodAuthorityConflictError(
            "Matrix import or Standard authority changed. Replace cannot reuse the prior import."
        )
    _verify_persisted_fingerprints(existing, existing_source, existing_draft)
    return replace(
        current.summary,
        context_fingerprint=str(existing["context_identity_fingerprint"]),
    )


def verify_new_method_authority(
    *,
    expected: MatrixImportMethodAuthorityResult,
    persisted_source: SourceMatrixSnapshot,
    persisted_draft: ProjectMatrixDraftSnapshot,
) -> None:
    """Read-verify one newly persisted source/draft aggregate before commit."""
    if persisted_draft.record.method_sync_context_json != expected.context_json:
        raise MatrixImportMethodAuthorityConflictError(
            "Persisted Matrix Method authority context could not be verified."
        )
    context = json.loads(expected.context_json)
    _verify_persisted_fingerprints(context, persisted_source, persisted_draft)


def fingerprint_draft_methods(
    draft: ProjectMatrixDraftSnapshot,
    source: SourceMatrixSnapshot,
) -> str:
    keys = _stable_keys_by_source_id(source)
    return fingerprint(
        [
            [keys.get(row.source_row_snapshot_id), row.row_order, row.method]
            for row in sorted(draft.rows, key=lambda item: item.row_order)
        ]
    )


def fingerprint_draft_snapshot(
    draft: ProjectMatrixDraftSnapshot,
    source: SourceMatrixSnapshot,
) -> str:
    source_rows = _stable_keys_by_source_id(source)
    groups = {group.draft_group_id: [group.group_order, group.group_key] for group in draft.groups}
    rows = {row.draft_row_id: [row.row_order, source_rows.get(row.source_row_snapshot_id)] for row in draft.rows}
    return fingerprint(
        {
            "groups": [
                [group.group_order, group.group_key, group.group_label, group.sample_quantity_expression, group.sample_note]
                for group in draft.groups
            ],
            "rows": [
                [row.row_order, source_rows.get(row.source_row_snapshot_id), row.test_item, row.source_section, row.method, row.condition, row.requirement]
                for row in draft.rows
            ],
            "cells": sorted(
                [rows[cell.draft_row_id], groups[cell.draft_group_id], cell.cell_value]
                for cell in draft.cells
            ),
        }
    )


def _resolve_rows(draft, source, candidates):
    source_by_id = {row.row_snapshot_id: row for row in source.rows}
    counts = Counter(row.source_row_index for row in source.rows if row.source_row_index is not None)
    decisions: list[MatrixImportMethodAuthorityRow] = []
    transformed_rows = []
    for row in sorted(draft.rows, key=lambda item: item.row_order):
        source_row = source_by_id.get(row.source_row_snapshot_id or "")
        stable_key = _stable_source_row_key(source_row, row.row_order)
        if source_row is None or source_row.source_row_index is None:
            status, proposal = "row_identity_missing", None
        elif counts[source_row.source_row_index] > 1:
            status, proposal = "row_identity_duplicate", None
        else:
            proposal = build_method_proposal(parse_matrix_method(row.method), candidates)
            status = proposal.status
        applied = status in {"update_available", "revision_missing"}
        resulting = proposal.proposed_method if applied and proposal else row.method
        decisions.append(
            MatrixImportMethodAuthorityRow(
                stable_source_row_key=stable_key,
                row_order=row.row_order,
                test_item=row.test_item,
                current_method=row.method,
                status=status,
                resulting_method=resulting,
                matched_standard_code=proposal.matched_standard_code if proposal else None,
                source_row_number=proposal.source_row_number if proposal else None,
                reason=proposal.reason if proposal else None,
                applied=applied,
            )
        )
        transformed_rows.append(replace(row, method=resulting))
    return tuple(decisions), replace(draft, rows=tuple(transformed_rows))


def _verify_persisted_fingerprints(context, source, draft) -> None:
    checks = {
        "source_root_fingerprint": fingerprint_source_snapshot(source),
        "source_row_fingerprint": fingerprint_source_rows(source),
        "post_method_fingerprint": fingerprint_draft_methods(draft, source),
        "result_fingerprint": fingerprint_draft_snapshot(draft, source),
    }
    if any(context.get(key) != value for key, value in checks.items()):
        raise MatrixImportMethodAuthorityConflictError(
            "Persisted Matrix import authority could not be read-verified."
        )


def _stable_keys_by_source_id(source: SourceMatrixSnapshot) -> dict[str, str]:
    return {
        row.row_snapshot_id: _stable_source_row_key(row, row.row_order)
        for row in source.rows
    }


def _stable_source_row_key(row, row_order: int) -> str:
    index = row.source_row_index if row is not None else None
    return f"source-row:v1:{index if index is not None else 'missing'}:{row_order}"


def _row_context(row: MatrixImportMethodAuthorityRow) -> dict[str, object]:
    return {
        "stable_source_row_key": row.stable_source_row_key,
        "row_order": row.row_order,
        "test_item": row.test_item,
        "current_method": row.current_method,
        "status": row.status,
        "resulting_method": row.resulting_method,
        "matched_standard_code": row.matched_standard_code,
        "source_row_number": row.source_row_number,
        "reason": row.reason,
        "applied": row.applied,
    }


def _row_identity(row: MatrixImportMethodAuthorityRow) -> list[object]:
    context = _row_context(row)
    return [context[key] for key in context]


def _context_identity(context: dict[str, object]) -> str:
    return fingerprint(
        {
            key: value
            for key, value in context.items()
            if key not in {"context_identity_fingerprint", "applied_at"}
        }
    )
