from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.application.external_excel_read_service import (
    StandardRecordReadResult,
    StandardRecordRow,
)
from backend.application.matrix_import_method_authority import (
    CachedStandardResourceStore,
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
from backend.infrastructure.office.excel_com_readonly_tabular_gateway import (
    LegacyExcelComUnavailableError,
)


def _resource(
    *,
    active: bool = True,
    path: str = "C:/standards.xlsx",
) -> ExternalResource:
    return ExternalResource(
        resource_id="standard-1",
        resource_type=ExternalResourceType.STANDARD_RECORD_EXCEL,
        path=Path(path),
        active=active,
        worksheet_name="认可标准",
    )


@pytest.mark.parametrize(
    ("resource", "failure", "reason_code"),
    [
        (None, None, "standard_version_not_configured"),
        (_resource(active=False), None, "standard_version_inactive"),
        (_resource(), FileNotFoundError("missing"), "standard_version_file_missing"),
        (_resource(), PermissionError("denied"), "standard_version_file_unavailable"),
        (
            _resource(path="C:/legacy.xls"),
            LegacyExcelComUnavailableError("Excel unavailable"),
            "standard_version_runtime_unavailable",
        ),
    ],
)
def test_prompt_returns_typed_action_required_for_only_allowed_availability(
    resource: ExternalResource | None,
    failure: Exception | None,
    reason_code: str,
) -> None:
    resolver = _resolver(resource=resource, failure=failure)

    with pytest.raises(MatrixImportMethodAuthorityError) as caught:
        _resolve(resolver)

    assert type(caught.value).__name__ == "MatrixImportStandardVersionActionRequiredError"
    assert getattr(caught.value, "reason_code", None) == reason_code
    assert str(caught.value) == "Standard version file unavailable."


def test_windows_sharing_violation_in_bounded_cause_chain_is_availability() -> None:
    windows_error = OSError("sharing violation")
    windows_error.winerror = 32  # type: ignore[attr-defined]
    wrapper = RuntimeError("catalog read failed")
    wrapper.__cause__ = windows_error

    with pytest.raises(MatrixImportMethodAuthorityError) as caught:
        _resolve(_resolver(resource=_resource(), failure=wrapper))

    assert type(caught.value).__name__ == "MatrixImportStandardVersionActionRequiredError"
    assert getattr(caught.value, "reason_code", None) == (
        "standard_version_file_unavailable"
    )


def test_production_store_preflight_reports_missing_file_without_reader(tmp_path: Path) -> None:
    reader = _CatalogReader(None)
    resolver = MatrixImportMethodAuthorityResolver(
        resource_store=CachedStandardResourceStore(
            _ResourceStore(_resource(path=str(tmp_path / "missing.xlsx")))
        ),
        catalog_reader=reader,
    )

    with pytest.raises(MatrixImportMethodAuthorityError) as caught:
        _resolve(resolver)

    assert getattr(caught.value, "reason_code", None) == "standard_version_file_missing"
    assert reader.calls == 0


def test_preserve_retry_keeps_exact_methods_and_records_fallback_context() -> None:
    draft = _draft((None, "", " ANSI / EIA-364-04A-2010 · 原值 "))
    source = _source_snapshot(3)

    result = _resolve(
        _resolver(resource=None),
        draft=draft,
        source=source,
        unavailable_action="preserve_imported_methods",
    )

    assert [row.method for row in result.draft.rows] == [
        None,
        "",
        " ANSI / EIA-364-04A-2010 · 原值 ",
    ]
    assert result.summary.status == "source_preserved"
    assert result.summary.standard_resource_id is None
    assert result.summary.effective_worksheet_name is None
    assert result.summary.catalog_fingerprint is None
    assert result.summary.warning is not None
    assert result.summary.warning.code == "standard_version_unavailable"
    assert result.summary.warning.message == (
        "Standard version file unavailable. Original Method values were kept. "
        "You can update them later in Standard Method versions."
    )
    assert all(row.status == "source_preserved" for row in result.summary.rows)
    assert all(not row.applied for row in result.summary.rows)
    assert all(row.matched_standard_code is None for row in result.summary.rows)
    context = json.loads(result.context_json)
    assert context["schema"] == "matrix-import-method-fallback:v1"
    assert context["authority_status"] == "source_preserved"
    assert context["fallback_reason_code"] == "standard_version_not_configured"
    assert context["standard_resource_id"] is None
    assert context["standard_resource_path"] is None
    assert context["effective_worksheet_name"] is None
    assert context["catalog_fingerprint"] is None
    assert context["pre_method_fingerprint"] == context["post_method_fingerprint"]
    assert context["context_identity_fingerprint"] == result.summary.context_fingerprint


@pytest.mark.parametrize(
    "failure",
    [
        ValueError("corrupt workbook"),
        RuntimeError("unknown reader failure"),
    ],
)
def test_preserve_retry_does_not_downgrade_integrity_or_unknown_failures(
    failure: Exception,
) -> None:
    with pytest.raises(MatrixImportMethodAuthorityError) as caught:
        _resolve(
            _resolver(resource=_resource(), failure=failure),
            unavailable_action="preserve_imported_methods",
        )

    assert type(caught.value).__name__ != "MatrixImportStandardVersionActionRequiredError"
    assert "could not be read" in str(caught.value)


def test_configured_success_keeps_v1_nonnullable_authority_contract() -> None:
    result = _resolve(_resolver(resource=_resource()))

    assert result.summary.status == "synchronized"
    assert result.summary.standard_resource_id == "standard-1"
    assert result.summary.effective_worksheet_name == "认可标准"
    assert result.summary.catalog_fingerprint
    assert result.summary.warning is None
    assert json.loads(result.context_json)["schema"] == "matrix-import-method-sync:v1"


def _resolver(
    *,
    resource: ExternalResource | None,
    failure: Exception | None = None,
) -> MatrixImportMethodAuthorityResolver:
    return MatrixImportMethodAuthorityResolver(
        resource_store=_ResourceStore(resource),
        catalog_reader=_CatalogReader(failure),
        now=lambda: "2026-08-01T00:00:00+00:00",
    )


def _resolve(
    resolver: MatrixImportMethodAuthorityResolver,
    *,
    draft: ProjectMatrixDraftSnapshot | None = None,
    source: SourceMatrixSnapshot | None = None,
    unavailable_action: str | None = None,
):
    values = {
        "draft": draft or _draft(("EIA-364-18B",)),
        "source_snapshot": source or _source_snapshot(1),
        "project_id": "P1",
        "source_import_id": "smi-1",
        "source_snapshot_id": "sms-1",
        "task261_commit_fingerprint": "task261",
        "source_locator_fingerprint": "locator",
        "payload_fingerprint": "payload",
        "selected_group_fingerprint": "groups",
        "source_root_fingerprint": "source-root",
        "source_row_fingerprint": "source-rows",
    }
    if unavailable_action is not None:
        values["standard_version_unavailable_action"] = unavailable_action
    return resolver.resolve(**values)


def _draft(methods: tuple[str | None, ...]) -> ProjectMatrixDraftSnapshot:
    return ProjectMatrixDraftSnapshot(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id="draft-1",
            project_id="P1",
            source_import_id="smi-1",
            source_snapshot_id="sms-1",
            status=ProjectMatrixDraftStatus.DRAFT,
            created_at="2026-08-01T00:00:00+00:00",
            updated_at="2026-08-01T00:00:00+00:00",
        ),
        rows=tuple(
            ProjectMatrixDraftRow(
                draft_row_id=f"row-{position}",
                project_matrix_draft_id="draft-1",
                source_row_snapshot_id=f"source-row-{position}",
                row_order=position,
                test_item=f"Item {position}",
                method=method,
            )
            for position, method in enumerate(methods, start=1)
        ),
    )


