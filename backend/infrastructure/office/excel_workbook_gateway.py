"""Read-only Excel workbook gateway for Office integration."""

from __future__ import annotations

import re
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree

from backend.infrastructure.office.models import (
    ExcelTabularReadResult,
    ExcelStructureProbeResult,
    LtrWorkbookFormat,
    LtrWorkbookSnapshot,
)
from backend.infrastructure.office.excel_tabular_layout import (
    ExcelTabularLayout,
    ExcelTabularLayoutError,
    first_non_empty_row,
    header_index_map,
    map_explicit_layout_rows,
    matching_sheet_pairs,
    normalize_header,
    probe_failure,
    probe_explicit_xlsx_layout,
    row_is_header,
    sheet_strategy,
)
from backend.modules.ltr import LtrNumberError, parse_ltr_number


class LtrWorkbookGatewayError(ValueError):
    """Base error for read-only LTR workbook snapshot failures."""


class UnsupportedLtrWorkbookError(LtrWorkbookGatewayError):
    """Raised when the workbook format or layout is unsupported."""


class UnreadableLtrWorkbookError(LtrWorkbookGatewayError):
    """Raised when a workbook exists but cannot be read."""


class ExcelWorkbookGateway:
    """Read workbook metadata and LTR numbers without writing."""

    def read_workbook(self, source_path: Path) -> object:
        """Read a generic workbook through the LTR snapshot path."""
        return self.read_ltr_workbook_snapshot(source_path)

    def read_ltr_workbook_snapshot(self, source_path: Path) -> LtrWorkbookSnapshot:
        """Read workbook metadata and existing LTR numbers without writing."""
        path = Path(source_path)
        if not path.is_file():
            raise FileNotFoundError(f"LTR workbook does not exist: {path}")

        workbook_format = _workbook_format(path)
        if workbook_format is LtrWorkbookFormat.XLS:
            raise UnsupportedLtrWorkbookError(
                "Legacy .xls LTR workbook snapshot requires a later adapter task."
            )
        if workbook_format is LtrWorkbookFormat.UNSUPPORTED:
            raise UnsupportedLtrWorkbookError(
                f"Unsupported LTR workbook format: {path.suffix or '<none>'}"
            )

        stat = path.stat()
        sheet_names, sheet_xml_paths = _read_xlsx_workbook_manifest(path)
        ltr_numbers: list[str] = []
        readable_sheets: list[str] = []
        shared_strings = _read_xlsx_shared_strings(path)
        for sheet_name, sheet_xml_path in zip(sheet_names, sheet_xml_paths, strict=True):
            values = _read_xlsx_sheet_values(path, sheet_xml_path, shared_strings)
            readable_sheets.append(sheet_name)
            ltr_numbers.extend(_extract_ltr_numbers(values))

        return LtrWorkbookSnapshot(
            workbook_path=path,
            workbook_format=workbook_format,
            size_bytes=stat.st_size,
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            sheet_names=tuple(sheet_names),
            readable_sheet_names=tuple(readable_sheets),
            sheet_strategy=sheet_strategy(sheet_names),
            existing_ltr_numbers=tuple(dict.fromkeys(ltr_numbers)),
        )

    def probe_structure(
        self,
        source_path: Path,
        *,
        expected_headers: tuple[str, ...],
        expected_date_headers: tuple[str, ...] = (),
        expected_sheet_names: tuple[str, ...] = (),
        expected_sheet_name_patterns: tuple[str, ...] = (),
        layout: ExcelTabularLayout | None = None,
    ) -> ExcelStructureProbeResult:
        """Probe workbook sheets and headers without writing."""
        path = Path(source_path)
        if not path.is_file():
            raise FileNotFoundError(f"Excel workbook does not exist: {path}")
        if _workbook_format(path) is not LtrWorkbookFormat.XLSX:
            raise UnsupportedLtrWorkbookError(
                f"Excel structure probe supports .xlsx only: {path.suffix or '<none>'}"
            )
        sheet_names, sheet_xml_paths = _read_xlsx_workbook_manifest(path)
        matched_pairs = matching_sheet_pairs(
            sheet_names,
            sheet_xml_paths,
            expected_sheet_names,
            expected_sheet_name_patterns,
            normalize_exact=bool(layout and layout.require_unique_sheet_match),
        )
        if layout and layout.require_unique_sheet_match and len(matched_pairs) != 1:
            return ExcelStructureProbeResult(
                workbook_path=path,
                sheet_names=tuple(sheet_names),
                matched_sheet_names=tuple(name for name, _path in matched_pairs),
                observed_headers=(),
                missing_headers=expected_headers,
                missing_date_headers=expected_date_headers,
                valid=False,
                failure_reason="Configured worksheet must match exactly one sheet.",
            )
        shared_strings = _read_xlsx_shared_strings(path)
        if layout:
            return probe_explicit_xlsx_layout(
                path,
                tuple(sheet_names),
                matched_pairs,
                shared_strings,
                expected_headers,
                expected_date_headers,
                layout,
                lambda workbook, sheet, strings: _read_xlsx_sheet_rows(
                    workbook, sheet, strings, preserve_positions=True
                ),
            )
        observed_headers: list[str] = []
        for _sheet_name, sheet_xml_path in matched_pairs:
            rows = _read_xlsx_sheet_rows(path, sheet_xml_path, shared_strings)
            observed_headers.extend(first_non_empty_row(rows))
        normalized_observed = {normalize_header(value) for value in observed_headers}
        missing_headers = tuple(
            header
            for header in expected_headers
            if normalize_header(header) not in normalized_observed
        )
        missing_date_headers = tuple(
            header
            for header in expected_date_headers
            if normalize_header(header) not in normalized_observed
        )
        failure = probe_failure(matched_pairs, missing_headers, missing_date_headers)
        return ExcelStructureProbeResult(
            workbook_path=path,
            sheet_names=tuple(sheet_names),
            matched_sheet_names=tuple(name for name, _xml_path in matched_pairs),
            observed_headers=tuple(dict.fromkeys(observed_headers)),
            missing_headers=missing_headers,
            missing_date_headers=missing_date_headers,
            valid=failure is None,
            failure_reason=failure,
        )

    def read_tabular_rows(
        self,
        source_path: Path,
        *,
        expected_headers: tuple[str, ...],
        expected_sheet_names: tuple[str, ...] = (),
        expected_sheet_name_patterns: tuple[str, ...] = (),
        layout: ExcelTabularLayout | None = None,
    ) -> ExcelTabularReadResult:
        """Read header-aligned worksheet rows from matching worksheets."""
        path = Path(source_path)
        if not path.is_file():
            raise FileNotFoundError(f"Excel workbook does not exist: {path}")
        if _workbook_format(path) is not LtrWorkbookFormat.XLSX:
            raise UnsupportedLtrWorkbookError(
                f"Excel tabular read supports .xlsx only: {path.suffix or '<none>'}"
            )
        sheet_names, sheet_xml_paths = _read_xlsx_workbook_manifest(path)
        matched_pairs = matching_sheet_pairs(
            sheet_names,
            sheet_xml_paths,
            expected_sheet_names,
            expected_sheet_name_patterns,
            normalize_exact=bool(layout and layout.require_unique_sheet_match),
        )
        if not matched_pairs:
            raise UnsupportedLtrWorkbookError(
                "No worksheet matched the expected sheet rules."
            )
        shared_strings = _read_xlsx_shared_strings(path)
        if layout:
            if layout.require_unique_sheet_match and len(matched_pairs) != 1:
                raise UnsupportedLtrWorkbookError(
                    "Configured worksheet must match exactly one sheet."
                )
            collected: list[dict[str, str]] = []
            headers: tuple[str, ...] = ()
            names: list[str] = []
            try:
                for sheet_name, sheet_xml_path in matched_pairs:
                    rows = _read_xlsx_sheet_rows(
                        path, sheet_xml_path, shared_strings, preserve_positions=True
                    )
                    headers, mapped = map_explicit_layout_rows(
                        rows, sheet_name=sheet_name, layout=layout
                    )
                    collected.extend(mapped)
                    names.append(sheet_name)
            except ExcelTabularLayoutError as exc:
                raise UnsupportedLtrWorkbookError(str(exc)) from exc
            if not collected:
                raise UnsupportedLtrWorkbookError(
                    "Configured worksheet has no nonblank data rows."
                )
            return ExcelTabularReadResult(
                workbook_path=path,
                matched_sheet_names=tuple(names),
                headers=headers,
                rows=tuple(collected),
            )
        canonical_headers = tuple(expected_headers)
        normalized_canonical = [normalize_header(value) for value in canonical_headers]
        collected_rows: list[dict[str, str]] = []
        matched_sheet_names: list[str] = []
        for sheet_name, sheet_xml_path in matched_pairs:
            rows = _read_xlsx_sheet_rows(path, sheet_xml_path, shared_strings)
            header_row = first_non_empty_row(rows)
            if not header_row:
                continue
            index_map = header_index_map(header_row, normalized_canonical)
            if index_map is None:
                continue
            matched_sheet_names.append(sheet_name)
            for raw_row in rows:
                row = [value.strip() for value in raw_row]
                if not any(row):
                    continue
                # Skip the header row itself.
                if row_is_header(row, header_row):
                    continue
                mapped: dict[str, str] = {}
                has_value = False
                for header, index in zip(canonical_headers, index_map, strict=True):
                    value = row[index] if index < len(row) else ""
                    mapped[header] = value
                    has_value = has_value or bool(value)
                if has_value:
                    mapped["__sheet_name"] = sheet_name
                    collected_rows.append(mapped)
        if not matched_sheet_names:
            raise UnsupportedLtrWorkbookError("Expected headers were not found.")
        return ExcelTabularReadResult(
            workbook_path=path,
            matched_sheet_names=tuple(matched_sheet_names),
            headers=canonical_headers,
            rows=tuple(collected_rows),
        )


