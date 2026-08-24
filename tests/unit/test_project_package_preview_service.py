from __future__ import annotations

from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from backend.application.confirmed_fee_version_service import (
    ConfirmedFeeVersionReadResult,
)
from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    ConfirmedMatrixFeeTemplateBasicFillNotFoundError,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftContext,
)
from backend.application.project_package_preview_service import (
    ProjectPackagePreviewProjectNotFoundError,
    ProjectPackagePreviewService,
)
from backend.application.official_project_workspace_service import (
    OfficialWorkspaceRecord,
)
from backend.application.project_section2_sync_service import (
    ProjectSection2FieldSync,
    ProjectSection2SyncReadinessError,
    ProjectSection2SyncResult,
)
from backend.domain import (
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
    ExternalResource,
    ExternalResourceType,
    Project,
    ProjectFolderRecord,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftStatus,
    ProjectStatus,
)
from backend.domain.confirmed_fee import ConfirmedFeeSummary, ConfirmedFeeVersion

_DEFAULT_SNAPSHOT = object()


def test_project_package_preview_ready_when_required_inputs_are_ready(
    tmp_path: Path,
) -> None:
    folder_path = tmp_path / "project-folder"
    folder_path.mkdir()
    template_folder = tmp_path / "templates"
    template_folder.mkdir()
    (template_folder / "E-4243_D Customer Feedback Form.xlsx").write_bytes(b"template")
    service = _service(folder_path=folder_path, template_folder=template_folder)

    result = service.preview("P1")

    assert result.status == "ready"
    assert result.project_folder.status == "ready"
    assert result.authority_context.confirmed_matrix_id == "CM1"
    assert result.authority_context.confirmed_fee_status == "current"
    assert result.blockers == ()
    assert {item.key: item.status for item in result.required_items} == {
        "test_record": "ready",
        "fee_form": "ready",
        "application_form_section2": "ready",
        "customer_feedback_form": "ready",
    }
    assert result.optional_items[0].status == "deferred"


def test_project_package_preview_blocks_missing_project(tmp_path: Path) -> None:
    service = _service(project=None, folder_path=tmp_path / "folder")

    with pytest.raises(ProjectPackagePreviewProjectNotFoundError):
        service.preview("P1")


def test_project_package_preview_blocks_missing_folder(tmp_path: Path) -> None:
    service = _service(folder_path=None, template_folder=_template_folder(tmp_path))

    result = service.preview("P1")

    assert result.status == "blocked"
    assert "Create the project folder" in result.blockers[0]


def test_project_package_preview_uses_official_workspace_record_when_legacy_folder_missing(
    tmp_path: Path,
) -> None:
    official_folder = tmp_path / "DL-2026-05-003" / "DL-2026-05-003 Product Qualification test"
    official_folder.mkdir(parents=True)
    service = _service(
        folder_path=None,
        official_workspace_folder=official_folder,
        template_folder=_template_folder(tmp_path),
    )

    result = service.preview("P1")

    assert result.status == "ready"
    assert result.project_folder.status == "ready"
    assert result.project_folder.path == str(official_folder)
    assert "Create the project folder before previewing package targets." not in result.blockers


def test_project_package_preview_blocks_missing_official_workspace_folder(
    tmp_path: Path,
) -> None:
    official_folder = tmp_path / "missing-official-folder"
    service = _service(
        folder_path=None,
        official_workspace_folder=official_folder,
        template_folder=_template_folder(tmp_path),
    )

    result = service.preview("P1")

    assert result.status == "blocked"
    assert "Local official project folder path is not available" in result.blockers[0]


def test_project_package_preview_blocks_non_directory_folder(tmp_path: Path) -> None:
    folder_path = tmp_path / "project-folder"
    folder_path.write_text("not a directory", encoding="utf-8")
    service = _service(folder_path=folder_path, template_folder=_template_folder(tmp_path))

    result = service.preview("P1")

    assert result.status == "blocked"
    assert "not available" in " ".join(result.blockers)


def test_project_package_preview_blocks_missing_confirmed_matrix(tmp_path: Path) -> None:
    service = _service(
        folder_path=_project_folder(tmp_path),
        template_folder=_template_folder(tmp_path),
        snapshot=None,
    )

    result = service.preview("P1")

    assert result.status == "blocked"
    assert "Create or import a Matrix draft" in " ".join(result.blockers)
    assert _item_status(result, "test_record") == "blocked"


