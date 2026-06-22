from __future__ import annotations

from pathlib import Path

import pytest
from docx import Document

import backend.infrastructure.office.word_document_gateway as word_gateway_module
from backend.infrastructure.office.office_lifecycle import OfficeAutomationUnavailable
from backend.infrastructure.office.word_document_gateway import WordDocumentGateway


def test_application_form_plain_table_writes_same_row_and_next_row_fields(
    tmp_path: Path,
) -> None:
    target = tmp_path / "application.docx"
    _write_application_form_plain_docx(target)

    result = WordDocumentGateway().write_application_form_fields(
        target,
        {
            "project_type": "New Product Development",
            "test_item": "Qualification test",
            "applicable_specifications": "GS-12-2113 Rev3",
            "requested_by": "Ming-Peng.Cao",
            "location": "Dongguan",
            "lab": "Dongguan Lab",
        },
    )

    assert {field.field_key for field in result.changed_fields} == {
        "project_type",
        "test_item",
        "applicable_specifications",
        "requested_by",
        "location",
        "lab",
    }
    values = _read_application_form_plain_docx(target)
    assert values["Project Type"] == "New Product Development"
    assert values["Tests to be Performed"] == "Qualification test"
    assert values["Applicable Specifications"] == "GS-12-2113 Rev3"
    assert values["Requested By:"] == "Ming-Peng.Cao"
    assert values["Mfg. Site:"] == "Dongguan"
    assert values["Lab Performing the Tests:"] == "Dongguan Lab"


def test_application_form_plain_table_blocks_missing_critical_field(
    tmp_path: Path,
) -> None:
    target = tmp_path / "application.docx"
    _write_application_form_plain_docx(target, include_applicable_specifications=False)

    with pytest.raises(ValueError, match="applicable_specifications"):
        WordDocumentGateway().write_application_form_fields(
            target,
            {
                "requested_by": "Ming-Peng.Cao",
                "applicable_specifications": "GS-12-2113 Rev3",
                "lab": "Dongguan Lab",
            },
        )


def test_application_form_requires_com_does_not_fallback_to_false_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "application.docx"
    _write_application_form_plain_docx(target)

    monkeypatch.setattr(
        word_gateway_module,
        "application_form_requires_com",
        lambda path: True,
    )

    def _raise_unavailable(path: Path, fields: dict[str, str]):
        raise OfficeAutomationUnavailable("Word COM automation requires pywin32.")

    monkeypatch.setattr(
        word_gateway_module,
        "write_application_form_fields_with_com",
        _raise_unavailable,
    )

    with pytest.raises(OfficeAutomationUnavailable):
        WordDocumentGateway().write_application_form_fields(
            target,
            {"requested_by": "Ming-Peng.Cao"},
        )


def _write_application_form_plain_docx(
    path: Path,
    *,
    include_applicable_specifications: bool = True,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    document = Document()
    next_row = document.add_table(rows=2, cols=3)
    next_row.cell(0, 0).text = "Project Type"
    next_row.cell(0, 1).text = "Tests to be Performed"
    if include_applicable_specifications:
        next_row.cell(0, 2).text = "Applicable Specifications"
    same_row = document.add_table(rows=2, cols=4)
    same_row.cell(0, 0).text = "Requested By:"
    same_row.cell(0, 2).text = "Mfg. Site:"
    same_row.cell(1, 0).text = "Lab Performing the Tests:"
    document.save(path)


def _read_application_form_plain_docx(path: Path) -> dict[str, str]:
    document = Document(path)
    next_row = document.tables[0]
    same_row = document.tables[1]
    return {
        next_row.cell(0, 0).text.strip(): next_row.cell(1, 0).text.strip(),
        next_row.cell(0, 1).text.strip(): next_row.cell(1, 1).text.strip(),
        next_row.cell(0, 2).text.strip(): next_row.cell(1, 2).text.strip(),
        same_row.cell(0, 0).text.strip(): same_row.cell(0, 1).text.strip(),
        same_row.cell(0, 2).text.strip(): same_row.cell(0, 3).text.strip(),
        same_row.cell(1, 0).text.strip(): same_row.cell(1, 1).text.strip(),
    }
