from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import pytest
import sys
from types import SimpleNamespace
from docx import Document

import backend.infrastructure.office.word_document_gateway as word_gateway_module
from backend.infrastructure.office.office_lifecycle import OfficeAutomationUnavailable
from backend.infrastructure.office.word_document_gateway import WordDocumentGateway


@pytest.mark.parametrize('window_pids, prior_ids, expected_ownership, should_quit', [
    ([999, 999], [100], [999], True), ([100], [100], [], False),
    ([999], [100, 999], [], False), ([999, 100], [100], [999, None], False),
])
def test_preview_owns_window_not_nonexistent_application_hwnd(tmp_path, monkeypatch, window_pids, prior_ids, expected_ownership, should_quit):
    calls = []
    options = SimpleNamespace(UpdateLinksAtOpen=True, UpdateLinksAtPrint=True, UpdateFieldsAtPrint=True)
    document = SimpleNamespace(Windows=SimpleNamespace(Item=lambda _: SimpleNamespace(Hwnd=55)), ReadOnly=True,
        Close=lambda **kwargs: calls.append(('close', kwargs)), Repaginate=lambda: calls.append(('paginate',)),
        ExportAsFixedFormat=lambda target, *_: Path(target).write_bytes(b'%PDF-isolated'))
    def opened(*args, **kwargs):
        assert word.AutomationSecurity == 3 and options.UpdateLinksAtOpen is False
        assert options.UpdateLinksAtPrint is False and options.UpdateFieldsAtPrint is False
        if args:
            assert args[1:4] == (False, True, False)
        calls.append(('open', kwargs))
        return document
    documents = SimpleNamespace(Count=0, Add=opened, Open=opened)
    word = SimpleNamespace(Documents=documents, Options=options, Quit=lambda: calls.append(('quit',)))
    client = SimpleNamespace(DispatchEx=lambda _: word, GetObject=lambda _: SimpleNamespace(ExecQuery=lambda _:
        [SimpleNamespace(ProcessId=999, ExecutablePath='C:/Office/WINWORD.EXE', CommandLine='WINWORD.EXE /Automation -Embedding')]))
    monkeypatch.setitem(sys.modules, 'pythoncom', SimpleNamespace(CoInitialize=lambda: None, CoUninitialize=lambda: calls.append(('uninit',))))
    monkeypatch.setitem(sys.modules, 'win32com', SimpleNamespace(client=client))
    monkeypatch.setitem(sys.modules, 'win32com.client', client)
    windows = iter(window_pids)
    monkeypatch.setitem(sys.modules, 'win32process', SimpleNamespace(EnumProcesses=lambda: prior_ids, GetWindowThreadProcessId=lambda _: (1, next(windows))))
    source = tmp_path / 'copy.docx'; source.write_bytes(b'isolated')
    ownership = []
    if should_quit:
        WordDocumentGateway().export_preview_pdf(source, tmp_path / 'preview.pdf', on_owned_word=ownership.append)
        assert (tmp_path / 'preview.pdf').read_bytes() == b'%PDF-isolated'
    else:
        with pytest.raises(OfficeAutomationUnavailable, match='private Word window|new Word automation server|read-only report window'):
            WordDocumentGateway().export_preview_pdf(source, tmp_path / 'preview.pdf', on_owned_word=ownership.append)
    assert ownership == expected_ownership
    assert (('quit',) in calls) == should_quit
    assert options.UpdateLinksAtOpen is True
    assert options.UpdateLinksAtPrint is True and options.UpdateFieldsAtPrint is True
    assert source.read_bytes() == b'isolated'
    if 999 in prior_ids:
        assert not any(call[0] == 'open' for call in calls)


def test_read_word_document_uses_protected_package_access(tmp_path: Path) -> None:
    protected = tmp_path / "protected.docx"
    protected.write_bytes(b"encrypted")
    readable = tmp_path / "readable.docx"
    document = Document()
    document.add_paragraph("Protected report content")
    document.save(readable)
    calls: list[Path] = []

    class _PackageGateway:
        @contextmanager
        def readable_copy(self, source: Path):
            calls.append(source)
            yield readable

    snapshot = WordDocumentGateway(
        protected_package_gateway=_PackageGateway(),
    ).read_word_document(protected)

    assert calls == [protected]
    assert snapshot.paragraphs == ["Protected report content"]


