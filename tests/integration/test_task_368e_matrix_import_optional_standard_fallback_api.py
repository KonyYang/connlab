from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.application.external_excel_read_service import (
    StandardRecordReadResult,
    StandardRecordRow,
)
from backend.domain import ExternalResource, ExternalResourceType
from backend.infrastructure.storage.repositories import ProjectMatrixDraftRepository
from backend.infrastructure.office.excel_com_readonly_tabular_gateway import (
    LegacyExcelCleanupError,
    LegacyExcelComUnavailableError,
)
from tests.integration.test_matrix_import_method_authority_commit_api import (
    _client,
    _counts,
    _request,
)


def test_initial_missing_resource_returns_typed_choice_before_any_write(tmp_path: Path) -> None:
    authority = _Authority(resource=None)
    client, engine, session_factory = _client(tmp_path, authority)
    try:
        response = client.post("/api/projects/P1/matrix-import/commit", json=_request())

        assert response.status_code == 409
        assert response.json()["detail"] == {
            "code": "matrix_import_standard_version_action_required",
            "reason_code": "standard_version_not_configured",
            "message": "Standard version file unavailable.",
        }
        assert _counts(session_factory) == (0, 0)
        assert authority.reader.calls == 0
    finally:
        _close(engine)


@pytest.mark.parametrize(
    ("resource_state", "failure", "reason_code"),
    [
        ("missing", None, "standard_version_not_configured"),
        ("inactive", None, "standard_version_inactive"),
        ("active", FileNotFoundError("missing"), "standard_version_file_missing"),
        ("active", PermissionError("denied"), "standard_version_file_unavailable"),
        (
            "legacy",
            LegacyExcelComUnavailableError("Excel unavailable"),
            "standard_version_runtime_unavailable",
        ),
    ],
)
def test_skip_returns_201_for_every_allowed_availability_state(
    tmp_path: Path,
    resource_state: str,
    failure: Exception | None,
    reason_code: str,
) -> None:
    resource = {
        "missing": None,
        "inactive": _resource(active=False),
        "active": _resource(),
        "legacy": _resource(path="C:/legacy.xls"),
    }[resource_state]
    authority = _Authority(resource=resource, failure=failure)
    client, engine, session_factory = _client(tmp_path, authority)
    try:
        response = client.post(
            "/api/projects/P1/matrix-import/commit",
            json={
                **_request(),
                "standard_version_unavailable_action": "preserve_imported_methods",
            },
        )

        assert response.status_code == 201
        assert response.json()["method_authority_sync"]["status"] == "source_preserved"
        assert _counts(session_factory) == (1, 1)
        with session_factory() as session:
            record = ProjectMatrixDraftRepository(session).get_by_project_and_source_import(
                "P1", response.json()["source_import_id"]
            )
            assert record is not None
            draft = ProjectMatrixDraftRepository(session).get(record.project_matrix_draft_id)
            assert draft is not None
            context = json.loads(draft.record.method_sync_context_json or "")
            assert context["fallback_reason_code"] == reason_code
    finally:
        _close(engine)


def test_skip_creates_source_preserved_draft_and_strictly_reuses(tmp_path: Path) -> None:
    authority = _Authority(resource=None)
    client, engine, session_factory = _client(tmp_path, authority)
    request = {
        **_request(),
        "standard_version_unavailable_action": "preserve_imported_methods",
    }
    try:
        first = client.post("/api/projects/P1/matrix-import/commit", json=request)
        assert first.status_code == 201
        body = first.json()
        assert body["commit_status"] == "created"
        assert [row["method"] for row in body["project_matrix_draft"]["rows"]] == [
            "EIA-364-18B",
            "EIA-364-20A",
        ]
        summary = body["method_authority_sync"]
        assert summary["status"] == "source_preserved"
        assert summary["standard_resource_id"] is None
        assert summary["effective_worksheet_name"] is None
        assert summary["catalog_fingerprint"] is None
        assert summary["warning"] == {
            "code": "standard_version_unavailable",
            "message": (
                "Standard version file unavailable. Original Method values were kept. "
                "You can update them later in Standard Method versions."
            ),
        }
        assert {row["status"] for row in summary["rows"]} == {"source_preserved"}
        counts = _counts(session_factory)
        assert counts == (1, 1)
        with session_factory() as session:
            draft = ProjectMatrixDraftRepository(session).get(
                body["project_matrix_draft"]["record"]["project_matrix_draft_id"]
            )
            assert draft is not None
            context = json.loads(draft.record.method_sync_context_json or "")
            assert context["schema"] == "matrix-import-method-fallback:v1"
            assert context["pre_method_fingerprint"] == context["post_method_fingerprint"]

        replay = client.post("/api/projects/P1/matrix-import/commit", json=request)
        assert replay.status_code == 201
        assert replay.json()["commit_status"] == "reused"
        assert _counts(session_factory) == counts
    finally:
        _close(engine)


