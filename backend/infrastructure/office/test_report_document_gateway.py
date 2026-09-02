"""E-3707_H Word adapter for initialization-report drafts."""

from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
from datetime import datetime
from decimal import Decimal
import os
from pathlib import Path
import re
from statistics import stdev
from uuid import uuid4

from docx import Document
from docx.enum.table import (
    WD_CELL_VERTICAL_ALIGNMENT,
    WD_ROW_HEIGHT_RULE,
    WD_TABLE_ALIGNMENT,
)
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph

from backend.application.confirmed_matrix_test_record_preview_service import (
    is_llcr_test_item,
)
from backend.application.test_report_draft_service import TestReportDraftData
from backend.domain.result_dataset_models import (
    LlcrSummaryRow,
    ResultDatasetRevision,
)
from backend.infrastructure.office.office_protected_document_gateway import (
    ProtectedWordPackageGateway,
)


_SAMPLE_HEADERS = ("Description", "Part #")
_METHOD_HEADERS = ("Item", "Test Method", "Condition", "Requirement")
_RESULT_HEADERS = (
    "Step",
    "Test",
    "Requirement",
    "Step Description",
    "Result",
    "Comment",
)
_EQUIPMENT_HEADERS = (
    "Item",
    "Manufacturer",
    "ID Number",
    "Last Cal.",
    "Cal. Due",
)
_REVISION_HEADERS = (
    "Revision Level",
    "Affected Pages",
    "Description",
    "Revision Date",
)
_REQUIRED_HEADINGS = (
    "1. PURPOSE",
    "2. CONCLUSIONS",
    "3. SAMPLE DESCRIPTION",
    "4. TEST DESCRIPTION",
    "5. TEST METHODS/REQUIREMENTS",
    "6. TEST RESULTS",
    "7. EQUIPMENTS",
    "8. REVISION RECORD",
    "*** End of Report ***",
)
_NUMBERED_CHAPTER_HEADING_KEYS = frozenset(_REQUIRED_HEADINGS[:-1])
_REQUIRED_FIRST_PAGE_HEADER_PLACEHOLDERS = (
    "WW-XXXX-YY-ZZZ",
    "DDMMMYYYY",
    "DDMMMYYYY-DDMMMYYYY",
    "Name(s)",
    "NAME",
    "PRODUCT NAME/TEST DESCRIPTION ",
)
_TABLE_FONT_NAME = "Arial"
_BODY_FONT_SIZE = Pt(11)
_CHAPTER_HEADING_FONT_SIZE = Pt(12)
_HEADER_FILL = "B2B2B2"
_SAMPLE_SIZE_FILL = "8DB3E2"
_PREFERRED_TEST_ITEM_WIDTH_DXA = 3024
_MIN_TEST_ITEM_WIDTH_DXA = 2500
_MIN_GROUP_WIDTH_DXA = 690
_APPENDIX_A_HEADING = "Appendix A: Statistical Summary of LLCR Measurements (Unit: mΩ)"
_APPENDIX_A_GRID_DXA = (1519, 3611, 1524, 1524, 1524, 1519)
_APPENDIX_HEADER_FILL = "DCDCDC"
_MIN_EQUIPMENT_ID_WIDTH_DXA = 1800
_MIN_EQUIPMENT_DATE_WIDTH_DXA = 1700


