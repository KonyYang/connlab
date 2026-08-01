"""Pure Method authority resolution for Import Matrix Replace."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from datetime import UTC, datetime
import stat
from typing import Callable, Literal, Protocol

from backend.application.external_excel_read_service import StandardRecordReadResult
from backend.application.external_resource_service import effective_standard_worksheet_name
from backend.application.source_matrix_import_builder import (
    canonical_json,
    canonical_windows_path,
    fingerprint,
)
from backend.domain import (
    ExternalResource,
    ExternalResourceType,
    ProjectMatrixDraftSnapshot,
    SourceMatrixSnapshot,
)
from backend.modules.test_plan.standard_method_version_parser import (
    build_method_proposal,
    parse_catalog_method,
    parse_matrix_method,
)
from backend.infrastructure.office.excel_com_readonly_tabular_gateway import (
    LegacyExcelComUnavailableError,
)


StandardVersionUnavailableAction = Literal[
    "prompt_if_unavailable", "preserve_imported_methods"
]
STANDARD_VERSION_WARNING = (
    "Standard version file unavailable. Original Method values were kept. "
    "You can update them later in Standard Method versions."
)
_WINDOWS_AVAILABILITY_CODES = frozenset({2, 3, 5, 32, 53, 54, 55, 59, 64, 65, 67, 121, 1231})

class MatrixImportMethodAuthorityError(ValueError):
    """Raised when the Standard authority cannot safely resolve import Methods."""


class MatrixImportMethodAuthorityConflictError(MatrixImportMethodAuthorityError):
    """Raised when persisted import authority no longer matches current facts."""

class MatrixImportStandardVersionActionRequiredError(MatrixImportMethodAuthorityError):
    """Require an explicit operator choice for one proven availability state."""

    def __init__(self, reason_code: str) -> None:
        super().__init__("Standard version file unavailable.")
        self.reason_code = reason_code


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

    @property
    def requires_file_preflight(self) -> bool:
        """Tell the resolver that this production-backed store needs a file stat check."""
        return True

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
class MatrixImportMethodAuthorityWarning:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class MatrixImportMethodAuthoritySummary:
    status: str
    updated_count: int
    current_count: int
    review_count: int
    standard_resource_id: str | None
    effective_worksheet_name: str | None
    catalog_fingerprint: str | None
    context_fingerprint: str
    rows: tuple[MatrixImportMethodAuthorityRow, ...]
    warning: MatrixImportMethodAuthorityWarning | None = None


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
        standard_version_unavailable_action: StandardVersionUnavailableAction = (
            "prompt_if_unavailable"
        ),
    ) -> MatrixImportMethodAuthorityResult:
        resource, unavailable_reason = self._load_resource()
        if unavailable_reason:
            return _resolve_unavailable(
                action=standard_version_unavailable_action,
                reason_code=unavailable_reason,
                resource=resource,
                draft=draft,
                source_snapshot=source_snapshot,
                context_facts=locals(),
                applied_at=self._now(),
            )
        assert resource is not None
        worksheet = effective_standard_worksheet_name(resource) or "认可标准"
        try:
            catalog = self._catalog.read_standard_records()
        except Exception as exc:
            unavailable_reason = _availability_reason(exc)
            if unavailable_reason:
                return _resolve_unavailable(
                    action=standard_version_unavailable_action,
                    reason_code=unavailable_reason,
                    resource=resource,
                    draft=draft,
                    source_snapshot=source_snapshot,
                    context_facts=locals(),
                    applied_at=self._now(),
                )
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
                warning=None,
            ),
        )

    def _load_resource(self) -> tuple[ExternalResource | None, str | None]:
        resource = self._resources.get_by_type(ExternalResourceType.STANDARD_RECORD_EXCEL)
        if resource is None:
            return None, "standard_version_not_configured"
        if not resource.active:
            return resource, "standard_version_inactive"
        if getattr(self._resources, "requires_file_preflight", False):
            try:
                if not stat.S_ISREG(resource.path.stat().st_mode):
                    return resource, "standard_version_file_missing"
            except FileNotFoundError:
                return resource, "standard_version_file_missing"
            except OSError as exc:
                reason = _availability_reason(exc)
                if reason:
                    return resource, reason
                raise MatrixImportMethodAuthorityError(
                    "Standard version file availability could not be verified."
                ) from exc
        return resource, None


def _resolve_unavailable(
    *,
    action: StandardVersionUnavailableAction,
    reason_code: str,
    resource: ExternalResource | None,
    draft: ProjectMatrixDraftSnapshot,
    source_snapshot: SourceMatrixSnapshot,
    context_facts: dict[str, object],
    applied_at: str,
) -> MatrixImportMethodAuthorityResult:
    if action == "prompt_if_unavailable":
        raise MatrixImportStandardVersionActionRequiredError(reason_code)
    if action != "preserve_imported_methods":
        raise MatrixImportMethodAuthorityError(
            "standard_version_unavailable_action is invalid."
        )
    source_by_id = {row.row_snapshot_id: row for row in source_snapshot.rows}
    decisions = tuple(
        MatrixImportMethodAuthorityRow(
            stable_source_row_key=_stable_source_row_key(
                source_by_id.get(row.source_row_snapshot_id or ""), row.row_order
            ),
            row_order=row.row_order,
            test_item=row.test_item,
            current_method=row.method,
            status="source_preserved",
            resulting_method=row.method,
            matched_standard_code=None,
            source_row_number=None,
            reason="Imported Method preserved because Standard version authority was unavailable.",
            applied=False,
        )
        for row in sorted(draft.rows, key=lambda item: item.row_order)
    )
    method_fingerprint = fingerprint_draft_methods(draft, source_snapshot)
    resource_path = canonical_windows_path(str(resource.path)) if resource else None
    worksheet = effective_standard_worksheet_name(resource) if resource else None
    context = {
        "schema": "matrix-import-method-fallback:v1",
        "mode": "replace_import",
        **{
            key: context_facts[key]
            for key in (
                "project_id",
                "source_import_id",
                "source_snapshot_id",
                "task261_commit_fingerprint",
                "source_locator_fingerprint",
                "payload_fingerprint",
                "selected_group_fingerprint",
                "source_root_fingerprint",
                "source_row_fingerprint",
            )
        },
        "project_matrix_draft_id": draft.record.project_matrix_draft_id,
        "authority_status": "source_preserved",
        "fallback_reason_code": reason_code,
        "standard_resource_id": resource.resource_id if resource else None,
        "standard_resource_path": resource_path,
        "effective_worksheet_name": worksheet,
        "catalog_fingerprint": None,
        "pre_method_fingerprint": method_fingerprint,
        "proposal_fingerprint": fingerprint([_row_identity(row) for row in decisions]),
        "post_method_fingerprint": method_fingerprint,
        "result_fingerprint": fingerprint_draft_snapshot(draft, source_snapshot),
        "applied_at": applied_at,
        "row_results": [_row_context(row) for row in decisions],
    }
    context["context_identity_fingerprint"] = _context_identity(context)
    context_json = canonical_json(context)
    preserved = replace(
        draft,
        record=replace(draft.record, method_sync_context_json=context_json),
    )
    return MatrixImportMethodAuthorityResult(
        draft=preserved,
        context_json=context_json,
        summary=MatrixImportMethodAuthoritySummary(
            status="source_preserved",
            updated_count=0,
            current_count=0,
            review_count=0,
            standard_resource_id=resource.resource_id if resource else None,
            effective_worksheet_name=worksheet,
            catalog_fingerprint=None,
            context_fingerprint=str(context["context_identity_fingerprint"]),
            rows=decisions,
            warning=MatrixImportMethodAuthorityWarning(
                code="standard_version_unavailable",
                message=STANDARD_VERSION_WARNING,
            ),
        ),
    )


def _availability_reason(error: BaseException) -> str | None:
    current: BaseException | None = error
    visited: set[int] = set()
    for _ in range(8):
        if current is None or id(current) in visited:
            return None
        visited.add(id(current))
        if isinstance(current, LegacyExcelComUnavailableError):
            return "standard_version_runtime_unavailable"
        if isinstance(current, FileNotFoundError):
            return "standard_version_file_missing"
        if isinstance(current, PermissionError):
            return "standard_version_file_unavailable"
        if isinstance(current, OSError) and getattr(current, "winerror", None) in (
            _WINDOWS_AVAILABILITY_CODES
        ):
            return "standard_version_file_unavailable"
        current = current.__cause__ or current.__context__
    return None


def fingerprint_draft_methods(draft: ProjectMatrixDraftSnapshot, source: SourceMatrixSnapshot) -> str:
    keys = _stable_keys_by_source_id(source)
    return fingerprint(
        [
            [keys.get(row.source_row_snapshot_id), row.row_order, row.method]
            for row in sorted(draft.rows, key=lambda item: item.row_order)
        ]
    )


def fingerprint_draft_snapshot(draft: ProjectMatrixDraftSnapshot, source: SourceMatrixSnapshot) -> str:
    source_rows = _stable_keys_by_source_id(source)
    groups = {group.draft_group_id: [group.group_order, group.group_key] for group in draft.groups}
    rows = {row.draft_row_id: [row.row_order, source_rows.get(row.source_row_snapshot_id)] for row in draft.rows}
    group_facts = [[g.group_order, g.group_key, g.group_label, g.sample_quantity_expression, g.sample_note] for g in draft.groups]
    row_facts = [[r.row_order, source_rows.get(r.source_row_snapshot_id), r.test_item, r.source_section, r.method, r.condition, r.requirement] for r in draft.rows]
    cell_facts = sorted([rows[cell.draft_row_id], groups[cell.draft_group_id], cell.cell_value] for cell in draft.cells)
    return fingerprint({"groups": group_facts, "rows": row_facts, "cells": cell_facts})


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
    return fingerprint({key: value for key, value in context.items() if key not in {"context_identity_fingerprint", "applied_at"}})
