"""Application Form Word COM target lookup helpers."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

from backend.infrastructure.office.application_form_word_mapping import (
    APPLICATION_FORM_FIELD_LABELS,
    APPLICATION_FORM_NEXT_ROW_FIELDS,
)


@dataclass(frozen=True, slots=True)
class ApplicationFormWordTarget:
    """Resolved Word COM target cell for one Application Form field."""

    field_key: str
    cell: object
    label: str
    location: str

    def visible_text(self) -> str:
        """Return the current target cell visible text."""
        return com_clean(getattr(getattr(self.cell, "Range", None), "Text", ""))


@dataclass(frozen=True, slots=True)
class ApplicationFormWordTargetIndex:
    """One-pass target lookup index for Application Form body fields."""

    targets: dict[str, ApplicationFormWordTarget]

    @classmethod
    def build(cls, document: object, *, field_keys: set[str]) -> "ApplicationFormWordTargetIndex":
        """Build a target index by scanning Word document tables once."""
        wanted = {key for key in field_keys if key in APPLICATION_FORM_FIELD_LABELS}
        targets: dict[str, ApplicationFormWordTarget] = {}
        tables = com_iter(getattr(document, "Tables", None))
        for table_index, table in enumerate(tables, start=1):
            _collect_table_targets(table, table_index, wanted, targets)
            if wanted <= targets.keys():
                break
        if wanted & {"location", "manufacturing_site"} and not (
            {"location", "manufacturing_site"} & targets.keys()
        ):
            _collect_business_unit_location_targets(tables, wanted, targets)
        return cls(targets=targets)

    def target_for(self, field_key: str) -> ApplicationFormWordTarget | None:
        """Return the resolved target for a field, if present."""
        return self.targets.get(field_key)


def label_matches_aliases(value: str, aliases: tuple[str, ...]) -> bool:
    """Return true when a Word label text exactly matches a known alias."""
    normalized = normalize_label(value)
    return normalized in {normalize_label(alias) for alias in aliases}


def normalize_label(value: str) -> str:
    """Normalize Word labels for deterministic matching."""
    text = clean_word_text(value).lower().rstrip(":")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def clean_word_text(value: object) -> str:
    """Collapse Word whitespace into a single trimmed string."""
    return re.sub(r"\s+", " ", str(value or "").replace("\x07", " ")).strip()


def com_clean(value: object) -> str:
    """Clean COM Word range text into human-visible text."""
    return clean_word_text(str(value or "").replace("\r", " ").replace("\x07", " "))


def com_iter(collection: object | None) -> list[object]:
    """Return COM collection items using 1-based indexing."""
    if collection is None:
        return []
    count = int(getattr(collection, "Count", 0) or 0)
    return [collection.Item(index) for index in range(1, count + 1)]


def com_table_cell(table: object, row: int, column: int) -> object | None:
    """Return a COM table cell or None when Word rejects the coordinate."""
    try:
        return table.Cell(row, column)
    except Exception:
        return None


def com_column_count(table: object) -> int:
    """Return a COM table column count or zero when unavailable."""
    return int(getattr(getattr(table, "Columns", None), "Count", 0) or 0)


def iter_com_table_cells(table: object) -> Iterable[tuple[int, int, object]]:
    """Yield available COM table cells while tolerating merged-cell errors."""
    row_count = int(getattr(getattr(table, "Rows", None), "Count", 0) or 0)
    for row_index in range(1, row_count + 1):
        for column_index in range(1, com_column_count(table) + 1):
            cell = com_table_cell(table, row_index, column_index)
            if cell is not None:
                yield row_index, column_index, cell


def _collect_table_targets(
    table: object,
    table_index: int,
    wanted: set[str],
    targets: dict[str, ApplicationFormWordTarget],
) -> None:
    for row_index, column_index, cell in iter_com_table_cells(table):
        if wanted <= targets.keys():
            return
        label_text = com_clean(getattr(cell.Range, "Text", ""))
        for field_key in wanted - targets.keys():
            aliases = APPLICATION_FORM_FIELD_LABELS[field_key]
            if not label_matches_aliases(label_text, aliases):
                continue
            target_row = row_index + 1 if field_key in APPLICATION_FORM_NEXT_ROW_FIELDS else row_index
            target_column = column_index if field_key in APPLICATION_FORM_NEXT_ROW_FIELDS else column_index + 1
            target_cell = com_table_cell(table, target_row, target_column)
            if target_cell is None:
                continue
            targets[field_key] = ApplicationFormWordTarget(
                field_key=field_key,
                cell=target_cell,
                label=label_text,
                location=f"table[{table_index}].cell[{target_row},{target_column}]",
            )


def _collect_business_unit_location_targets(
    tables: list[object],
    wanted: set[str],
    targets: dict[str, ApplicationFormWordTarget],
) -> None:
    for table_index, table in enumerate(tables, start=1):
        if com_column_count(table) != 6:
            continue
        target = _find_location_in_business_unit_table(table, table_index)
        if target is None:
            continue
        for field_key in ("location", "manufacturing_site"):
            if field_key in wanted and field_key not in targets:
                targets[field_key] = ApplicationFormWordTarget(
                    field_key=field_key,
                    cell=target.cell,
                    label=target.label,
                    location=target.location,
                )
        return


def _find_location_in_business_unit_table(
    table: object,
    table_index: int,
) -> ApplicationFormWordTarget | None:
    if com_column_count(table) != 6:
        return None
    for row_index, column_index, cell in iter_com_table_cells(table):
        label_text = com_clean(getattr(cell.Range, "Text", ""))
        if not label_matches_aliases(label_text, ("business unit", "bu")):
            continue
        row_values: list[tuple[int, object, str]] = []
        for target_column in range(column_index + 1, com_column_count(table) + 1):
            target_cell = com_table_cell(table, row_index, target_column)
            if target_cell is None:
                continue
            visible = com_clean(getattr(target_cell.Range, "Text", ""))
            if visible:
                row_values.append((target_column, target_cell, visible))
        if len(row_values) < 2:
            continue
        target_column, target_cell, _visible = row_values[-1]
        return ApplicationFormWordTarget(
            field_key="location",
            cell=target_cell,
            label="Business Unit row site",
            location=f"table[{table_index}].cell[{row_index},{target_column}]",
        )
    return None