class TestReportDocumentGateway:
    """Populate a copied E-3707_H template through semantic document anchors."""

    __test__ = False

    def __init__(self, *, protected_package_gateway=None) -> None:
        self._protected_package_gateway = (
            protected_package_gateway or ProtectedWordPackageGateway()
        )

    def generate(
        self,
        *,
        template_path: Path,
        output_path: Path,
        report: TestReportDraftData,
    ) -> Path:
        """Write one initialization draft while retaining the approved source."""
        template = Path(template_path)
        target = Path(output_path)
        if template.suffix.lower() != ".docx":
            raise ValueError(f"Only .docx report templates are supported: {template}")
        if not template.is_file():
            raise FileNotFoundError(f"Test report template does not exist: {template}")
        if template.resolve() == target.resolve():
            raise ValueError("Approved report template cannot be used as the output path.")
        if not target.parent.is_dir():
            raise FileNotFoundError(f"Output directory does not exist: {target.parent}")
        if target.exists() and target.stat().st_size:
            raise FileExistsError(f"Output file already exists and will not be replaced: {target}")

        temporary = target.with_name(
            f".{target.stem}.{uuid4().hex}.tmp{target.suffix}"
        )
        try:
            protection_state = self._protected_package_gateway.stage_editable_copy(
                template,
                temporary,
            )
            document = Document(temporary)
            anchors = _validate_template_contract(document)
            _fill_headers(document, report)
            _fill_narrative(document, report)
            _fill_sample_table(anchors.sample_table, report)
            _fill_test_description_table(anchors.description_table, report)
            _fill_method_table(anchors.method_table, report)
            _fill_result_blocks(
                document,
                anchors.result_heading,
                anchors.result_table,
                report,
            )
            _insert_page_break_before_heading(document, "7. EQUIPMENTS")
            _fill_revision_table(anchors.revision_table, report)
            _set_document_table_font(document, _TABLE_FONT_NAME)
            equipment = _find_table(document, _EQUIPMENT_HEADERS, "Equipment table")
            _set_equipment_table_geometry(equipment)
            _apply_report_body_format(document)
            document.save(temporary)
            _audit_generated_document(temporary, report)
            self._protected_package_gateway.restore_password_protection(
                temporary,
                protection_state,
            )
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
        return target

    def synchronize_llcr_results(
        self,
        *,
        source_path: Path,
        output_path: Path,
        dataset: ResultDatasetRevision,
    ) -> Path:
        """Copy one report revision and update only uniquely matched LLCR cells."""
        source = Path(source_path)
        target = Path(output_path)
        if source.suffix.lower() != ".docx" or not source.is_file():
            raise FileNotFoundError(f"Internal report draft does not exist: {source}")
        if target.suffix.lower() != ".docx":
            raise ValueError("Internal report draft output must be .docx.")
        if source.resolve() == target.resolve() or target.exists():
            raise FileExistsError("Report synchronization requires a new output file.")
        if not target.parent.is_dir():
            raise FileNotFoundError(f"Output directory does not exist: {target.parent}")
        if dataset.dataset_type != "llcr" or dataset.validation_status != "confirmed":
            raise ValueError("A confirmed LLCR ResultDataset revision is required.")

        temporary = target.with_name(f".{target.stem}.{uuid4().hex}.tmp{target.suffix}")
        try:
            protection_state = self._protected_package_gateway.stage_editable_copy(
                source,
                temporary,
            )
            document = Document(temporary)
            result_tables = _result_tables_by_group(document)
            updates = []
            for entry in dataset.payload.entries:
                group_key = _report_group_key(entry.group_label)
                tables = result_tables.get(group_key, ())
                matches = []
                for table in tables:
                    for row in table.rows[1:]:
                        if len(row.cells) < 6:
                            continue
                        if (
                            _normalized(row.cells[0].text) == _normalized(entry.matrix_step_token)
                            and is_llcr_test_item(row.cells[1].text)
                            and _normalized(row.cells[2].text) == _normalized(entry.requirement)
                        ):
                            matches.append(row)
                if len(matches) != 1:
                    raise ValueError(
                        "Unable to uniquely locate the LLCR report target for "
                        f"Group {entry.group_label} Step {entry.matrix_step_token}."
                    )
                row = matches[0]
                expected_result = _llcr_report_result(entry)
                expected_comment = (entry.confirmed_outcome or "").title()
                if (
                    _normalized(row.cells[4].text) != _normalized(expected_result)
                    or _normalized(row.cells[5].text) != _normalized(expected_comment)
                ):
                    updates.append((row, expected_result, expected_comment))
            for row, expected_result, expected_comment in updates:
                _set_cell_text(row.cells[4], expected_result)
                _set_cell_text(row.cells[5], expected_comment)
            summary_rows = _llcr_summary_rows(dataset)
            appendix_changed = not _appendix_a_is_current(document, summary_rows)
            if appendix_changed:
                _replace_appendix_a(document, summary_rows)
            format_changed = _apply_report_body_format(document)
            if updates or appendix_changed or format_changed:
                document.save(temporary)
            _audit_llcr_sync(temporary, dataset)
            self._protected_package_gateway.restore_password_protection(
                temporary,
                protection_state,
            )
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
        return target

    def synchronize_equipment_list(
        self,
        *,
        source_path: Path,
        output_path: Path,
        rows: tuple[object, ...],
    ) -> Path:
        """Copy one report revision and replace only the Equipment table body."""
        source = Path(source_path)
        target = Path(output_path)
        if source.suffix.lower() != ".docx" or not source.is_file():
            raise FileNotFoundError(f"Internal report draft does not exist: {source}")
        if target.suffix.lower() != ".docx":
            raise ValueError("Internal report draft output must be .docx.")
        if source.resolve() == target.resolve() or target.exists():
            raise FileExistsError("Report synchronization requires a new output file.")
        if not target.parent.is_dir():
            raise FileNotFoundError(f"Output directory does not exist: {target.parent}")
        if not rows:
            raise ValueError("Equipment List requires at least one row.")

        expected = tuple(
            (
                str(row.item).strip(),
                str(row.manufacturer).strip(),
                str(row.id_number).strip(),
                str(row.last_calibration).strip(),
                str(row.calibration_due).strip(),
            )
            for row in rows
        )
        temporary = target.with_name(f".{target.stem}.{uuid4().hex}.tmp{target.suffix}")
        try:
            protection_state = self._protected_package_gateway.stage_editable_copy(
                source,
                temporary,
            )
            document = Document(temporary)
            equipment = _find_table(document, _EQUIPMENT_HEADERS, "Equipment table")
            actual = tuple(
                tuple(cell.text.strip() for cell in row.cells[:5])
                for row in equipment.rows[1:]
            )
            body_before = document.element.body.xml
            if actual != expected:
                _replace_equipment_table_rows(equipment, expected)
            _set_equipment_table_geometry(equipment)
            _apply_report_body_format(document)
            if actual != expected or document.element.body.xml != body_before:
                document.save(temporary)
            _audit_equipment_sync(temporary, expected)
            self._protected_package_gateway.restore_password_protection(
                temporary,
                protection_state,
            )
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
        return target


class _TemplateAnchors:
    def __init__(
        self,
        *,
        sample_table: Table,
        description_table: Table,
        method_table: Table,
        result_heading: Paragraph,
        result_table: Table,
        revision_table: Table,
    ) -> None:
        self.sample_table = sample_table
        self.description_table = description_table
        self.method_table = method_table
        self.result_heading = result_heading
        self.result_table = result_table
        self.revision_table = revision_table


def _validate_template_contract(document, *, populated: bool = False) -> _TemplateAnchors:
    paragraphs = {_heading_key(paragraph.text): paragraph for paragraph in document.paragraphs}
    for heading in _REQUIRED_HEADINGS:
        if _heading_key(heading) not in paragraphs:
            raise ValueError(f"E-3707_H template heading is missing: {heading}")

    sample = _find_table(document, _SAMPLE_HEADERS, "Sample Description table")
    description = _find_table(document, ("Test Items",), "Test Description table")
    methods = _find_table(document, _METHOD_HEADERS, "Test Methods/Requirements table")
    results = _find_table(document, _RESULT_HEADERS, "Test Results table")
    _find_table(document, _EQUIPMENT_HEADERS, "Equipment table")
    revision = _find_table(document, _REVISION_HEADERS, "Revision Record table")
    result_heading = paragraphs.get(_heading_key("Group # Test Results"))
    if result_heading is None and populated:
        result_heading = next(
            (
                paragraph
                for paragraph in document.paragraphs
                if re.fullmatch(r"Group\s+.+\s+Test Results", _normalized(paragraph.text))
            ),
            None,
        )
    if result_heading is None:
        raise ValueError("E-3707_H template result-group heading is missing.")
    if not document.sections or not any(
        section.header.tables for section in document.sections
    ):
        raise ValueError("E-3707_H template report header is missing.")
    if not populated:
        first_page_text = "".join(
            _header_text_nodes(document.sections[0].first_page_header)
        )
        for placeholder in _REQUIRED_FIRST_PAGE_HEADER_PLACEHOLDERS:
            if placeholder not in first_page_text:
                raise ValueError(
                    "E-3707_H first-page header placeholder is missing: "
                    f"{placeholder}"
                )
    return _TemplateAnchors(
        sample_table=sample,
        description_table=description,
        method_table=methods,
        result_heading=result_heading,
        result_table=results,
        revision_table=revision,
    )


def _find_table(document, expected_headers: tuple[str, ...], label: str) -> Table:
    expected = tuple(_normalized(value) for value in expected_headers)
    for table in document.tables:
        if not table.rows:
            continue
        actual = tuple(_normalized(cell.text) for cell in table.rows[0].cells)
        if actual[: len(expected)] == expected:
            return table
    raise ValueError(f"E-3707_H {label} does not match the approved table contract.")


