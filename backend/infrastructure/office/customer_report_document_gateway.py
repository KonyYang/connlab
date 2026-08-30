"""Microsoft Word adapter for deriving E-4515 customer-report drafts."""

from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
import re
import shutil
from uuid import uuid4

from docx import Document

from backend.infrastructure.office.office_lifecycle import OfficeAutomationUnavailable


_INTERNAL_REPORT_LABEL = "LABORATORY TEST REPORT"
_CUSTOMER_REPORT_LABEL = "CUSTOMER TEST REPORT"
_REVISION_NOTE = "Note: Each new revision replaces/supersedes all previous revisions."
_END_MARKER = "*** End of Report ***"
_ACCEPTANCE_TEXT = (
    "Unless otherwise specified, assessment of conformity to requirements is based on "
    "simple acceptance."
)
_SAMPLE_SCOPE_TEXT = "The results of testing only apply to the sample"
_CUSTOMER_HEADINGS = (
    "PURPOSE",
    "CONCLUSIONS",
    "SAMPLE DESCRIPTION",
    "TEST DESCRIPTION",
    "TEST METHODS/REQUIREMENTS",
    "TEST RESULTS",
    "REVISION RECORD",
)


class CustomerReportDocumentGateway:
    """Create one customer draft without changing its internal-report source."""

    def generate_customer_report(
        self,
        *,
        source_path: Path,
        template_path: Path,
        output_path: Path,
    ) -> Path:
        source = Path(source_path)
        template = Path(template_path)
        output = Path(output_path)
        _validate_paths(source, template, output)
        source_hash = _file_hash(source)
        temporary = output.with_name(
            f".{output.stem}.{uuid4().hex}.tmp{output.suffix}"
        )
        try:
            shutil.copy2(template, temporary)
            _generate_with_word(source, temporary)
            _audit_customer_report(temporary)
            if _file_hash(source) != source_hash:
                raise ValueError("The internal report source changed during customer generation.")
            os.replace(temporary, output)
        finally:
            temporary.unlink(missing_ok=True)
        return output


def _validate_paths(source: Path, template: Path, output: Path) -> None:
    if source.suffix.lower() != ".docx" or template.suffix.lower() != ".docx":
        raise ValueError("Customer report generation requires .docx source and template files.")
    if not source.is_file():
        raise FileNotFoundError("Internal report source file is missing.")
    if not template.is_file():
        raise FileNotFoundError("E-4515 customer report template file is missing.")
    if source.resolve() == output.resolve() or template.resolve() == output.resolve():
        raise ValueError("Customer report output must not replace its source or template.")
    if not output.parent.is_dir():
        raise FileNotFoundError("Customer report output folder is missing.")
    if output.exists():
        raise FileExistsError("Customer report output already exists and will not be replaced.")


def _generate_with_word(source_path: Path, target_path: Path) -> None:
    try:
        import pythoncom  # type: ignore[import-not-found]
        import win32com.client  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - depends on Windows host
        raise OfficeAutomationUnavailable(
            "Customer report generation requires Microsoft Word automation on Windows."
        ) from exc

    pythoncom.CoInitialize()
    word = None
    source = None
    target = None
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        word.ScreenUpdating = False
        source = word.Documents.Open(
            str(source_path.resolve()),
            ReadOnly=True,
            AddToRecentFiles=False,
            ConfirmConversions=False,
        )
        if source is None:
            raise ValueError(
                "Microsoft Word did not return the internal report document."
            )
        target = word.Documents.Open(
            str(target_path.resolve()),
            ReadOnly=False,
            AddToRecentFiles=False,
            ConfirmConversions=False,
        )
        if target is None:
            raise ValueError(
                "Microsoft Word did not return the E-4515 customer template document."
            )
        try:
            _validate_document_types(source, target)
        except Exception as exc:
            raise ValueError(
                f"Customer report document validation failed: {_error_summary(exc)}"
            ) from exc
        try:
            _copy_customer_header(source, target)
        except Exception as exc:
            raise ValueError(
                f"Customer report header generation failed: {_error_summary(exc)}"
            ) from exc
        try:
            _copy_customer_body(source, target)
        except Exception as exc:
            raise ValueError(
                f"Customer report body generation failed: {_error_summary(exc)}"
            ) from exc
        target.Save()
    except Exception as exc:
        summary = " ".join(str(exc).split()) or exc.__class__.__name__
        raise ValueError(f"Unable to generate customer report: {summary[:320]}") from exc
    finally:
        if target is not None:
            try:
                target.Close(SaveChanges=False)
            except Exception:
                pass
        if source is not None:
            try:
                source.Close(SaveChanges=False)
            except Exception:
                pass
        if word is not None:
            try:
                word.Quit()
            except Exception:
                pass
        pythoncom.CoUninitialize()


