from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from backend.application.section2_write_back_service import (
    Section2WriteBackCommand,
    Section2WriteBackError,
    Section2WriteBackNotFoundError,
    Section2WriteBackService,
)
from backend.domain import Project, ProjectStatus, ProjectTestPlanDraft, ProjectTestPlanDraftStatus
from backend.infrastructure.office import WordSection2FieldChange, WordSection2WriteResult


_DEFAULT_DRAFT = object()


def test_section2_write_back_service_backs_up_and_writes_fields(tmp_path: Path) -> None:
    target = tmp_path / "request.docx"
    target.write_text("fake docx", encoding="utf-8")
    office = _FakeOffice()
    service = _service(office=office)

    result = service.write_back(
        Section2WriteBackCommand(
            project_id="P1",
            draft_id="D1",
            target_application_form_path=target,
            received_date=date(2026, 5, 12),
            lab="Connector Lab",
            assigned_personnel="White",
            sample_condition="Good condition",
            operator="Alice",
        )
    )

    assert result.backup_path.is_file()
    assert result.backup_path.read_text(encoding="utf-8") == "fake docx"
    assert result.operator == "Alice"
    assert office.calls[0][0] == target
    assert office.calls[0][1]["lab"] == "Connector Lab"
    assert office.calls[0][1]["received_date"] == "2026-05-12"
    assert office.calls[0][1]["estimated_completion_date"] == "2026-05-18"
    assert result.changed_fields[0].field_key == "lab"
    assert "No explicit test duration" in result.warnings[0]


def test_section2_write_back_service_rejects_missing_target_and_non_docx(
    tmp_path: Path,
) -> None:
    service = _service()

    with pytest.raises(Section2WriteBackNotFoundError):
        service.write_back(_command(tmp_path / "missing.docx"))

    non_docx = tmp_path / "request.doc"
    non_docx.write_text("legacy", encoding="utf-8")
    with pytest.raises(Section2WriteBackError, match="Only .docx"):
        service.write_back(_command(non_docx))


def test_section2_write_back_service_maps_unknown_draft_to_not_found(tmp_path: Path) -> None:
    target = tmp_path / "request.docx"
    target.write_text("fake docx", encoding="utf-8")
    service = _service(draft=None)

    with pytest.raises(Section2WriteBackNotFoundError, match="draft not found"):
        service.write_back(_command(target))


def _command(target: Path) -> Section2WriteBackCommand:
    return Section2WriteBackCommand(
        project_id="P1",
        draft_id="D1",
        target_application_form_path=target,
        received_date=date(2026, 5, 12),
    )


def _service(
    *,
    office: _FakeOffice | None = None,
    draft: ProjectTestPlanDraft | None | object = _DEFAULT_DRAFT,
) -> Section2WriteBackService:
    draft_value = _draft() if draft is _DEFAULT_DRAFT else draft
    return Section2WriteBackService(
        project_store=_ProjectStore(),
        draft_store=_DraftStore(draft_value if isinstance(draft_value, ProjectTestPlanDraft) else None),
        office=office or _FakeOffice(),
    )


def _draft() -> ProjectTestPlanDraft:
    return ProjectTestPlanDraft(
        draft_id="D1",
        project_id="P1",
        source_document_path="C:/spec.docx",
        source_document_name="spec.docx",
        source_format=".docx",
        source_asset_id=None,
        source_case_id=None,
        source_draft_id=None,
        status=ProjectTestPlanDraftStatus.REVIEWED,
        version=1,
        payload_json=json.dumps(
            {
                "groups": [
                    {
                        "group_label": "Group 1",
                        "steps": [{"sequence": 1, "test_item": "Examination"}],
                    }
                ]
            }
        ),
        created_at="2026-05-12T00:00:00+00:00",
        updated_at="2026-05-12T00:00:00+00:00",
        reviewed_at="2026-05-12T00:00:00+00:00",
    )


class _ProjectStore:
    def get(self, project_id: str) -> Project | None:
        if project_id != "P1":
            return None
        return Project(
            project_id="P1",
            project_no="DL-2026-05-001",
            product_name="Connector",
            requestor="Alice",
            status=ProjectStatus.LTR_REGISTERED,
        )


class _DraftStore:
    def __init__(self, draft: ProjectTestPlanDraft | None) -> None:
        self._draft = draft

    def get(self, draft_id: str) -> ProjectTestPlanDraft | None:
        if self._draft is not None and draft_id == self._draft.draft_id:
            return self._draft
        return None


class _FakeOffice:
    def __init__(self) -> None:
        self.calls: list[tuple[Path, dict[str, str]]] = []

    def write_word_section2_fields(
        self,
        source_path: Path,
        fields: dict[str, str],
    ) -> WordSection2WriteResult:
        self.calls.append((source_path, fields))
        return WordSection2WriteResult(
            changed_fields=(
                WordSection2FieldChange(
                    field_key="lab",
                    label="Lab",
                    old_value="",
                    new_value=fields["lab"],
                    location="table[0].row[0].cell[1]",
                ),
            ),
            unchanged_fields=(),
        )