def _workbook_format(path: Path) -> LtrWorkbookFormat:
    """Return the workbook format from the extension."""
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        return LtrWorkbookFormat.XLSX
    if suffix == ".xls":
        return LtrWorkbookFormat.XLS
    return LtrWorkbookFormat.UNSUPPORTED


def _read_xlsx_workbook_manifest(path: Path) -> tuple[list[str], list[str]]:
    """Read sheet names and XML paths from an XLSX package."""
    try:
        with zipfile.ZipFile(path) as archive:
            workbook_root = ElementTree.fromstring(archive.read("xl/workbook.xml"))
            rels_root = ElementTree.fromstring(
                archive.read("xl/_rels/workbook.xml.rels")
            )
    except (KeyError, OSError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        raise UnreadableLtrWorkbookError(f"Unable to read XLSX workbook: {path}") from exc

    relationships = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels_root
        if "Id" in rel.attrib and "Target" in rel.attrib
    }
    sheet_names: list[str] = []
    sheet_xml_paths: list[str] = []
    for sheet in workbook_root.findall(".//{*}sheet"):
        name = sheet.attrib.get("name")
        relation_id = sheet.attrib.get(
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
        )
        target = relationships.get(relation_id or "")
        if not name or not target:
            continue
        sheet_names.append(name)
        sheet_xml_paths.append(_normalize_xlsx_target(target))
    if not sheet_names:
        raise UnsupportedLtrWorkbookError("XLSX workbook has no readable worksheets.")
    return sheet_names, sheet_xml_paths