def _replace_equipment_table_rows(
    table: Table,
    rows: tuple[tuple[str, str, str, str, str], ...],
) -> None:
    template_row = deepcopy(table.rows[1]._tr) if len(table.rows) > 1 else None
    for row in list(table.rows[1:]):
        table._tbl.remove(row._tr)
    for values in rows:
        if template_row is not None:
            table._tbl.append(deepcopy(template_row))
            target_row = table.rows[-1]
        else:
            target_row = table.add_row()
        for cell, value in zip(target_row.cells[:5], values, strict=True):
            _set_cell_text(cell, value)
    _set_table_font(table, _TABLE_FONT_NAME)


def _set_equipment_table_geometry(table: Table) -> None:
    total_width = _table_width_dxa(table)
    id_width = max(round(total_width * 0.18), _MIN_EQUIPMENT_ID_WIDTH_DXA)
    date_width = max(
        round(total_width * 0.16),
        _MIN_EQUIPMENT_DATE_WIDTH_DXA,
    )
    remaining = total_width - id_width - 2 * date_width
    if remaining < 2:
        raise ValueError("E-3707_H Equipment table is too narrow for its columns.")
    item_width = round(remaining * 0.52)
    widths = (
        item_width,
        remaining - item_width,
        id_width,
        date_width,
        date_width,
    )
    grid_columns = table._tbl.tblGrid.gridCol_lst
    if len(grid_columns) != len(widths):
        raise ValueError("E-3707_H Equipment table grid is inconsistent.")
    table.autofit = False
    table_width = table._tbl.tblPr.find(qn("w:tblW"))
    if table_width is None:
        table_width = OxmlElement("w:tblW")
        table._tbl.tblPr.insert(0, table_width)
    table_width.set(qn("w:type"), "dxa")
    table_width.set(qn("w:w"), str(total_width))
    layout = table._tbl.tblPr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        table._tbl.tblPr.append(layout)
    layout.set(qn("w:type"), "fixed")
    for column, width in zip(grid_columns, widths, strict=True):
        column.set(qn("w:w"), str(width))
    for row in table.rows:
        for cell, width in zip(row.cells[:5], widths, strict=True):
            cell_width = cell._tc.get_or_add_tcPr().get_or_add_tcW()
            cell_width.set(qn("w:type"), "dxa")
            cell_width.set(qn("w:w"), str(width))
        id_properties = row.cells[2]._tc.get_or_add_tcPr()
        if id_properties.find(qn("w:noWrap")) is None:
            id_properties.append(OxmlElement("w:noWrap"))


def _set_table_font(table: Table, font_name: str) -> None:
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.name = font_name
                    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), font_name)


def _audit_equipment_sync(
    path: Path,
    expected: tuple[tuple[str, str, str, str, str], ...],
) -> None:
    document = Document(path)
    equipment = _find_table(document, _EQUIPMENT_HEADERS, "Equipment table")
    actual = tuple(
        tuple(cell.text.strip() for cell in row.cells[:5])
        for row in equipment.rows[1:]
    )
    if actual != expected:
        raise ValueError("Generated Equipment List does not match the confirmed preview.")
    id_width = int(equipment._tbl.tblGrid.gridCol_lst[2].get(qn("w:w"), "0"))
    if id_width < _MIN_EQUIPMENT_ID_WIDTH_DXA or any(
        row.cells[2]._tc.get_or_add_tcPr().find(qn("w:noWrap")) is None
        for row in equipment.rows
    ):
        raise ValueError("Generated Equipment List ID Number column may wrap lab IDs.")
    _audit_report_body_format(document)


def _fill_headers(document, report: TestReportDraftData) -> None:
    report_number = report.report_number
    project_leader = report.project_leader or "[To be assigned]"
    replacements = {
        "DDMMMYYYY-DDMMMYYYY": _display_test_date_range(
            report.start_test_date,
            report.finish_test_date,
        ),
        "WW-XXXX-YY-ZZZ": report_number,
        "XX-YY-ZZZ": report_number,
        "DDMMMYYYY": report.generated_on.strftime("%d/%b/%Y"),
        "Name(s)": project_leader,
        "NAME": report.requestor or "[To be confirmed]",
        "PRODUCT NAME/TEST DESCRIPTION ": (
            f"{report.product_name} {report.test_description}"
        ),
        "Name": "Gentle Zeng",
        "(s)": "",
    }
    for section in document.sections:
        for header in (
            section.header,
            section.first_page_header,
        ):
            seen_cells: set[object] = set()
            for table in header.tables:
                for row in table.rows:
                    for cell in row.cells:
                        cell_identity = cell._tc
                        if cell_identity in seen_cells:
                            continue
                        seen_cells.add(cell_identity)
                        updated = _replace_header_text(cell.text, replacements)
                        if updated != cell.text:
                            _set_cell_text(cell, updated)
            for text_node in header._element.xpath(".//w:t"):
                value = text_node.text or ""
                text_node.text = _replace_header_text(value, replacements)


def _replace_header_text(value: str, replacements: dict[str, str]) -> str:
    if value in replacements:
        return replacements[value]
    updated = value
    for placeholder in (
        "DDMMMYYYY-DDMMMYYYY",
        "WW-XXXX-YY-ZZZ",
        "XX-YY-ZZZ",
        "DDMMMYYYY",
    ):
        updated = updated.replace(placeholder, replacements[placeholder])
    return updated


def _fill_narrative(document, report: TestReportDraftData) -> None:
    received_date = _display_date(report.received_samples_date)
    replacements = {
        "[TEST DESCRIPTION]": report.test_description,
        "[PRODUCT NAME]": report.product_name,
        "[GS-XX-XXXX (Rev.X, DATE)]": report.applicable_specification,
        "[RECEIVED SAMPLES DATE]": received_date,
        "DDMMMYYYY": received_date,
    }
    purpose_heading_seen = False
    conclusion_heading_seen = False
    for paragraph in document.paragraphs:
        normalized = _heading_key(paragraph.text)
        if normalized == _heading_key("1. PURPOSE"):
            purpose_heading_seen = True
            continue
        if normalized == _heading_key("2. CONCLUSIONS"):
            conclusion_heading_seen = True
            continue
        if purpose_heading_seen and normalized:
            _set_paragraph_text(
                paragraph,
                (
                    f"This report summarizes the {report.test_description} conducted on "
                    f"{report.product_name} to assess the conformance to AFCI product "
                    f"specification {report.applicable_specification}."
                ),
            )
            purpose_heading_seen = False
            continue
        if conclusion_heading_seen and normalized:
            _set_paragraph_text(
                paragraph,
                "DRAFT — Conclusions will be completed after testing and review.",
            )
            conclusion_heading_seen = False
            continue
        updated = paragraph.text
        for placeholder, value in replacements.items():
            updated = updated.replace(placeholder, value or "[To be confirmed]")
        if updated != paragraph.text:
            _set_paragraph_text(paragraph, updated)