def _source_snapshot(count: int) -> SourceMatrixSnapshot:
    return SourceMatrixSnapshot(
        snapshot_id="sms-1",
        import_id="smi-1",
        project_id="P1",
        source_table_index=1,
        rows=tuple(
            SourceMatrixRowSnapshot(
                row_snapshot_id=f"source-row-{position}",
                row_order=position,
                source_row_index=position,
                test_item=f"Item {position}",
            )
            for position in range(1, count + 1)
        ),
    )


class _ResourceStore:
    def __init__(self, resource: ExternalResource | None) -> None:
        self.resource = resource

    def get_by_type(self, resource_type: ExternalResourceType) -> ExternalResource | None:
        assert resource_type is ExternalResourceType.STANDARD_RECORD_EXCEL
        return self.resource


class _CatalogReader:
    def __init__(self, failure: Exception | None) -> None:
        self.failure = failure
        self.calls = 0

    def read_standard_records(self) -> StandardRecordReadResult:
        self.calls += 1
        if self.failure is not None:
            raise self.failure
        return StandardRecordReadResult(
            resource_path="C:/standards.xlsx",
            matched_sheets=("认可标准",),
            rows=(
                StandardRecordRow(
                    standard_code="EIA-364-18B-2024",
                    test_item="Visual",
                    sample_description=None,
                    source_sheet="认可标准",
                    source_row_number=3,
                ),
            ),
        )