def test_application_form_plain_table_writes_same_row_and_next_row_fields(
    tmp_path: Path,
) -> None:
    target = tmp_path / "application.docx"
    _write_application_form_plain_docx(target)

    result = WordDocumentGateway().write_application_form_fields(
        target,
        {
            "project_type": "New Product Development",
            "lab": "Dongguan Lab",
            "project_leader": "BI Leader",
            "received_date": "20 Jun 2026",
            "estimated_completion_date": "30 Jun 2026",
            "sample_condition": "Acceptable",
        },
    )

    assert {field.field_key for field in result.changed_fields} == {
        "project_type",
        "lab",
        "project_leader",
        "received_date",
        "estimated_completion_date",
        "sample_condition",
    }
    values = _read_application_form_plain_docx(target)
    assert values["Project Type"] == "New Product Development"
    assert values["Lab Performing the Tests:"] == "Dongguan Lab"
    assert values["Lab Personnel Assigned:"] == "BI Leader"
    assert values["Date Lab Received Samples:"] == "20 Jun 2026"
    assert values["Estimated Completion Date:"] == "30 Jun 2026"
    assert values["Condition of Samples when Received:"] == "Acceptable"


def test_application_form_plain_table_blocks_missing_critical_field(
    tmp_path: Path,
) -> None:
    target = tmp_path / "application.docx"
    _write_application_form_plain_docx(target, include_lab=False)

    with pytest.raises(ValueError, match="lab"):
        WordDocumentGateway().write_application_form_fields(
            target,
            {
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

    def _raise_unavailable(path: Path, fields: dict[str, str], **kwargs: object):
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


def test_convert_legacy_doc_to_docx_uses_caller_output_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "legacy.doc"
    source.write_bytes(b"legacy")
    output = tmp_path / "converted.docx"

    def _fake_convert(source_path: Path, output_path: Path) -> None:
        assert source_path == source
        assert output_path == output
        output_path.write_bytes(b"converted")

    monkeypatch.setattr(
        word_gateway_module,
        "_convert_legacy_doc_to_docx_with_com",
        _fake_convert,
    )

    result = WordDocumentGateway().convert_legacy_doc_to_docx(source, output)

    assert result == output
    assert output.read_bytes() == b"converted"


def test_convert_legacy_doc_to_docx_rejects_wrong_extensions(tmp_path: Path) -> None:
    source = tmp_path / "source.docx"
    source.write_bytes(b"docx")

    with pytest.raises(ValueError, match="Only .doc files"):
        WordDocumentGateway().convert_legacy_doc_to_docx(
            source,
            tmp_path / "converted.docx",
        )

    legacy_source = tmp_path / "legacy.doc"
    legacy_source.write_bytes(b"legacy")
    with pytest.raises(ValueError, match="output must be a .docx"):
        WordDocumentGateway().convert_legacy_doc_to_docx(
            legacy_source,
            tmp_path / "converted.doc",
        )


def _write_application_form_plain_docx(
    path: Path,
    *,
    include_lab: bool = True,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    document = Document()
    next_row = document.add_table(rows=2, cols=1)
    next_row.cell(0, 0).text = "Project Type"
    same_row = document.add_table(rows=3, cols=4)
    if include_lab:
        same_row.cell(0, 0).text = "Lab Performing the Tests:"
    same_row.cell(0, 2).text = "Lab Personnel Assigned:"
    same_row.cell(1, 0).text = "Date Lab Received Samples:"
    same_row.cell(1, 2).text = "Estimated Completion Date:"
    same_row.cell(2, 0).text = "Condition of Samples when Received:"
    document.save(path)


def _read_application_form_plain_docx(path: Path) -> dict[str, str]:
    document = Document(path)
    next_row = document.tables[0]
    same_row = document.tables[1]
    return {
        next_row.cell(0, 0).text.strip(): next_row.cell(1, 0).text.strip(),
        same_row.cell(0, 0).text.strip(): same_row.cell(0, 1).text.strip(),
        same_row.cell(0, 2).text.strip(): same_row.cell(0, 3).text.strip(),
        same_row.cell(1, 0).text.strip(): same_row.cell(1, 1).text.strip(),
        same_row.cell(1, 2).text.strip(): same_row.cell(1, 3).text.strip(),
        same_row.cell(2, 0).text.strip(): same_row.cell(2, 1).text.strip(),
    }