def _fill_sample_table(table: Table, report: TestReportDraftData) -> None:
    sample_rows = report.sample_rows
    if not sample_rows:
        _resize_rows(table, 2)
        fallback_values = [
            report.product_name,
            report.description_part_number,
            "",
            "",
            "",
            "",
            "",
        ]
        for cell, value in zip(
            table.rows[1].cells,
            fallback_values,
            strict=False,
        ):
            _set_cell_text(cell, value)
        return

    _resize_rows(table, 1 + len(sample_rows))
    for table_row, sample in zip(table.rows[1:], sample_rows, strict=True):
        values = [
            sample.product_name,
            sample.part_number,
            sample.lot_or_traceability,
            sample.material,
            sample.plating,
            sample.lubricant,
            sample.housing_material,
        ]
        for cell, value in zip(table_row.cells, values, strict=False):
            _set_cell_text(cell, value)


def _fill_test_description_table(table: Table, report: TestReportDraftData) -> None:
    groups = report.groups
    table_width_dxa = _table_width_dxa(table)
    item_names: list[str] = []
    for group in groups:
        for step in group.steps:
            if step.test_item not in item_names:
                item_names.append(step.test_item)

    target_columns = len(groups) + 1
    _resize_columns(table, target_columns)
    _resize_rows(table, 2 + len(item_names) + 1)
    _set_cell_text(table.cell(0, 0), "Test Items")
    _set_cell_text(table.cell(1, 0), "")
    for column_index, group in enumerate(groups, start=1):
        _set_cell_text(
            table.cell(0, column_index),
            "Test Sequence" if column_index == 1 else "",
        )
        _set_cell_text(
            table.cell(1, column_index),
            _test_sequence_group_label(group.group_label),
        )
    if len(groups) > 1:
        table.cell(0, 1).merge(table.cell(0, len(groups)))
    table.cell(0, 0).merge(table.cell(1, 0))
    _set_cell_text(table.cell(0, 0), "Test Items")
    _set_cell_text(table.cell(0, 1), "Test Sequence")
    for cell in table.rows[0].cells:
        _set_cell_fill(cell, _HEADER_FILL)
    for cell in table.rows[1].cells[1:]:
        _set_cell_fill(cell, _HEADER_FILL)

    for row_index, item_name in enumerate(item_names, start=2):
        _set_cell_text(table.cell(row_index, 0), item_name)
        for column_index, group in enumerate(groups, start=1):
            tokens = [
                step.raw_token
                for step in group.steps
                if step.test_item == item_name
            ]
            _set_cell_text(table.cell(row_index, column_index), ",".join(tokens))
    final_row = table.rows[-1]
    _set_cell_text(final_row.cells[0], "Samples Size(sets)")
    for column_index, group in enumerate(groups, start=1):
        _set_cell_text(final_row.cells[column_index], group.sample_quantity_expression)
    for cell in final_row.cells:
        _set_cell_fill(cell, _SAMPLE_SIZE_FILL)
    _set_description_widths(table, len(groups), table_width_dxa)


def _fill_method_table(table: Table, report: TestReportDraftData) -> None:
    methods: OrderedDict[tuple[str, str, str], list[str]] = OrderedDict()
    for group in report.groups:
        for step in group.steps:
            key = (step.test_item, step.method, step.condition)
            requirements = methods.setdefault(key, [])
            if step.requirement and step.requirement not in requirements:
                requirements.append(step.requirement)
    _resize_rows(table, 1 + len(methods))
    for row_index, ((item, method, condition), requirements) in enumerate(
        methods.items(),
        start=1,
    ):
        values = (item, method, condition, "; ".join(requirements))
        for cell, value in zip(table.rows[row_index].cells, values, strict=True):
            _set_cell_text(cell, value)


def _fill_result_blocks(
    document,
    template_heading: Paragraph,
    template_table: Table,
    report: TestReportDraftData,
) -> None:
    heading_xml = deepcopy(template_heading._p)
    table_xml = deepcopy(template_table._tbl)
    _fill_result_block(template_heading, template_table, report.groups[0])
    cursor = template_table._tbl
    for group in report.groups[1:]:
        cloned_heading_xml = deepcopy(heading_xml)
        cursor.addnext(cloned_heading_xml)
        cursor = cloned_heading_xml
        cloned_table_xml = deepcopy(table_xml)
        cursor.addnext(cloned_table_xml)
        cursor = cloned_table_xml
        _fill_result_block(
            Paragraph(cloned_heading_xml, document._body),
            Table(cloned_table_xml, document._body),
            group,
        )


def _fill_result_block(heading: Paragraph, table: Table, group) -> None:
    group_label = _test_sequence_group_label(group.group_label)
    _set_paragraph_text(heading, f"Group {group_label} Test Results")
    _resize_rows(table, 1 + len(group.steps))
    llcr_indexes = tuple(
        index
        for index, candidate in enumerate(group.steps)
        if is_llcr_test_item(candidate.test_item)
    )
    for step_index, step in enumerate(group.steps):
        row_index = step_index + 1
        description = _step_description(
            group.steps,
            step_index,
            llcr_indexes,
        )
        display_requirement = _display_requirement(
            step.requirement,
            step_index=step_index,
            llcr_indexes=llcr_indexes,
        )
        result_requirement = _stage_result_requirement(
            display_requirement,
            step_index=step_index,
            llcr_indexes=llcr_indexes,
        )
        values = (
            step.raw_token,
            step.test_item,
            display_requirement,
            description,
            _default_result(result_requirement),
            "Pass",
        )
        for cell, value in zip(table.rows[row_index].cells, values, strict=True):
            _set_cell_text(cell, value)


def _fill_revision_table(table: Table, report: TestReportDraftData) -> None:
    _resize_rows(table, max(2, len(table.rows)))
    values = (
        "A",
        "All",
        "Initial draft - not released",
        report.generated_on.strftime("%d/%b/%Y"),
    )
    for cell, value in zip(table.rows[1].cells, values, strict=True):
        _set_cell_text(cell, value)