def _read_xlsx_shared_strings(path: Path) -> list[str]:
    """Read shared strings from an XLSX package."""
    try:
        with zipfile.ZipFile(path) as archive:
            root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    except (OSError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        raise UnreadableLtrWorkbookError(
            f"Unable to read XLSX shared strings: {path}"
        ) from exc
    return [
        "".join(text.text or "" for text in item.findall(".//{*}t"))
        for item in root.findall(".//{*}si")
    ]


def _read_xlsx_sheet_values(
    path: Path,
    sheet_xml_path: str,
    shared_strings: list[str],
) -> list[str]:
    """Read plain cell values from one XLSX worksheet."""
    try:
        with zipfile.ZipFile(path) as archive:
            root = ElementTree.fromstring(archive.read(sheet_xml_path))
    except (KeyError, OSError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        raise UnreadableLtrWorkbookError(
            f"Unable to read XLSX worksheet: {sheet_xml_path}"
        ) from exc

    values: list[str] = []
    for cell in root.findall(".//{*}c"):
        value_node = cell.find("{*}v")
        inline_node = cell.find("{*}is/{*}t")
        if inline_node is not None and inline_node.text:
            values.append(inline_node.text)
            continue
        if value_node is None or value_node.text is None:
            continue
        if cell.attrib.get("t") == "s":
            index = int(value_node.text)
            if 0 <= index < len(shared_strings):
                values.append(shared_strings[index])
        else:
            values.append(value_node.text)
    return values


def _read_xlsx_sheet_rows(
    path: Path,
    sheet_xml_path: str,
    shared_strings: list[str],
    preserve_positions: bool = False,
) -> list[list[str]]:
    """Read plain worksheet rows from one XLSX sheet."""
    try:
        with zipfile.ZipFile(path) as archive:
            root = ElementTree.fromstring(archive.read(sheet_xml_path))
    except (KeyError, OSError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        raise UnreadableLtrWorkbookError(
            f"Unable to read XLSX worksheet: {sheet_xml_path}"
        ) from exc
    rows: list[list[str]] = []
    for row in root.findall(".//{*}row"):
        if not preserve_positions:
            rows.append([_cell_text(cell, shared_strings) for cell in row.findall("{*}c")])
            continue
        row_number = int(row.attrib.get("r", len(rows) + 1))
        while len(rows) < row_number - 1:
            rows.append([])
        values: list[str] = []
        for cell in row.findall("{*}c"):
            column = _xlsx_column_number(cell.attrib.get("r", "A1"))
            while len(values) < column:
                values.append("")
            values[column - 1] = _cell_text(cell, shared_strings)
        rows.append(values)
    return rows


def _xlsx_column_number(reference: str) -> int:
    letters = re.match(r"[A-Za-z]+", reference)
    if letters is None:
        return 1
    result = 0
    for letter in letters.group(0).upper():
        result = result * 26 + ord(letter) - ord("A") + 1
    return result


def _cell_text(cell: ElementTree.Element, shared_strings: list[str]) -> str:
    """Return a string value from one XLSX cell node."""
    inline_node = cell.find("{*}is/{*}t")
    if inline_node is not None and inline_node.text:
        return inline_node.text.strip()
    value_node = cell.find("{*}v")
    if value_node is None or value_node.text is None:
        return ""
    if cell.attrib.get("t") == "s":
        index = int(value_node.text)
        if 0 <= index < len(shared_strings):
            return shared_strings[index].strip()
        return ""
    return value_node.text.strip()


def _extract_ltr_numbers(values: list[str]) -> list[str]:
    """Extract supported LTR numbers from worksheet cell values."""
    numbers: list[str] = []
    for value in values:
        for candidate in re.findall(r"\b(?:DL-\d{4}-\d{2}-\d{3}[A-Z0-9]*|W[A-Z0-9]+)\b", value, flags=re.IGNORECASE):
            try:
                numbers.append(parse_ltr_number(candidate).normalized)
            except LtrNumberError:
                continue
    return numbers


def _normalize_xlsx_target(target: str) -> str:
    """Normalize a workbook relationship target into a ZIP path."""
    target = target.lstrip("/")
    if target.startswith("xl/"):
        return target
    return f"xl/{target}"
