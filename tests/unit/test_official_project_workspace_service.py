from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pytest

from backend.application.official_project_workspace_service import (
    OfficialProjectWorkspaceService,
    OfficialWorkspaceCreateError,
    OfficialWorkspaceRecord,
    resolve_official_template_root,
)
from backend.domain import ApplicationForm, LtrRecord, LtrStatus, Project, ProjectStatus
from backend.shared.config import OfficialWorkspaceSettings


def test_preview_ready_for_new_workspace(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    service = _service(
        tmp_path,
        project=Project(
            project_id="project-1",
            project_no="DL-2025-11-074",
            product_name="Coolpower",
            requestor="Alice",
            status=ProjectStatus.CONFIRMED,
        ),
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service.preview("project-1")

    assert preview.status == "ready"
    assert preview.local_workspace_path == tmp_path / "workspaces" / "DL-2025-11-074"
    assert preview.source_book_path == preview.local_workspace_path / "Source Book"
    assert preview.official_folder_path == (
        preview.local_workspace_path / "DL-2025-11-074 Coolpower Qualification test"
    )
    assert any("Public Project locations is not configured" in warning for warning in preview.warnings)
    assert not preview.blockers


def test_resolve_template_folder_with_workspace_template_child(
    tmp_path: Path,
) -> None:
    template_folder = tmp_path / "Template"
    official_template = _make_template(
        template_folder / "DL-XXXX-YY-ZZZ project" / "DL-XXXX-YY-ZZZ Title"
    )
    (template_folder / "E-4243_D Customer Feedback Form.xlsx").write_text(
        "placeholder",
        encoding="utf-8",
    )

    resolved = resolve_official_template_root(template_folder)

    assert resolved.path == official_template
    assert resolved.mode == "workspace_template_child_root"


def test_existing_safe_dl_workspace_is_adoptable(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    existing_workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    existing_workspace.mkdir(parents=True)
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=tmp_path / "public",
        ),
    )

    preview = service.preview("project-1")

    assert preview.status == "adoptable"
    assert "Local project workspace already exists and can be continued." in preview.warnings


def test_existing_official_folder_blocks_create(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    official_folder = (
        tmp_path
        / "workspaces"
        / "DL-2025-11-074"
        / "DL-2025-11-074 Coolpower Qualification test"
    )
    official_folder.mkdir(parents=True)
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=tmp_path / "public",
        ),
    )

    preview = service.preview("project-1")

    assert preview.status == "exists"
    assert "Official project folder already exists" in preview.blockers[0]
    with pytest.raises(OfficialWorkspaceCreateError, match="Official project folder already exists"):
        service.create("project-1")