def _result_tables_by_group(document) -> dict[str, tuple[Table, ...]]:
    collected: dict[str, list[Table]] = {}
    current_group: str | None = None
    for child in document.element.body.iterchildren():
        if child.tag == qn("w:p"):
            text = Paragraph(child, document._body).text.strip()
            match = re.fullmatch(r"Group\s+(.+?)\s+Test Results", text, re.IGNORECASE)
            current_group = _report_group_key(match.group(1)) if match else current_group
            continue
        if child.tag != qn("w:tbl") or current_group is None:
            continue
        table = Table(child, document._body)
        if not table.rows:
            continue
        headers = tuple(_normalized(cell.text) for cell in table.rows[0].cells)
        if headers[: len(_RESULT_HEADERS)] == tuple(
            _normalized(value) for value in _RESULT_HEADERS
        ):
            collected.setdefault(current_group, []).append(table)
            current_group = None
    return {key: tuple(value) for key, value in collected.items()}


def _report_group_key(value: str) -> str:
    return re.sub(r"^group\s+", "", value.strip(), flags=re.IGNORECASE).casefold()


def _llcr_report_result(entry) -> str:
    value = f"{entry.summary_max:.3f}"
    return f"Initial ≤{value}mΩ" if entry.stage == "initial" else f"∆R ≤{value}mΩ"


def _audit_llcr_sync(path: Path, dataset: ResultDatasetRevision) -> None:
    document = Document(path)
    result_tables = _result_tables_by_group(document)
    for entry in dataset.payload.entries:
        expected = _llcr_report_result(entry)
        matches = [
            row
            for table in result_tables.get(_report_group_key(entry.group_label), ())
            for row in table.rows[1:]
            if len(row.cells) >= 6
            and _normalized(row.cells[0].text) == _normalized(entry.matrix_step_token)
            and is_llcr_test_item(row.cells[1].text)
            and row.cells[4].text == expected
            and row.cells[5].text == (entry.confirmed_outcome or "").title()
        ]
        if len(matches) != 1:
            raise ValueError(
                "Generated report failed LLCR synchronization audit for "
                f"Group {entry.group_label} Step {entry.matrix_step_token}."
            )
    summary_rows = _llcr_summary_rows(dataset)
    if not _appendix_a_is_current(document, summary_rows):
        raise ValueError("Generated report failed Appendix A synchronization audit.")
    _audit_report_body_format(document)


def _llcr_summary_rows(dataset: ResultDatasetRevision) -> tuple[LlcrSummaryRow, ...]:
    if dataset.payload.summary_rows:
        return dataset.payload.summary_rows
    group_order: list[str] = []
    rows: list[LlcrSummaryRow] = []
    for source_row, entry in enumerate(dataset.payload.entries, start=3):
        group_key = _report_group_key(entry.group_label)
        if group_key not in group_order:
            group_order.append(group_key)
        values = [measurement.value for measurement in entry.measurements]
        rows.append(
            LlcrSummaryRow(
                group_label=entry.group_label,
                stage_label=entry.stage_label,
                summary_min=entry.summary_min,
                summary_max=entry.summary_max,
                summary_average=entry.summary_average,
                summary_stdev=stdev(values) if len(values) > 1 else Decimal("0"),
                source_row=source_row,
                fill_color=(
                    "FFFFCC"
                    if group_order.index(group_key) % 2 == 1
                    else None
                ),
            )
        )
    return tuple(rows)


def _appendix_a_is_current(
    document,
    rows: tuple[LlcrSummaryRow, ...],
) -> bool:
    heading, table = _appendix_a_region(document)
    if heading is None or table is None:
        return False
    if heading.text != _APPENDIX_A_HEADING:
        return False
    previous = heading._p.getprevious()
    if previous is None or not previous.xpath('.//w:br[@w:type="page"]'):
        return False
    if any(
        run.font.name != _TABLE_FONT_NAME
        or run.font.size != _CHAPTER_HEADING_FONT_SIZE
        or run.bold is not True
        or run.underline is not True
        for run in heading.runs
    ):
        return False
    expected = _appendix_a_values(rows)
    actual = tuple(tuple(cell.text for cell in row.cells) for row in table.rows)
    if actual != expected:
        return False
    expected_grid = _appendix_grid_dxa(document)
    if len(table._tbl.tblGrid.gridCol_lst) != len(expected_grid):
        return False
    if tuple(
        int(column.get(qn("w:w"), "0"))
        for column in table._tbl.tblGrid.gridCol_lst
    ) != expected_grid:
        return False
    if any(
        row._tr.get_or_add_trPr().find(qn("w:tblHeader")) is None
        for row in table.rows[:2]
    ):
        return False
    if any(
        run.font.size != _BODY_FONT_SIZE
        for row in table.rows
        for cell in row.cells
        for paragraph in cell.paragraphs
        for run in paragraph.runs
        if run.text
    ):
        return False
    for row_index, summary in enumerate(rows, start=2):
        expected_fill = summary.fill_color or "FFFFFF"
        if any(
            _cell_fill_value(table.cell(row_index, column)) != expected_fill
            for column in range(2, 6)
        ):
            return False
        max_runs = table.cell(row_index, 3).paragraphs[0].runs
        if not max_runs or any(run.bold is not True for run in max_runs):
            return False
    return True


def _appendix_a_region(document) -> tuple[Paragraph | None, Table | None]:
    headings = [
        paragraph
        for paragraph in document.paragraphs
        if re.match(r"^Appendix\s+A\s*:", paragraph.text.strip(), re.IGNORECASE)
    ]
    if len(headings) > 1:
        raise ValueError("Internal report contains more than one Appendix A heading.")
    if not headings:
        return None, None
    heading = headings[0]
    table = None
    for sibling in heading._p.itersiblings():
        if sibling.tag == qn("w:tbl"):
            table = Table(sibling, document._body)
            break
        if sibling.tag == qn("w:p"):
            text = Paragraph(sibling, document._body).text.strip()
            if text and (
                re.match(r"^Appendix\s+[B-Z]\s*:", text, re.IGNORECASE)
                or _normalized(text) == _normalized("*** End of Report ***")
            ):
                break
    return heading, table