def _validate_document_types(source, target) -> None:
    source_header = _first_page_header_table(source, "internal report")
    target_header = _first_page_header_table(target, "E-4515 template")
    if _INTERNAL_REPORT_LABEL not in _clean_text(source_header.Range.Text):
        raise ValueError("Selected source is not a Laboratory Test Report.")
    if _CUSTOMER_REPORT_LABEL not in _clean_text(target_header.Range.Text):
        raise ValueError("Configured E-4515 template is not a Customer Test Report.")


def _copy_customer_header(source, target) -> None:
    source_table = _first_page_header_table(source, "internal report")
    target_table = _first_page_header_table(target, "E-4515 template")
    report_number = _customer_report_number(_cell_text(source_table, 3, 1))
    _set_cell_text(target_table, 3, 1, report_number)
    _set_cell_text(target_table, 3, 2, _cell_text(source_table, 3, 2))
    _set_cell_text(target_table, 3, 3, _cell_text(source_table, 3, 3))
    _set_cell_text(target_table, 5, 1, _cell_text(source_table, 5, 2))
    _set_cell_text(target_table, 5, 2, _cell_text(source_table, 5, 3, preserve_paragraphs=True))
    _set_cell_text(target_table, 5, 3, _cell_text(source_table, 5, 4, preserve_paragraphs=True))

    if int(target.Sections.Count) < 2:
        raise ValueError("E-4515 template requires a second report section.")
    second_header = target.Sections(2).Headers(1).Range
    if int(second_header.Tables.Count) < 1:
        raise ValueError("E-4515 template second-section header table is missing.")
    _set_cell_text(second_header.Tables(1), 1, 1, f"Report No.{report_number}")


def _copy_customer_body(source, target) -> None:
    purpose, _ = _find_numbered_heading(source, 1, "PURPOSE")
    equipment, _ = _find_numbered_heading(source, 7, "EQUIPMENTS")
    if int(equipment.Start) <= int(purpose.Start):
        raise ValueError("Internal report section order is invalid.")
    core = source.Range(int(purpose.Start), int(equipment.Start))
    destination = target.Sections(1).Range.Duplicate
    destination.Collapse(0)
    core.Copy()
    destination.Paste()

    revision, _ = _find_numbered_heading(source, 8, "REVISION RECORD")
    revision_note = _find_text(source, _REVISION_NOTE)
    if int(revision_note.End) <= int(revision.Start):
        raise ValueError("Internal report revision record is incomplete.")
    revision_content = source.Range(int(revision.Start), int(revision_note.End))
    end = target.Content.Duplicate
    end.Collapse(0)
    revision_content.Copy()
    end.Paste()

    marker = target.Content.Duplicate
    marker.Collapse(0)
    marker.InsertAfter(f"\r\r\r{_END_MARKER}\r")
    marker.Font.Name = "Times New Roman"
    marker.Font.Size = 12
    marker.Font.Bold = True
    marker.Font.Italic = True
    marker.ParagraphFormat.Alignment = 1

    for index, heading in enumerate(_CUSTOMER_HEADINGS, start=1):
        number = 8 if heading == "REVISION RECORD" else index
        found, matched_text = _find_numbered_heading(target, number, heading)
        delete_prefix = target.Range(
            int(found.Start),
            int(found.Start) + len(matched_text) - len(heading),
        )
        delete_prefix.Text = ""
    _merge_customer_disclaimer(target)


