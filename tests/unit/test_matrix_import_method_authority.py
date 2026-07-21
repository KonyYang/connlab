from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.application.external_excel_read_service import (
    StandardRecordReadResult,
    StandardRecordRow,
)
from backend.application.matrix_import_method_authority import (
    MatrixImportMethodAuthorityError,
    MatrixImportMethodAuthorityResolver,
)
from backend.domain import (
    ExternalResource,
    ExternalResourceType,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
    SourceMatrixRowSnapshot,
    SourceMatrixSnapshot,
)


def test_resolve_updates_safe_rows_and_records_explicit_review_outcomes() -> None:
    reader = _CatalogReader(
        StandardRecordReadResult(
            resource_path="C:/standards.xlsx",
            matched_sheets=("认可标准",),
            rows=(
                StandardRecordRow(
                    standard_code="EIA-364-18C-2024",
                    test_item="Visual",
                    sample_description=None,
                    source_sheet="认可标准",
                    source_row_number=3,
                ),
            ),
        )
    )
    resolver = _resolver(reader)

    result = resolver.resolve(
        draft=_draft(("EIA-364-18B", "No standard", "EIA-364-18B / 364-20A")),
        source_snapshot=_source_snapshot((1, 2, 3)),
        project_id="P1",
        source_import_id="smi-1",
        source_snapshot_id="sms-1",
        task261_commit_fingerprint="task261",
        source_locator_fingerprint="locator",
        payload_fingerprint="payload",
        selected_group_fingerprint="groups",
        source_root_fingerprint="source-root",
        source_row_fingerprint="source-rows",
    )

    assert reader.calls == 1
    assert [row.method for row in result.draft.rows] == [
        "EIA-364-18C",
        "No standard",
        "EIA-364-18B / 364-20A",
    ]
    assert [row.status for row in result.summary.rows] == [
        "update_available",
        "no_method_core",
        "multiple_method_cores",
    ]
    assert result.summary.status == "review_required"
    assert result.summary.updated_count == 1
    assert result.summary.current_count == 0
    assert result.summary.review_count == 2
    context = json.loads(result.context_json)
    assert context["schema"] == "matrix-import-method-sync:v1"
    assert context["mode"] == "replace_import"
    assert context["standard_resource_id"] == "standard-1"
    assert context["standard_resource_path"] == "c:\\standards.xlsx"
    assert context["effective_worksheet_name"] == "认可标准"
    assert context["matched_worksheet_name"] == "认可标准"
    assert context["context_identity_fingerprint"] == result.summary.context_fingerprint
    assert result.draft.record.method_sync_context_json == result.context_json


def test_resolve_blocks_missing_or_duplicate_source_row_identity_without_updating() -> None:
    resolver = _resolver(_catalog_reader())
    draft = _draft(("EIA-364-18B", "EIA-364-18B", "EIA-364-18B"), indexes=(1, 1, None))

    result = resolver.resolve(
        draft=draft,
        source_snapshot=_source_snapshot((1, 1, None)),
        project_id="P1",
        source_import_id="smi-1",
        source_snapshot_id="sms-1",
        task261_commit_fingerprint="task261",
        source_locator_fingerprint="locator",
        payload_fingerprint="payload",
        selected_group_fingerprint="groups",
        source_root_fingerprint="source-root",
        source_row_fingerprint="source-rows",
    )

    assert [row.status for row in result.summary.rows] == [
        "row_identity_duplicate",
        "row_identity_duplicate",
        "row_identity_missing",
    ]
    assert [row.method for row in result.draft.rows] == [row.method for row in draft.rows]
    assert result.summary.updated_count == 0
    assert result.summary.review_count == 3


