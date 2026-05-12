from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from backend.application.approval_package_service import (
    ApprovalPackageCommand,
    ApprovalPackageConflictError,
    ApprovalPackageService,
)
from backend.domain import Project, ProjectStatus


def test_approval_package_preview_builds_items_and_blockers(tmp_path: Path) -> None:
    folder = tmp_path / "project"
    folder.mkdir()
    app_form = tmp_path / "request.docx"
    app_form.write_text("req", encoding="utf-8")
    test_record = tmp_path / "record.docx"
    test_record.write_text("record", encoding="utf-8")

    service = ApprovalPackageService(_ProjectRepo())
    result = service.preview(
        ApprovalPackageCommand(
            project_id="P1",
            project_folder_path=folder,
            completed_application_form_path=app_form,
            test_record_output_path=test_record,
            fee_evaluation_output_path=tmp_path / "missing.xls",
            evidence_source_paths=(tmp_path / "mail.msg",),
        )
    )

    assert result.mode == "preview"
    assert len(result.items) == 4
    assert any(item.classification == "application_form" for item in result.items)
    assert any(item.classification == "email" for item in result.items)
    assert len(result.blockers) == 2


def test_approval_package_execute_copies_files(tmp_path: Path) -> None:
    folder = tmp_path / "project"
    folder.mkdir()
    submitted = folder / "Submitted Material"
    submitted.mkdir()
    email_dir = folder / "E-mail"
    email_dir.mkdir()
    app_form = tmp_path / "request.docx"
    app_form.write_text("req", encoding="utf-8")
    test_record = tmp_path / "record.docx"
    test_record.write_text("record", encoding="utf-8")
    fee = tmp_path / "fee.xls"
    fee.write_text("fee", encoding="utf-8")
    msg = tmp_path / "mail.msg"
    msg.write_text("mail", encoding="utf-8")

    service = ApprovalPackageService(_ProjectRepo())
    result = service.execute(
        ApprovalPackageCommand(
            project_id="P1",
            project_folder_path=folder,
            completed_application_form_path=app_form,
            test_record_output_path=test_record,
            fee_evaluation_output_path=fee,
            evidence_source_paths=(msg,),
        )
    )

    assert result.mode == "execute"
    assert all(item.status in {"copied", "already_in_place"} for item in result.items)
    assert (submitted / "request.docx").exists()
    assert (submitted / "record.docx").exists()
    assert (submitted / "fee.xls").exists()
    assert (email_dir / "mail.msg").exists()


def test_approval_package_execute_rejects_blockers(tmp_path: Path) -> None:
    folder = tmp_path / "project"
    folder.mkdir()
    submitted = folder / "Submitted Material"
    submitted.mkdir()
    app_form = tmp_path / "request.docx"
    app_form.write_text("req", encoding="utf-8")
    target = submitted / "request.docx"
    target.write_text("exists", encoding="utf-8")
    test_record = tmp_path / "record.docx"
    test_record.write_text("record", encoding="utf-8")

    service = ApprovalPackageService(_ProjectRepo())
    with pytest.raises(ApprovalPackageConflictError, match="Target conflict"):
        service.execute(
            ApprovalPackageCommand(
                project_id="P1",
                project_folder_path=folder,
                completed_application_form_path=app_form,
                test_record_output_path=test_record,
            )
        )


class _ProjectRepo:
    def get(self, project_id: str) -> Project | None:
        if project_id != "P1":
            return None
        return Project(
            project_id="P1",
            project_no="DL-2026-05-001",
            product_name="Connector",
            requestor="Alice",
            status=ProjectStatus.FOLDER_CREATED,
            created_on=date(2026, 5, 12),
        )