def test_project_package_preview_uses_matrix_draft_without_blocking_or_confirmed_fee_lookup(
    tmp_path: Path,
) -> None:
    service = _service(
        folder_path=_project_folder(tmp_path),
        template_folder=_template_folder(tmp_path),
        snapshot=None,
        matrix_drafts=[_matrix_draft_record()],
        fee_status="error",
    )

    result = service.preview("P1")

    assert result.status == "ready"
    assert result.blockers == ()
    assert result.authority_context.matrix_source == "draft"
    assert result.authority_context.project_matrix_draft_id == "D1"
    assert "using the latest Matrix draft" in " ".join(result.warnings)
    assert _item_status(result, "test_record") == "warning"
    assert _item_status(result, "fee_form") == "warning"


def test_project_package_preview_ignores_superseded_matrix_drafts(tmp_path: Path) -> None:
    service = _service(
        folder_path=_project_folder(tmp_path),
        template_folder=_template_folder(tmp_path),
        snapshot=None,
        matrix_drafts=[
            _matrix_draft_record(
                status=ProjectMatrixDraftStatus.SUPERSEDED,
                updated_at="2026-06-12T00:00:00+00:00",
            )
        ],
    )

    result = service.preview("P1")

    assert result.status == "blocked"
    assert result.authority_context.matrix_source == "missing"
    assert result.authority_context.project_matrix_draft_id is None


def test_project_package_preview_blocks_missing_confirmed_fee(tmp_path: Path) -> None:
    service = _service(
        folder_path=_project_folder(tmp_path),
        template_folder=_template_folder(tmp_path),
        fee_status="missing",
    )

    result = service.preview("P1")

    assert result.status == "blocked"
    assert "Confirm Fee" in " ".join(result.blockers)
    assert _item_status(result, "fee_form") == "blocked"


def test_project_package_preview_blocks_confirmed_fee_readiness_error(
    tmp_path: Path,
) -> None:
    service = _service(
        folder_path=_project_folder(tmp_path),
        template_folder=_template_folder(tmp_path),
        fee_status="error",
    )

    result = service.preview("P1")

    assert result.status == "blocked"
    assert "Confirmed Fee readiness is blocked" in " ".join(result.blockers)
    assert result.authority_context.confirmed_fee_status == "blocked"
    assert _item_status(result, "fee_form") == "blocked"


def test_project_package_preview_does_not_hide_unexpected_confirmed_fee_error(
    tmp_path: Path,
) -> None:
    service = _service(
        folder_path=_project_folder(tmp_path),
        template_folder=_template_folder(tmp_path),
        fee_status="runtime_error",
    )

    with pytest.raises(RuntimeError, match="database unavailable"):
        service.preview("P1")


def test_project_package_preview_blocks_section2_ready(tmp_path: Path) -> None:
    service = _service(
        folder_path=_project_folder(tmp_path),
        template_folder=_template_folder(tmp_path),
        section2_status="ready",
    )

    result = service.preview("P1")

    assert result.status == "blocked"
    assert "Sync Section 2 dates" in " ".join(result.blockers)
    assert _item_status(result, "application_form_section2") == "blocked"


def test_project_package_preview_warns_for_section2_partial(tmp_path: Path) -> None:
    service = _service(
        folder_path=_project_folder(tmp_path),
        template_folder=_template_folder(tmp_path),
        section2_status="partial",
    )

    result = service.preview("P1")

    assert result.status == "ready"
    assert result.warnings
    assert _item_status(result, "application_form_section2") == "warning"


def test_project_package_preview_blocks_section2_readiness_error(
    tmp_path: Path,
) -> None:
    service = _service(
        folder_path=_project_folder(tmp_path),
        template_folder=_template_folder(tmp_path),
        section2_status="readiness_error",
    )

    result = service.preview("P1")

    assert result.status == "blocked"
    assert "Section 2 date readiness is blocked" in " ".join(result.blockers)
    assert _item_status(result, "application_form_section2") == "blocked"


def test_project_package_preview_does_not_hide_unexpected_section2_error(
    tmp_path: Path,
) -> None:
    service = _service(
        folder_path=_project_folder(tmp_path),
        template_folder=_template_folder(tmp_path),
        section2_status="runtime_error",
    )

    with pytest.raises(RuntimeError, match="section2 integration bug"):
        service.preview("P1")


