"""Update an uploaded report copy without project authority or publication."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from hashlib import file_digest
from pathlib import Path

from backend.application.current_report_update_service import EquipmentReportWriter
from backend.application.equipment_report_update_service import (
    EQUIPMENT_IDS_HELP, EquipmentCatalogReader, EquipmentSelectionError, EquipmentSourceReader,
    resolve_equipment_rows,
)
from backend.application.external_excel_read_service import ExternalExcelReadError, ExternalExcelReadNotFoundError
from backend.application.tools_service import ToolsError


@dataclass(frozen=True, slots=True)
class ToolsEquipmentReportResult:
    output_path: Path
    statistics: dict[str, object]


class ToolsEquipmentReportService:
    def __init__(
        self, *, source_reader: EquipmentSourceReader,
        catalog_reader: EquipmentCatalogReader,
        report_writer: EquipmentReportWriter,
        today: Callable[[], date] = date.today,
    ) -> None:
        self._source_reader = source_reader
        self._catalog_reader = catalog_reader
        self._writer = report_writer
        self._today = today

    def update(
        self, *, source_path: Path, output_path: Path,
        equipment_path: Path | None = None,
        references_text: str | None = None,
    ) -> ToolsEquipmentReportResult:
        source, output = Path(source_path), Path(output_path)
        if source.suffix.lower() != ".docx" or not source.is_file():
            raise ToolsError("Select an Internal Report .docx with an Equipment List table.")
        if output.suffix.lower() != ".docx" or output.resolve() == source.resolve() or output.exists():
            raise ToolsError("The updated report must be a new .docx copy.")
        has_text = bool(references_text and references_text.strip())
        if equipment_path and has_text:
            raise ToolsError("Choose EquipmentID.docx or enter equipment IDs, not both.")
        if not equipment_path and not has_text:
            raise ToolsError(f"Choose EquipmentID.docx or enter equipment IDs. {EQUIPMENT_IDS_HELP}")
        output.parent.mkdir(parents=True, exist_ok=True)
        if equipment_path is None:
            # The API supplies a per-request output directory, never a project folder.
            equipment_path = output.parent / "EquipmentID.docx"
            self._source_reader.save_missing(equipment_path, references_text=references_text)
        if output.resolve() == Path(equipment_path).resolve():
            raise ToolsError("The updated report must not replace the equipment selection.")
        tracked = {source: _sha256(source)}
        try:
            tracked[Path(equipment_path)] = _sha256(Path(equipment_path))
            selection = self._source_reader.read(equipment_path)
        except EquipmentSelectionError as exc:
            raise ToolsError(f"{exc} Choose the corrected document and retry the update.") from exc
        except OSError as exc:
            raise ToolsError(
                "ConnLab could not read EquipmentID.docx. Open the original in Word, save a local .docx copy, and select it again."
            ) from exc
        if not selection.references:
            raise ToolsError(f"EquipmentID.docx contains no equipment IDs. Open it in Word. {EQUIPMENT_IDS_HELP}")
        try:
            catalog = self._catalog_reader.read_equipment_calibrations()
            catalog_path = Path(catalog.resource_path)
            tracked[catalog_path] = _sha256(catalog_path)
            catalog = self._catalog_reader.read_equipment_calibrations()
            if Path(catalog.resource_path) != catalog_path:
                raise ValueError("Equipment workbook changed while reading.")
        except (ExternalExcelReadError, ExternalExcelReadNotFoundError) as exc:
            raise ToolsError(str(exc)) from exc
        except (LookupError, OSError, RuntimeError, ValueError) as exc:
            raise ToolsError(
                "ConnLab could not read the calibration workbook during the update. Open the file shown in "
                "Settings > Equipment calibration Excel in Excel on this computer, then retry."
            ) from exc
        rows, _warnings = resolve_equipment_rows(selection.references, catalog.rows, today=self._today())
        _require_unchanged(tracked)
        try:
            result = self._writer.synchronize_equipment_list(
                source_path=source, output_path=output, rows=tuple(rows),
            )
            if Path(result).resolve() != output.resolve() or not output.is_file() or not output.stat().st_size:
                raise ToolsError("The updated report could not be prepared. Retry the update.")
            if Path(self._catalog_reader.read_equipment_calibrations().resource_path) != catalog_path:
                raise ToolsError("The configured equipment workbook changed. Retry the update.")
            _require_unchanged(tracked)
        except Exception:
            output.unlink(missing_ok=True)
            raise
        return ToolsEquipmentReportResult(output, {
            "filled": len(rows),
            "unmatched": [row.source_reference for row in rows if row.status == "unmatched"],
            "incomplete": [row.source_reference for row in rows if row.status == "incomplete"],
            "expired": [row.source_reference for row in rows if row.expired],
        })


def _sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def _require_unchanged(tracked: dict[Path, str]) -> None:
    if any(_sha256(path) != digest for path, digest in tracked.items()):
        raise ToolsError("Report, equipment selection, or calibration workbook changed. Retry the update.")