def test_create_from_adoptable_workspace_adds_missing_pieces(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    workspace.mkdir(parents=True)
    repo = _WorkspaceRepo()
    service = _service(
        tmp_path,
        repository=repo,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    result = service.create("project-1")

    assert (workspace / "Source Book").is_dir()
    assert (workspace / ".connlab" / "manifest.json").is_file()
    assert (result.official_folder_path / "Submitted Material").is_dir()
    assert repo.saved is not None
    assert repo.saved.official_folder_path == result.official_folder_path


def test_preview_completed_after_connlab_created_workspace(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    repo = _WorkspaceRepo()
    service = _service(
        tmp_path,
        repository=repo,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    result = service.create("project-1")
    preview = service.preview("project-1")

    assert preview.status == "completed"
    assert preview.official_folder_path == result.official_folder_path
    assert preview.local_workspace_path == result.record.local_workspace_path
    assert not preview.blockers


def test_preview_keeps_completed_workspace_when_current_naming_rule_changes(
    tmp_path: Path,
) -> None:
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    repo = _WorkspaceRepo()
    service = _service(
        tmp_path,
        repository=repo,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )
    result = service.create("project-1")
    service_with_updated_identity = _service(
        tmp_path,
        repository=repo,
        ltr_repository=_LtrRepo(
            [
                LtrRecord(
                    ltr_id="ltr-1",
                    project_id="project-1",
                    ltr_number="DL-2025-11-074",
                    status=LtrStatus.REGISTERED,
                    registered_on=date(2026, 5, 11),
                    notes=json.dumps(
                        {
                            "operator_note": json.dumps(
                                {
                                    "source": "new_project_setup_confirmation",
                                    "test_item": "Qualification Testing",
                                },
                                sort_keys=True,
                            )
                        },
                        sort_keys=True,
                    ),
                )
            ]
        ),
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service_with_updated_identity.preview("project-1")

    assert preview.status == "completed"
    assert preview.official_folder_path == result.official_folder_path
    assert any("current naming rule" in warning for warning in preview.warnings)
    assert not preview.blockers


def test_preview_uses_registered_ltr_when_project_no_is_missing(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    service = _service(
        tmp_path,
        project=Project(
            project_id="project-1",
            project_no=None,
            product_name="Coolpower",
            requestor="Alice",
            status=ProjectStatus.CONFIRMED,
        ),
        ltr_repository=_LtrRepo(
            [
                LtrRecord(
                    ltr_id="ltr-1",
                    project_id="project-1",
                    ltr_number="DL-2025-11-074",
                    status=LtrStatus.REGISTERED,
                )
            ]
        ),
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service.preview("project-1")

    assert preview.status == "ready"
    assert preview.dl_number == "DL-2025-11-074"
    assert preview.local_workspace_path == tmp_path / "workspaces" / "DL-2025-11-074"


def test_preview_prefers_registered_ltr_over_legacy_project_no(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    service = _service(
        tmp_path,
        project=Project(
            project_id="project-1",
            project_no="1453402",
            product_name="Coolpower",
            requestor="Alice",
            status=ProjectStatus.CONFIRMED,
        ),
        ltr_repository=_LtrRepo(
            [
                LtrRecord(
                    ltr_id="ltr-1",
                    project_id="project-1",
                    ltr_number="DL-2025-11-074",
                    status=LtrStatus.REGISTERED,
                )
            ]
        ),
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service.preview("project-1")

    assert preview.dl_number == "DL-2025-11-074"
    assert preview.local_workspace_path == tmp_path / "workspaces" / "DL-2025-11-074"


def test_preview_uses_application_form_requested_testing_in_folder_name(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    service = _service(
        tmp_path,
        forms=[
            ApplicationForm(
                form_id="form-1",
                project_id="project-1",
                form_no="E-3718",
                revision="H",
                requester="Alice",
                requested_testing="Thermal cycling and contact resistance",
            )
        ],
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service.preview("project-1")

    assert preview.official_folder_path == (
        tmp_path
        / "workspaces"
        / "DL-2025-11-074"
        / "DL-2025-11-074 Coolpower Thermal cycling and contact resistance"
    )


def test_preview_uses_ltr_sample_description_and_test_item_in_folder_name(
    tmp_path: Path,
) -> None:
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    service = _service(
        tmp_path,
        project=Project(
            project_id="project-1",
            project_no="1453402",
            product_name="Coolpower HDF 3.40mm pin",
            requestor="Alice",
            status=ProjectStatus.CONFIRMED,
        ),
        ltr_repository=_LtrRepo(
            [
                LtrRecord(
                    ltr_id="ltr-1",
                    project_id="project-1",
                    ltr_number="DL-2026-05-011",
                    status=LtrStatus.REGISTERED,
                    registered_on=date(2026, 5, 11),
                    notes=json.dumps(
                        {
                            "operator_note": json.dumps(
                                {
                                    "source": "new_project_setup_confirmation",
                                    "sample_description": "Stale LTR sample text",
                                    "test_item": "Qualification Testing",
                                },
                                sort_keys=True,
                            )
                        },
                        sort_keys=True,
                    ),
                )
            ]
        ),
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service.preview("project-1")

    assert preview.official_folder_path == (
        tmp_path
        / "workspaces"
        / "DL-2026-05-011"
        / "DL-2026-05-011 Coolpower HDF 3.40mm pin Qualification Testing"
    )


def test_manifest_disagreement_is_repairable_inconsistency(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    manifest_dir = workspace / ".connlab"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "manifest.json").write_text(
        '{"schema_version":1,"project_id":"other","official_project_folder_path":"x"}',
        encoding="utf-8",
    )
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service.preview("project-1")

    assert preview.status == "inconsistent"
    assert "Workspace manifest does not match" in preview.blockers[0]


def test_manifest_without_workspace_record_is_repairable_inconsistency(tmp_path: Path) -> None:
    template = _make_template(tmp_path / "template")
    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    official_folder = workspace / "DL-2025-11-074 Coolpower Qualification test"
    manifest_dir = workspace / ".connlab"
    official_folder.mkdir(parents=True)
    (workspace / "Source Book").mkdir()
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "project_id": "project-1",
                "official_project_folder_path": str(official_folder),
            }
        ),
        encoding="utf-8",
    )
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    preview = service.preview("project-1")

    assert preview.status == "inconsistent"
    assert "workspace index record is missing" in preview.blockers[0]


def test_failed_template_copy_cleans_temp_without_final_folder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    template = _make_template(tmp_path / "template")
    (tmp_path / "workspaces").mkdir()
    service = _service(
        tmp_path,
        settings=OfficialWorkspaceSettings(
            local_workspace_root=tmp_path / "workspaces",
            template_path=template,
            public_drive_root=None,
        ),
    )

    def fail_copytree(source: Path, target: Path) -> None:
        target.mkdir(parents=True)
        (target / "partial.txt").write_text("partial", encoding="utf-8")
        raise OSError("copy failed")

    monkeypatch.setattr(
        "backend.application.official_project_workspace_service._copytree_no_overwrite",
        fail_copytree,
    )

    with pytest.raises(OfficialWorkspaceCreateError, match="copy failed"):
        service.create("project-1")

    workspace = tmp_path / "workspaces" / "DL-2025-11-074"
    final_folder = workspace / "DL-2025-11-074 Coolpower Qualification test"
    assert not final_folder.exists()
    assert not list((workspace / ".connlab" / "tmp").glob("*"))


@dataclass
class _ProjectRepo:
    project: Project

    def get(self, project_id: str) -> Project | None:
        return self.project if self.project.project_id == project_id else None


class _WorkspaceRepo:
    def __init__(self) -> None:
        self.saved: OfficialWorkspaceRecord | None = None

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord | None:
        return self.saved if self.saved and self.saved.project_id == project_id else None

    def save(self, record: OfficialWorkspaceRecord) -> OfficialWorkspaceRecord:
        self.saved = record
        return record


class _LtrRepo:
    def __init__(self, records: list[LtrRecord] | None = None) -> None:
        self._records = records or []

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        return [record for record in self._records if record.project_id == project_id]


class _ApplicationFormRepo:
    def __init__(self, forms: list[ApplicationForm] | None = None) -> None:
        self._forms = forms or []

    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        return [form for form in self._forms if form.project_id == project_id]


def _service(
    tmp_path: Path,
    *,
    project: Project | None = None,
    repository: _WorkspaceRepo | None = None,
    ltr_repository: _LtrRepo | None = None,
    forms: list[ApplicationForm] | None = None,
    settings: OfficialWorkspaceSettings,
) -> OfficialProjectWorkspaceService:
    return OfficialProjectWorkspaceService(
        project_repository=_ProjectRepo(
            project
            or Project(
                project_id="project-1",
                project_no="DL-2025-11-074",
                product_name="Coolpower",
                requestor="Alice",
                status=ProjectStatus.CONFIRMED,
            )
        ),
        workspace_repository=repository or _WorkspaceRepo(),
        ltr_repository=ltr_repository or _LtrRepo(),
        application_form_repository=_ApplicationFormRepo(forms),
        settings=settings,
    )


def _make_template(path: Path) -> Path:
    (path / "E-mail").mkdir(parents=True)
    (path / "Submitted Material").mkdir()
    (path / "Photos").mkdir()
    (path / "Test results" / "Final Examination").mkdir(parents=True)
    return path