@pytest.mark.parametrize(
    ("resource_path", "matched_sheets", "message"),
    [
        ("C:/other.xlsx", ("认可标准",), "path"),
        ("C:/standards.xlsx", ("Other",), "worksheet"),
        ("C:/standards.xlsx", ("认可标准", "Other"), "worksheet"),
    ],
)
def test_resolve_rejects_catalog_source_context_mismatch(
    resource_path: str,
    matched_sheets: tuple[str, ...],
    message: str,
) -> None:
    resolver = _resolver(
        _CatalogReader(
            StandardRecordReadResult(
                resource_path=resource_path,
                matched_sheets=matched_sheets,
                rows=(),
            )
        )
    )

    with pytest.raises(MatrixImportMethodAuthorityError, match=message):
        resolver.resolve(
            draft=_draft(("EIA-364-18B",)),
            source_snapshot=_source_snapshot((1,)),
            project_id="P1",
            source_import_id="smi-1",
            source_snapshot_id="sms-1",
            task261_commit_fingerprint="task261",
            source_locator_fingerprint="locator",
            payload_fingerprint="payload",
            selected_group_fingerprint="groups",
            source_root_fingerprint="source-root",
            source_row_fingerprint="source-rows",
        )


def _resolver(reader: "_CatalogReader") -> MatrixImportMethodAuthorityResolver:
    return MatrixImportMethodAuthorityResolver(
        resource_store=_ResourceStore(),
        catalog_reader=reader,
        now=lambda: "2026-07-21T00:00:00+00:00",
    )


def _catalog_reader() -> "_CatalogReader":
    return _CatalogReader(
        StandardRecordReadResult(
            resource_path="C:/standards.xlsx",
            matched_sheets=("认可标准",),
            rows=(
                StandardRecordRow(
                    standard_code="EIA-364-18C-2024",
                    test_item="Visual",
                    sample_description=None,
                    source_sheet="认可标准",
                    source_row_number=3,
                ),
            ),
        )
    )


def _draft(
    methods: tuple[str, ...],
    *,
    indexes: tuple[int | None, ...] | None = None,
) -> ProjectMatrixDraftSnapshot:
    source_indexes = indexes or tuple(range(1, len(methods) + 1))
    return ProjectMatrixDraftSnapshot(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id="draft-1",
            project_id="P1",
            source_import_id="smi-1",
            source_snapshot_id="sms-1",
            status=ProjectMatrixDraftStatus.DRAFT,
            created_at="2026-07-21T00:00:00+00:00",
            updated_at="2026-07-21T00:00:00+00:00",
        ),
        rows=tuple(
            ProjectMatrixDraftRow(
                draft_row_id=f"row-{position}",
                project_matrix_draft_id="draft-1",
                source_row_snapshot_id=(
                    f"source-row-{position}"
                ),
                row_order=position,
                test_item=f"Item {position}",
                method=method,
            )
            for position, (method, source_index) in enumerate(
                zip(methods, source_indexes, strict=True),
                start=1,
            )
        ),
    )


def _source_snapshot(indexes: tuple[int | None, ...]) -> SourceMatrixSnapshot:
    return SourceMatrixSnapshot(
        snapshot_id="sms-1",
        import_id="smi-1",
        project_id="P1",
        source_table_index=1,
        rows=tuple(
            SourceMatrixRowSnapshot(
                row_snapshot_id=f"source-row-{position}",
                row_order=position,
                source_row_index=source_index,
                test_item=f"Item {position}",
            )
            for position, source_index in enumerate(indexes, start=1)
        ),
    )


class _ResourceStore:
    def get_by_type(self, resource_type: ExternalResourceType) -> ExternalResource | None:
        assert resource_type is ExternalResourceType.STANDARD_RECORD_EXCEL
        return ExternalResource(
            resource_id="standard-1",
            resource_type=resource_type,
            path=Path("C:/standards.xlsx"),
            worksheet_name="认可标准",
        )


class _CatalogReader:
    def __init__(self, result: StandardRecordReadResult) -> None:
        self.result = result
        self.calls = 0

    def read_standard_records(self) -> StandardRecordReadResult:
        self.calls += 1
        return self.result