def _merge_customer_disclaimer(document) -> None:
    scope = _find_text(document, _SAMPLE_SCOPE_TEXT, required=False)
    acceptance = _find_text(document, _ACCEPTANCE_TEXT, required=False)
    if scope is not None:
        sentence = scope.Duplicate
        sentence.End = sentence.Start
        for _ in range(1000):
            sentence.MoveEnd(1, 1)
            if str(sentence.Characters.Last.Text) == ".":
                break
        else:
            raise ValueError("Customer-report sample-scope sentence is incomplete.")
        sentence.Cut()
        acceptance = _find_text(document, _ACCEPTANCE_TEXT, required=False)
    if acceptance is None:
        end = document.Content.Duplicate
        end.Collapse(0)
        end.InsertAfter(_ACCEPTANCE_TEXT)
        acceptance = _find_text(document, _ACCEPTANCE_TEXT)
    if scope is not None:
        insert = acceptance.Duplicate
        insert.Collapse(0)
        insert.InsertAfter(" ")
        insert.Collapse(0)
        insert.Paste()


def _find_text(document, text: str, *, required: bool = True):
    search = document.Content.Duplicate
    finder = search.Find
    finder.ClearFormatting()
    finder.Text = text
    finder.Forward = True
    finder.Wrap = 0
    finder.MatchCase = True
    finder.MatchWholeWord = False
    if finder.Execute():
        return search
    if required:
        raise ValueError(f"Internal report is missing required content: {text}")
    return None


def _find_numbered_heading(document, number: int, heading: str):
    for candidate in (f"{number}. {heading}", f"{number}.{heading}"):
        found = _find_text(document, candidate, required=False)
        if found is not None:
            return found, candidate
    raise ValueError(
        f"Internal report is missing required content: {number}. {heading}"
    )


def _first_page_header_table(document, label: str):
    if int(document.Sections.Count) < 1:
        raise ValueError(f"{label} has no document sections.")
    tables = document.Sections(1).Headers(2).Range.Tables
    for index in range(1, int(tables.Count) + 1):
        table = tables(index)
        if int(table.Rows.Count) >= 5:
            try:
                table.Cell(5, 3)
            except Exception:
                continue
            return table
    raise ValueError(f"{label} first-page header table is missing or incompatible.")


def _cell_text(table, row: int, column: int, *, preserve_paragraphs: bool = False) -> str:
    value = str(table.Cell(row, column).Range.Text).replace("\x07", "")
    if preserve_paragraphs:
        return value.rstrip("\r")
    return _clean_text(value)


def _set_cell_text(table, row: int, column: int, value: str) -> None:
    table.Cell(row, column).Range.Text = value


def _clean_text(value: str) -> str:
    return " ".join(value.replace("\r", " ").replace("\x07", " ").split())


def _customer_report_number(value: str) -> str:
    report_number = _clean_text(value)
    if not report_number:
        raise ValueError("Internal report number is blank.")
    match = re.search(r"\s+Rev\.[A-Z]+$", report_number, flags=re.IGNORECASE)
    if match:
        base = report_number[: match.start()]
        suffix = report_number[match.start() :]
    else:
        base = report_number
        suffix = ""
    if not base.upper().endswith("-CR"):
        base = f"{base}-CR"
    return f"{base}{suffix}"


def _audit_customer_report(path: Path) -> None:
    document = Document(path)
    body_text = "\n".join(paragraph.text.strip() for paragraph in document.paragraphs)
    for heading in _CUSTOMER_HEADINGS:
        if heading not in body_text:
            raise ValueError(f"Generated customer report is missing {heading}.")
    if re.search(
        r"(?im)^\s*(?:7\s*\.\s*)?EQUIPMENTS\s*$",
        body_text,
    ) or re.search(r"\bAppendix\s+[A-Z]:", body_text, flags=re.IGNORECASE):
        raise ValueError("Generated customer report retained internal-only sections.")
    header_text = " ".join(
        cell.text
        for section in document.sections
        for table in section.first_page_header.tables
        for row in table.rows
        for cell in row.cells
    )
    if _CUSTOMER_REPORT_LABEL not in _clean_text(header_text):
        raise ValueError("Generated customer report header is invalid.")
    if "-CR" not in header_text:
        raise ValueError("Generated customer report number is missing -CR.")


def _file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _error_summary(exc: Exception) -> str:
    return (" ".join(str(exc).split()) or exc.__class__.__name__)[:240]