def test_project_package_preview_blocks_customer_feedback_template_missing(
    tmp_path: Path,
) -> None:
    template_folder = tmp_path / "templates"
    template_folder.mkdir()
    service = _service(folder_path=_project_folder(tmp_path), template_folder=template_folder)

    result = service.preview("P1")

    assert result.status == "blocked"
    assert "E-4243" in " ".join(result.blockers)
    assert _item_status(result, "customer_feedback_form") == "blocked"


def test_project_package_preview_blocks_customer_feedback_template_ambiguous(
    tmp_path: Path,
) -> None:
    template_folder = tmp_path / "templates"
    template_folder.mkdir()
    (template_folder / "E-4243_D Customer Feedback Form.xlsx").write_bytes(b"one")
    (template_folder / "copy E-4243 customer feedback.xlsx").write_bytes(b"two")
    service = _service(folder_path=_project_folder(tmp_path), template_folder=template_folder)

    result = service.preview("P1")

    assert result.status == "blocked"
    assert "Multiple" in " ".join(result.blockers)


class FakeProjectStore:
    def __init__(self, project: Project | None) -> None:
        self.project = project

    def get(self, project_id: str) -> Project | None:
        return self.project if self.project and self.project.project_id == project_id else None


class FakeFolderStore:
    def __init__(self, folder_path: Path | None) -> None:
        self.folder_path = folder_path

    def list_by_project(self, project_id: str) -> list[ProjectFolderRecord]:
        if self.folder_path is None:
            return []
        return [
            ProjectFolderRecord(
                folder_id="F1",
                project_id=project_id,
                folder_path=self.folder_path,
                created_on=date(2026, 6, 1),
            )
        ]


class FakeConfirmedMatrixStore:
    def __init__(self, snapshot: ConfirmedMatrixSnapshot | None) -> None:
        self.snapshot = snapshot

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        return self.snapshot if self.snapshot and self.snapshot.version.project_id == project_id else None


class FakeMatrixDraftStore:
    def __init__(self, drafts: list[ProjectMatrixDraftRecord]) -> None:
        self.drafts = drafts

    def list_by_project(self, project_id: str) -> list[ProjectMatrixDraftRecord]:
        return [draft for draft in self.drafts if draft.project_id == project_id]


class FakeConfirmedFeeReader:
    def __init__(self, status: str) -> None:
        self.status = status

    def get_latest(self, project_id: str) -> ConfirmedFeeVersionReadResult:
        if self.status == "error":
            raise ConfirmedMatrixFeeTemplateBasicFillNotFoundError(
                "Active confirmed matrix not found."
            )
        if self.status == "runtime_error":
            raise RuntimeError("database unavailable")
        context = FeeEvaluationPricingDraftContext(
            project_id=project_id,
            confirmed_matrix_id="CM1",
            confirmed_revision=1,
            fee_rule_version_id="fee_rules_v2026_06_03",
        )
        latest = (
            ConfirmedFeeVersion(
                confirmed_fee_id="CF1",
                project_id=project_id,
                confirmed_fee_revision=1,
                confirmed_matrix_id="CM1",
                confirmed_revision=1,
                fee_rule_version_id="fee_rules_v2026_06_03",
                pricing_draft_edit_id="PD1",
                pricing_effective_from=None,
                summary=ConfirmedFeeSummary(
                    testing_fee_total="100",
                    working_hours="1",
                    lab_manpower_cost="200",
                    external_cost="0",
                    grand_cost="300",
                ),
                pricing_snapshot_json="{}",
                confirmed_by="Lab User",
                confirmed_at="2026-06-11T00:00:00+00:00",
            )
            if self.status != "missing"
            else None
        )
        return ConfirmedFeeVersionReadResult(
            status=self.status,  # type: ignore[arg-type]
            current_context=context,
            latest_confirmed_fee=latest,
        )


class FakeSection2Previewer:
    def __init__(self, status: str) -> None:
        self.status = status

    def preview(self, command: object) -> ProjectSection2SyncResult:
        project_id = getattr(command, "project_id")
        if self.status == "readiness_error":
            raise ProjectSection2SyncReadinessError(
                "Application Form is required before syncing Section 2 dates."
            )
        if self.status == "runtime_error":
            raise RuntimeError("section2 integration bug")
        return ProjectSection2SyncResult(
            project_id=project_id,
            application_form_id="AF1",
            confirmed_matrix_id="CM1",
            confirmed_revision=1,
            fields=(
                ProjectSection2FieldSync(
                    field_key="received_date",
                    source_field_key="sample_received_date",
                    source_value="2026-06-01",
                    current_value="2026-06-01",
                    next_value="2026-06-01",
                    status="unchanged",
                    message="Section 2 already matches Confirmed Matrix.",
                ),
            ),
            status=self.status,  # type: ignore[arg-type]
        )