def _replace_appendix_a(
    document,
    rows: tuple[LlcrSummaryRow, ...],
) -> None:
    if not rows:
        raise ValueError("Appendix A requires at least one LLCR Summary row.")
    old_heading, old_table = _appendix_a_region(document)
    if old_heading is not None:
        anchor = old_heading._p
    else:
        anchor = next(
            (
                paragraph._p
                for paragraph in document.paragraphs
                if re.match(
                    r"^Appendix\s+[B-Z]\s*:",
                    paragraph.text.strip(),
                    re.IGNORECASE,
                )
            ),
            None,
        )
        if anchor is None:
            anchor = next(
                (
                    paragraph._p
                    for paragraph in document.paragraphs
                    if _normalized(paragraph.text)
                    == _normalized("*** End of Report ***")
                ),
                None,
            )
    if anchor is None:
        raise ValueError("Internal report End of Report anchor is missing.")

    preceding_page_break = (
        old_heading is not None
        and old_heading._p.getprevious() is not None
        and bool(old_heading._p.getprevious().xpath('.//w:br[@w:type="page"]'))
    )
    heading = document.add_paragraph()
    heading.paragraph_format.space_after = Pt(4)
    run = heading.add_run(_APPENDIX_A_HEADING)
    run.font.name = _TABLE_FONT_NAME
    run.font.size = _CHAPTER_HEADING_FONT_SIZE
    run.bold = True
    run.underline = True
    _set_run_font_family(run, _TABLE_FONT_NAME)
    table = _build_appendix_a_table(document, rows)
    if not preceding_page_break:
        anchor.addprevious(_page_break_paragraph())
    anchor.addprevious(heading._p)
    anchor.addprevious(table._tbl)

    if old_table is not None:
        old_table._tbl.getparent().remove(old_table._tbl)
    if old_heading is not None:
        old_heading._p.getparent().remove(old_heading._p)


def _build_appendix_a_table(
    document,
    rows: tuple[LlcrSummaryRow, ...],
) -> Table:
    table = document.add_table(rows=2 + len(rows), cols=6)
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    _set_appendix_table_geometry(table, _appendix_grid_dxa(document))

    table.cell(0, 0).merge(table.cell(1, 1))
    table.cell(0, 2).merge(table.cell(0, 5))
    _write_appendix_cell(table.cell(0, 0), "Test Step", bold=True, fill=_APPENDIX_HEADER_FILL)
    _write_appendix_cell(table.cell(0, 2), "Statistics", bold=True, fill=_APPENDIX_HEADER_FILL)
    for column, label in enumerate(("Min", "Max", "Avg", "Stdev"), start=2):
        _write_appendix_cell(table.cell(1, column), label, bold=True, fill=_APPENDIX_HEADER_FILL)

    for row_index, summary in enumerate(rows, start=2):
        _write_appendix_cell(
            table.cell(row_index, 0),
            f"Group {_report_group_key(summary.group_label)}",
            bold=True,
            fill=_APPENDIX_HEADER_FILL,
        )
        _write_appendix_cell(
            table.cell(row_index, 1),
            _appendix_stage_label(summary.stage_label),
            bold=True,
            fill=_APPENDIX_HEADER_FILL,
        )
        fill = summary.fill_color or "FFFFFF"
        for column, value in enumerate(
            (
                summary.summary_min,
                summary.summary_max,
                summary.summary_average,
                summary.summary_stdev,
            ),
            start=2,
        ):
            _write_appendix_cell(
                table.cell(row_index, column),
                f"{value:.3f}",
                bold=column == 3,
                fill=fill,
            )

    group_starts: dict[str, int] = {}
    group_ends: dict[str, int] = {}
    for row_index, summary in enumerate(rows, start=2):
        key = _report_group_key(summary.group_label)
        group_starts.setdefault(key, row_index)
        group_ends[key] = row_index
    for key, start in group_starts.items():
        end = group_ends[key]
        if end > start:
            merged = table.cell(start, 0).merge(table.cell(end, 0))
            _write_appendix_cell(
                merged,
                f"Group {key}",
                bold=True,
                fill=_APPENDIX_HEADER_FILL,
            )

    for row_index, row in enumerate(table.rows):
        row.height = Pt(15.15)
        row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
        properties = row._tr.get_or_add_trPr()
        cant_split = properties.find(qn("w:cantSplit"))
        if cant_split is None:
            properties.append(OxmlElement("w:cantSplit"))
        if row_index < 2 and properties.find(qn("w:tblHeader")) is None:
            properties.append(OxmlElement("w:tblHeader"))
    return table


def _appendix_a_values(
    rows: tuple[LlcrSummaryRow, ...],
) -> tuple[tuple[str, ...], ...]:
    values = [
        ("Test Step", "Test Step", "Statistics", "Statistics", "Statistics", "Statistics"),
        ("Test Step", "Test Step", "Min", "Max", "Avg", "Stdev"),
    ]
    for summary in rows:
        values.append(
            (
                f"Group {_report_group_key(summary.group_label)}",
                _appendix_stage_label(summary.stage_label),
                f"{summary.summary_min:.3f}",
                f"{summary.summary_max:.3f}",
                f"{summary.summary_average:.3f}",
                f"{summary.summary_stdev:.3f}",
            )
        )
    return tuple(values)


def _appendix_stage_label(value: str) -> str:
    label = " ".join(value.strip().split())
    if re.search(r"[Δ∆]\s*R", label, re.IGNORECASE):
        return label.replace("Δ", "∆")
    if re.fullmatch(r"Final(?:\s+LLCR)?", label, re.IGNORECASE):
        return "Final ∆R"
    if not label.casefold().startswith("initial"):
        return f"∆R {label}"
    return label


def _appendix_grid_dxa(document) -> tuple[int, ...]:
    usable_width = min(
        int((section.page_width - section.left_margin - section.right_margin) / 635)
        for section in document.sections
    )
    reference_width = sum(_APPENDIX_A_GRID_DXA)
    if usable_width >= reference_width:
        return _APPENDIX_A_GRID_DXA
    scaled = [
        max(1, round(width * usable_width / reference_width))
        for width in _APPENDIX_A_GRID_DXA
    ]
    scaled[-1] += usable_width - sum(scaled)
    return tuple(scaled)


def _set_appendix_table_geometry(table: Table, widths: tuple[int, ...]) -> None:
    properties = table._tbl.tblPr
    table_width = properties.find(qn("w:tblW"))
    if table_width is None:
        table_width = OxmlElement("w:tblW")
        properties.insert(0, table_width)
    table_width.set(qn("w:type"), "dxa")
    table_width.set(qn("w:w"), str(sum(widths)))
    layout = properties.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        properties.append(layout)
    layout.set(qn("w:type"), "fixed")
    for column, width in zip(
        table._tbl.tblGrid.gridCol_lst,
        widths,
        strict=True,
    ):
        column.set(qn("w:w"), str(width))
    for row in table.rows:
        for cell, width in zip(row.cells, widths, strict=True):
            tc_width = cell._tc.get_or_add_tcPr().get_or_add_tcW()
            tc_width.set(qn("w:type"), "dxa")
            tc_width.set(qn("w:w"), str(width))


def _write_appendix_cell(
    cell: _Cell,
    value: str,
    *,
    bold: bool,
    fill: str,
) -> None:
    _set_cell_text(cell, value)
    _set_cell_fill(cell, fill)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    _set_cell_borders(cell)
    for paragraph in cell.paragraphs:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(0)
        for run in paragraph.runs:
            run.font.name = _TABLE_FONT_NAME
            run.font.size = _BODY_FONT_SIZE
            run.bold = bold
            _set_run_font_family(run, _TABLE_FONT_NAME)