def test_skip_cannot_suppress_integrity_failure(tmp_path: Path) -> None:
    authority = _Authority(resource=_resource(), failure=ValueError("corrupt workbook"))
    client, engine, session_factory = _client(tmp_path, authority)
    try:
        response = client.post(
            "/api/projects/P1/matrix-import/commit",
            json={
                **_request(),
                "standard_version_unavailable_action": "preserve_imported_methods",
            },
        )
        assert response.status_code == 422
        assert "corrupt workbook" in response.json()["detail"]
        assert _counts(session_factory) == (0, 0)
    finally:
        _close(engine)


@pytest.mark.parametrize(
    "unavailable_action",
    [None, "preserve_imported_methods"],
)
@pytest.mark.parametrize("nested_failure_kind", ["permission", "windows"])
def test_cleanup_integrity_wrapper_is_422_zero_write_without_skip_detail(
    tmp_path: Path,
    unavailable_action: str | None,
    nested_failure_kind: str,
) -> None:
    nested: OSError
    if nested_failure_kind == "permission":
        nested = PermissionError("cleanup denied")
    else:
        nested = OSError("cleanup sharing violation")
        nested.winerror = 32  # type: ignore[attr-defined]
    cleanup = LegacyExcelCleanupError("cleanup failed")
    cleanup.__cause__ = nested
    authority = _Authority(resource=_resource(), failure=cleanup)
    client, engine, session_factory = _client(tmp_path, authority)
    request = _request()
    if unavailable_action is not None:
        request["standard_version_unavailable_action"] = unavailable_action
    try:
        response = client.post("/api/projects/P1/matrix-import/commit", json=request)

        assert response.status_code == 422
        assert response.json()["detail"].endswith("cleanup failed")
        assert "matrix_import_standard_version_action_required" not in response.text
        assert _counts(session_factory) == (0, 0)
    finally:
        _close(engine)


def test_newly_readable_authority_conflicts_with_prior_fallback(tmp_path: Path) -> None:
    authority = _Authority(resource=None)
    client, engine, session_factory = _client(tmp_path, authority)
    request = {
        **_request(),
        "standard_version_unavailable_action": "preserve_imported_methods",
    }
    try:
        assert client.post("/api/projects/P1/matrix-import/commit", json=request).status_code == 201
        counts = _counts(session_factory)
        authority.resource = _resource()

        conflict = client.post("/api/projects/P1/matrix-import/commit", json=request)
        assert conflict.status_code == 409
        assert _counts(session_factory) == counts
    finally:
        _close(engine)


def test_skip_persistence_failure_rolls_back_source_and_draft(tmp_path: Path) -> None:
    authority = _Authority(resource=None)
    client, engine, session_factory = _client(tmp_path, authority, fail_after_draft=True)
    try:
        response = client.post(
            "/api/projects/P1/matrix-import/commit",
            json={
                **_request(),
                "standard_version_unavailable_action": "preserve_imported_methods",
            },
        )
        assert response.status_code == 409
        assert _counts(session_factory) == (0, 0)
    finally:
        _close(engine)


def _resource(*, active: bool = True, path: str = "C:/standards.xlsx") -> ExternalResource:
    return ExternalResource(
        resource_id="standard-1",
        resource_type=ExternalResourceType.STANDARD_RECORD_EXCEL,
        path=Path(path),
        active=active,
        worksheet_name="认可标准",
    )


class _Authority:
    def __init__(
        self,
        *,
        resource: ExternalResource | None,
        failure: Exception | None = None,
    ) -> None:
        self.resource = resource
        self.reader = _Reader(failure)

    def get_by_type(self, resource_type: ExternalResourceType) -> ExternalResource | None:
        assert resource_type is ExternalResourceType.STANDARD_RECORD_EXCEL
        return self.resource


class _Reader:
    def __init__(self, failure: Exception | None) -> None:
        self.failure = failure
        self.calls = 0

    def read_standard_records(self) -> StandardRecordReadResult:
        self.calls += 1
        if self.failure:
            raise self.failure
        return StandardRecordReadResult(
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


def _close(engine) -> None:
    from backend.api.main import app

    app.dependency_overrides.clear()
    engine.dispose()
