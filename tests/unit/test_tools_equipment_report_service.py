from datetime import date
from pathlib import Path

from docx import Document
import pytest

from backend.application.external_excel_read_service import (
    EquipmentCalibrationReadResult, EquipmentCalibrationRow,
)
from backend.application.tools_equipment_report_service import ToolsEquipmentReportService
from backend.infrastructure.office.equipment_id_document_reader import EquipmentIdDocumentReader


class Catalog:
    def __init__(self, path):
        self.path = path

    def read_equipment_calibrations(self):
        return EquipmentCalibrationReadResult(str(self.path), ("All Equip.",), (
            EquipmentCalibrationRow("DG-Q-0033", "Multimeter", "Keysight",
                                    "2026-01-01", "2027-01-01", "All Equip."),
        ))


class OfficeWriter:
    def synchronize_equipment_list(self, *, source_path, output_path, rows):
        self.rows = rows
        output_path.write_bytes(b"updated-copy")
        return output_path


def service(tmp_path):
    catalog_path = tmp_path / "catalog.xlsx"
    catalog_path.write_bytes(b"stable catalog")
    writer = OfficeWriter()
    instance = ToolsEquipmentReportService(
        source_reader=EquipmentIdDocumentReader(), catalog_reader=Catalog(catalog_path),
        report_writer=writer, today=lambda: date(2026, 10, 3),
    )
    return instance, writer


def test_updates_uploaded_report_copy_from_equipment_document_without_project(tmp_path: Path):
    report = tmp_path / "Internal Report.docx"
    report.write_bytes(b"original report")
    equipment = tmp_path / "equipment.docx"
    document = Document()
    document.add_paragraph("Q-0033, DG-Q-0033, DG-Q-9999")
    document.save(equipment)
    before = equipment.read_bytes()
    instance, writer = service(tmp_path)

    result = instance.update(source_path=report, output_path=tmp_path / "updated.docx",
                             equipment_path=equipment)

    assert result.output_path.read_bytes() == b"updated-copy"
    assert report.read_bytes() == b"original report"
    assert equipment.read_bytes() == before
    assert len(writer.rows) == 2
    assert writer.rows[0].item == "Multimeter"
    assert writer.rows[0].last_calibration == "01-Jan-2026"
    assert writer.rows[1].item == ""
    assert result.statistics == {"filled": 2, "unmatched": ["DG-Q-9999"],
                                 "incomplete": [], "expired": []}


def test_pasted_ids_are_normalized_and_do_not_replace_original_report(tmp_path):
    instance, writer = service(tmp_path)
    report = tmp_path / "source.docx"
    report.write_bytes(b"source")
    result = instance.update(source_path=report, output_path=tmp_path / "copy.docx",
                             references_text="DG-Q-0033\nQ-0033")
    assert result.statistics["filled"] == 1
    assert writer.rows[0].id_number == "DG-Q-0033"
    assert report.read_bytes() == b"source"


@pytest.mark.parametrize("selection", [{}, {"references_text": " "},
                                        {"equipment_path": Path("id.docx"), "references_text": "Q-0033"}])
def test_requires_exactly_one_equipment_source(tmp_path, selection):
    instance, _writer = service(tmp_path)
    report = tmp_path / "source.docx"
    report.write_bytes(b"source")
    output = tmp_path / "copy.docx"
    with pytest.raises(ValueError, match="Choose EquipmentID.docx"):
        instance.update(source_path=report, output_path=output, **selection)
    assert not output.exists()


def test_existing_output_is_never_replaced_or_deleted(tmp_path):
    instance, _writer = service(tmp_path)
    report = tmp_path / "source.docx"
    report.write_bytes(b"source")
    output = tmp_path / "copy.docx"
    output.write_bytes(b"keep")
    with pytest.raises(ValueError, match="new .docx copy"):
        instance.update(source_path=report, output_path=output, references_text="Q-0033")
    assert output.read_bytes() == b"keep"


def test_calibration_change_during_writing_discards_only_updated_copy(tmp_path):
    instance, writer = service(tmp_path)
    report = tmp_path / "source.docx"
    report.write_bytes(b"source")
    write = writer.synchronize_equipment_list
    def changing_writer(**kwargs):
        result = write(**kwargs)
        (tmp_path / "catalog.xlsx").write_bytes(b"changed")
        return result
    writer.synchronize_equipment_list = changing_writer
    output = tmp_path / "copy.docx"
    with pytest.raises(ValueError, match="changed"):
        instance.update(source_path=report, output_path=output, references_text="Q-0033")
    assert not output.exists()
    assert report.read_bytes() == b"source"


def test_catalog_configuration_switch_during_writing_stops_download(tmp_path):
    workbook = tmp_path / "catalog.xlsx"
    workbook.write_bytes(b"catalog")
    catalog = Catalog(workbook)
    writer = OfficeWriter()
    instance = ToolsEquipmentReportService(source_reader=EquipmentIdDocumentReader(),
        catalog_reader=catalog, report_writer=writer)
    report = tmp_path / "source.docx"
    report.write_bytes(b"source")
    replacement = tmp_path / "other.xlsx"
    replacement.write_bytes(b"other catalog")
    write = writer.synchronize_equipment_list
    def switching_writer(**kwargs):
        result = write(**kwargs)
        catalog.path = replacement
        return result
    writer.synchronize_equipment_list = switching_writer
    output = tmp_path / "copy.docx"
    with pytest.raises(ValueError, match="changed"):
        instance.update(source_path=report, output_path=output, references_text="Q-0033")
    assert not output.exists()