def _set_cell_borders(cell: _Cell) -> None:
    properties = cell._tc.get_or_add_tcPr()
    borders = properties.find(qn("w:tcBorders"))
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        properties.append(borders)
    for edge_name in ("top", "left", "bottom", "right", "insideH", "insideV"):
        edge = borders.find(qn(f"w:{edge_name}"))
        if edge is None:
            edge = OxmlElement(f"w:{edge_name}")
            borders.append(edge)
        edge.set(qn("w:val"), "single")
        edge.set(qn("w:sz"), "4")
        edge.set(qn("w:color"), "000000")


def _set_run_font_family(run, font_name: str) -> None:
    fonts = run._element.get_or_add_rPr().get_or_add_rFonts()
    for attribute in ("ascii", "hAnsi", "eastAsia", "cs"):
        fonts.set(qn(f"w:{attribute}"), font_name)


def _cell_fill_value(cell: _Cell) -> str | None:
    shading = cell._tc.get_or_add_tcPr().find(qn("w:shd"))
    return shading.get(qn("w:fill")) if shading is not None else None


def _resize_rows(table: Table, target: int) -> None:
    while len(table.rows) < target:
        template_row = table.rows[-1]
        cloned = deepcopy(template_row._tr)
        table._tbl.append(cloned)
    while len(table.rows) > target:
        row = table.rows[-1]
        table._tbl.remove(row._tr)


def _resize_columns(table: Table, target: int) -> None:
    while len(table.columns) < target:
        grid_columns = table._tbl.tblGrid.gridCol_lst
        if not grid_columns:
            raise ValueError("E-3707_H Test Description table has no column grid.")
        table._tbl.tblGrid.append(deepcopy(grid_columns[-1]))
        for row in table.rows:
            row._tr.append(deepcopy(row._tr.tc_lst[-1]))
    while len(table.columns) > target:
        index = len(table.columns) - 1
        grid_columns = table._tbl.tblGrid.gridCol_lst
        if index < len(grid_columns):
            table._tbl.tblGrid.remove(grid_columns[index])
        for row in table.rows:
            row._tr.remove(row.cells[index]._tc)


def _table_width_dxa(table: Table) -> int:
    table_width = table._tbl.tblPr.find(qn("w:tblW"))
    if table_width is not None and table_width.get(qn("w:type")) == "dxa":
        width = int(table_width.get(qn("w:w"), "0"))
        if width > 0:
            return width
    grid_widths = [
        int(column.get(qn("w:w"), "0"))
        for column in table._tbl.tblGrid.gridCol_lst
    ]
    total_width = sum(grid_widths)
    if total_width <= 0:
        raise ValueError("E-3707_H Test Description table has no usable width.")
    return total_width


def _set_description_widths(
    table: Table,
    group_count: int,
    total_width_dxa: int,
) -> None:
    if group_count < 1:
        raise ValueError("E-3707_H Test Description table requires a group column.")
    first_width = min(
        _PREFERRED_TEST_ITEM_WIDTH_DXA,
        max(
            _MIN_TEST_ITEM_WIDTH_DXA,
            total_width_dxa - group_count * _MIN_GROUP_WIDTH_DXA,
        ),
    )
    group_area_width = total_width_dxa - first_width
    if group_area_width < group_count:
        raise ValueError("E-3707_H Test Description table is too narrow for its groups.")
    group_width, remainder = divmod(group_area_width, group_count)
    widths = [first_width]
    widths.extend(
        group_width + (1 if index < remainder else 0)
        for index in range(group_count)
    )

    table_width = table._tbl.tblPr.find(qn("w:tblW"))
    if table_width is None:
        raise ValueError("E-3707_H Test Description table has no width contract.")
    table_width.set(qn("w:type"), "dxa")
    table_width.set(qn("w:w"), str(total_width_dxa))
    table.autofit = False

    grid_columns = table._tbl.tblGrid.gridCol_lst
    if len(grid_columns) != len(widths):
        raise ValueError("E-3707_H Test Description table grid is inconsistent.")
    for column, width in zip(grid_columns, widths, strict=True):
        column.set(qn("w:w"), str(width))

    for row in table.rows:
        grid_index = 0
        for cell_xml in row._tr.tc_lst:
            cell_properties = cell_xml.get_or_add_tcPr()
            span_xml = cell_properties.find(qn("w:gridSpan"))
            span = 1 if span_xml is None else int(span_xml.get(qn("w:val"), "1"))
            next_grid_index = grid_index + span
            if next_grid_index > len(widths):
                raise ValueError("E-3707_H Test Description cell span is inconsistent.")
            cell_width = cell_properties.get_or_add_tcW()
            cell_width.set(qn("w:type"), "dxa")
            cell_width.set(
                qn("w:w"),
                str(sum(widths[grid_index:next_grid_index])),
            )
            grid_index = next_grid_index
        if grid_index != len(widths):
            raise ValueError("E-3707_H Test Description row grid is inconsistent.")


def _insert_page_break_before_heading(document, heading: str) -> None:
    paragraph = next(
        (
            item
            for item in document.paragraphs
            if _heading_key(item.text) == _heading_key(heading)
        ),
        None,
    )
    if paragraph is None:
        raise ValueError(f"E-3707_H template heading is missing: {heading}")
    break_paragraph = OxmlElement("w:p")
    run = OxmlElement("w:r")
    page_break = OxmlElement("w:br")
    page_break.set(qn("w:type"), "page")
    run.append(page_break)
    break_paragraph.append(run)
    paragraph._p.addprevious(break_paragraph)


def _set_document_table_font(document, font_name: str) -> None:
    tables = list(document.tables)
    for section in document.sections:
        for header in (section.header, section.first_page_header):
            tables.extend(header.tables)
        for footer in (section.footer, section.first_page_footer):
            tables.extend(footer.tables)
    for table in tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.name = font_name
                        fonts = run._element.get_or_add_rPr().get_or_add_rFonts()
                        for attribute in ("ascii", "hAnsi", "eastAsia", "cs"):
                            fonts.set(qn(f"w:{attribute}"), font_name)


def _apply_report_body_format(document) -> bool:
    before = document.element.body.xml
    for keep_next in document.element.body.xpath(".//w:keepNext"):
        keep_next.getparent().remove(keep_next)
    for paragraph in document.paragraphs:
        size = (
            _CHAPTER_HEADING_FONT_SIZE
            if _is_report_chapter_heading(paragraph.text)
            else _BODY_FONT_SIZE
        )
        for run in paragraph.runs:
            run.font.size = size
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = _BODY_FONT_SIZE
    return document.element.body.xml != before