class FakeExternalResourceStore:
    def __init__(self, template_folder: Path | None) -> None:
        self.template_folder = template_folder

    def get_by_type(self, resource_type: ExternalResourceType) -> ExternalResource | None:
        if self.template_folder is None:
            return None
        return ExternalResource(
            resource_id="R1",
            resource_type=resource_type,
            path=self.template_folder,
        )


class FakeOfficialWorkspaceStore:
    def __init__(self, official_folder_path: Path | None) -> None:
        self.official_folder_path = official_folder_path

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord | None:
        if self.official_folder_path is None:
            return None
        workspace_path = self.official_folder_path.parent
        return OfficialWorkspaceRecord(
            workspace_id="W1",
            project_id=project_id,
            dl_number="DL-2026-05-003",
            local_workspace_path=workspace_path,
            source_book_path=workspace_path / "Source Book",
            official_folder_path=self.official_folder_path,
            manifest_path=workspace_path / ".connlab" / "manifest.json",
            template_source_path=Path("D:/Source/Template/DL-XXXX-YY-ZZZ Title"),
            created_at="2026-06-13T00:00:00+00:00",
        )


def _service(
    *,
    folder_path: Path | None,
    official_workspace_folder: Path | None = None,
    template_folder: Path | None = None,
    project: Project | None = Project(
        project_id="P1",
        project_no="DL-2026-05-003",
        product_name="Coolpower",
        requestor="MP Cao",
        status=ProjectStatus.FOLDER_CREATED,
    ),
    snapshot: ConfirmedMatrixSnapshot | None | object = _DEFAULT_SNAPSHOT,
    matrix_drafts: list[ProjectMatrixDraftRecord] | None = None,
    fee_status: str = "current",
    section2_status: str = "up_to_date",
) -> ProjectPackagePreviewService:
    active_snapshot = _snapshot() if snapshot is _DEFAULT_SNAPSHOT else snapshot
    return ProjectPackagePreviewService(
        project_store=FakeProjectStore(project),
        folder_store=FakeFolderStore(folder_path),
        confirmed_matrix_store=FakeConfirmedMatrixStore(active_snapshot),
        matrix_draft_store=FakeMatrixDraftStore(matrix_drafts or []),
        confirmed_fee_reader=FakeConfirmedFeeReader(fee_status),
        section2_previewer=FakeSection2Previewer(section2_status),
        external_resource_store=FakeExternalResourceStore(template_folder),
        official_workspace_store=FakeOfficialWorkspaceStore(official_workspace_folder),
    )


def _snapshot() -> ConfirmedMatrixSnapshot:
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="CM1",
            project_id="P1",
            project_matrix_draft_id="D1",
            source_import_id="S1",
            source_snapshot_id="SS1",
            confirmed_revision=1,
            is_active_authority=True,
            status=ConfirmedMatrixStatus.CONFIRMED,
            confirmed_by="Lab User",
            confirmed_at="2026-06-11T00:00:00+00:00",
        )
    )


def _matrix_draft_record(
    *,
    status: ProjectMatrixDraftStatus = ProjectMatrixDraftStatus.DRAFT,
    updated_at: str = "2026-06-11T00:00:00+00:00",
) -> ProjectMatrixDraftRecord:
    return ProjectMatrixDraftRecord(
        project_matrix_draft_id="D1",
        project_id="P1",
        source_import_id="S1",
        source_snapshot_id="SS1",
        status=status,
        created_at="2026-06-10T00:00:00+00:00",
        updated_at=updated_at,
    )


def _project_folder(tmp_path: Path) -> Path:
    folder = tmp_path / "project-folder"
    folder.mkdir()
    return folder


def _template_folder(tmp_path: Path) -> Path:
    folder = tmp_path / "templates"
    folder.mkdir()
    (folder / "E-4243_D Customer Feedback Form.xlsx").write_bytes(b"template")
    return folder


def _item_status(result, key: str) -> str:
    return next(item.status for item in result.required_items if item.key == key)