def _is_report_chapter_heading(value: str) -> bool:
    normalized = _heading_key(value)
    return (
        normalized in _NUMBERED_CHAPTER_HEADING_KEYS
        or re.fullmatch(r"group\s+.+\s+test results", normalized, re.IGNORECASE)
        is not None
        or re.match(r"^appendix\s+[a-z]\s*:", normalized, re.IGNORECASE)
        is not None
    )


def _page_break_paragraph():
    paragraph = OxmlElement("w:p")
    run = OxmlElement("w:r")
    page_break = OxmlElement("w:br")
    page_break.set(qn("w:type"), "page")
    run.append(page_break)
    paragraph.append(run)
    return paragraph


def _audit_report_body_format(document) -> None:
    if document.element.body.xpath(".//w:keepNext"):
        raise ValueError("Generated report still contains keep-with-next pagination controls.")
    for paragraph in document.paragraphs:
        expected = (
            _CHAPTER_HEADING_FONT_SIZE
            if _is_report_chapter_heading(paragraph.text)
            else _BODY_FONT_SIZE
        )
        if any(
            run.font.size != expected
            for run in paragraph.runs
            if run.text.strip()
        ):
            raise ValueError("Generated report body typography is inconsistent.")
    if any(
        run.font.size != _BODY_FONT_SIZE
        for table in document.tables
        for row in table.rows
        for cell in row.cells
        for paragraph in cell.paragraphs
        for run in paragraph.runs
        if run.text
    ):
        raise ValueError("Generated report table typography is inconsistent.")


def _set_cell_fill(cell: _Cell, fill: str) -> None:
    properties = cell._tc.get_or_add_tcPr()
    shading = properties.find(qn("w:shd"))
    if shading is None:
        shading = OxmlElement("w:shd")
        properties.append(shading)
    shading.set(qn("w:val"), "clear")
    shading.set(qn("w:color"), "auto")
    shading.set(qn("w:fill"), fill)


def _test_sequence_group_label(value: str) -> str:
    return re.sub(r"^Group\s+", "", value.strip(), flags=re.IGNORECASE)


def _default_result(requirement: str) -> str:
    normalized = _normalized(requirement)
    if normalized.casefold() == "no detrimental condition":
        return "No detriment"
    return re.sub(
        r"([≤≥])\s*[+-]?(?:\d+(?:\.\d*)?|\.\d+)",
        r"\1_",
        requirement.strip(),
    )


def _step_description(steps, step_index: int, llcr_indexes: tuple[int, ...]) -> str:
    step = steps[step_index]
    if not is_llcr_test_item(step.test_item):
        description = step.test_item
        if step.suffix_note:
            description = f"{description} ({step.suffix_note})"
        return description
    if len(llcr_indexes) <= 1 or step_index == llcr_indexes[0]:
        return "LLCR"
    if step_index == llcr_indexes[-1]:
        return "Final ΔR"
    previous = next(
        (
            candidate
            for candidate in reversed(steps[:step_index])
            if not is_llcr_test_item(candidate.test_item)
        ),
        None,
    )
    return f"After {previous.test_item}" if previous is not None else "LLCR"


def _stage_result_requirement(
    requirement: str,
    *,
    step_index: int,
    llcr_indexes: tuple[int, ...],
) -> str:
    if step_index not in llcr_indexes:
        return requirement
    clauses = [
        clause.strip()
        for clause in re.split(r"[;；\n]+", requirement)
        if clause.strip()
    ]
    if not clauses:
        return requirement
    if step_index == llcr_indexes[0]:
        return next(
            (clause for clause in clauses if "initial" in clause.casefold()),
            clauses[0],
        )
    return next(
        (clause for clause in clauses if "ΔR" in clause or "∆R" in clause),
        clauses[-1],
    )


def _display_requirement(
    requirement: str,
    *,
    step_index: int,
    llcr_indexes: tuple[int, ...],
) -> str:
    normalized = requirement.strip()
    if (
        llcr_indexes
        and step_index == llcr_indexes[0]
        and "initial" not in normalized.casefold()
        and re.match(r"^[≤≥]", normalized)
    ):
        return f"Initial {normalized}"
    return normalized


def _set_cell_text(cell: _Cell, text: str) -> None:
    first = cell.paragraphs[0]
    for paragraph in list(cell.paragraphs[1:]):
        cell._tc.remove(paragraph._p)
    _set_paragraph_text(first, text)


def _set_paragraph_text(paragraph: Paragraph, text: str) -> None:
    run_properties = None
    for run in paragraph.runs:
        if run._r.rPr is not None:
            run_properties = deepcopy(run._r.rPr)
            break
    for child in list(paragraph._p):
        if child.tag != qn("w:pPr"):
            paragraph._p.remove(child)
    run = paragraph.add_run(text)
    if run_properties is not None:
        run._r.insert(0, run_properties)


def _display_date(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        return "[To be confirmed]"
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError:
        return normalized
    return parsed.strftime("%b %d, %Y")


def _display_test_date_range(start_date: str, finish_date: str) -> str:
    start = start_date.strip()
    finish = finish_date.strip()
    if not start or not finish:
        return "TBD"
    return f"{_display_header_date(start)} to {_display_header_date(finish)}"


def _display_header_date(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    return parsed.strftime("%d/%b/%Y")


def _audit_generated_document(path: Path, report: TestReportDraftData) -> None:
    document = Document(path)
    _validate_template_contract(document, populated=True)
    _audit_report_body_format(document)
    body_text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    if "[PRODUCT NAME]" in body_text or "[TEST DESCRIPTION]" in body_text:
        raise ValueError("Generated report still contains required identity placeholders.")
    header_text = "".join(
        text
        for section in document.sections
        for header in (section.header, section.first_page_header)
        for text in _header_text_nodes(header)
    )
    if report.report_number not in header_text:
        raise ValueError("Generated report header does not contain the report number.")
    unresolved = [
        placeholder
        for placeholder in _REQUIRED_FIRST_PAGE_HEADER_PLACEHOLDERS
        if placeholder in header_text
    ]
    if unresolved:
        raise ValueError(
            "Generated report header still contains placeholders: "
            + ", ".join(unresolved)
        )


def _header_text_nodes(header) -> tuple[str, ...]:
    return tuple(
        text_node.text or "" for text_node in header._element.xpath(".//w:t")
    )


def _normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _heading_key(value: str) -> str:
    return re.sub(r"^(\d+)\.\s*", r"\1. ", _normalized(value))
