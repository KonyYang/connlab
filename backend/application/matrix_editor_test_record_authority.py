"""Compare the current Matrix Editor Test Record payload with active authority."""

from __future__ import annotations

from hashlib import sha256
import json
from typing import Iterable, Protocol


class ConfirmedMatrixStore(Protocol):
    def get_active_by_project(self, project_id: str):
        """Return the active confirmed Matrix snapshot when one exists."""


class ConfirmedMatrixTestRecordAuthorityMatcher:
    """Keep official Test Record publication behind active Matrix authority."""

    def __init__(self, confirmed_store: ConfirmedMatrixStore) -> None:
        self._confirmed = confirmed_store

    def matches_active_authority(
        self, project_id: str, draft_signature: str
    ) -> bool:
        snapshot = self._confirmed.get_active_by_project(project_id)
        if snapshot is None:
            return False
        cells = {
            (cell.confirmed_row_id, cell.confirmed_group_id): cell.cell_value
            for cell in snapshot.cells
        }
        group_key_by_id = {
            group.confirmed_group_id: group.group_key for group in snapshot.groups
        }
        groups = tuple(snapshot.groups)
        rows = tuple(
            _ConfirmedRowProjection(
                row=row,
                group_values={
                    group_key_by_id[group.confirmed_group_id]: cells.get(
                        (row.confirmed_row_id, group.confirmed_group_id), ""
                    )
                    for group in groups
                },
            )
            for row in snapshot.rows
        )
        return draft_signature == build_matrix_editor_test_record_signature(
            groups=groups,
            rows=rows,
        )


class _ConfirmedRowProjection:
    def __init__(self, *, row, group_values: dict[str, str]) -> None:
        self.test_item = row.test_item
        self.section = row.source_section
        self.method = row.method
        self.condition = row.condition
        self.requirement = row.requirement
        self.is_sample_row = False
        self.group_values = group_values


def build_matrix_editor_test_record_signature(
    *, groups: Iterable[object], rows: Iterable[object]
) -> str:
    """Return a stable signature for fields consumed by Test Record generation."""
    group_items = tuple(groups)
    payload = {
        "groups": [
            {
                "group_key": _text(group.group_key),
                "group_label": _text(group.group_label),
                "sample_quantity_expression": _text(
                    group.sample_quantity_expression
                ),
            }
            for group in group_items
        ],
        "rows": [
            {
                "test_item": _text(row.test_item),
                "section": _text(row.section),
                "method": _text(row.method),
                "condition": _text(row.condition),
                "requirement": _text(row.requirement),
                "is_sample_row": bool(row.is_sample_row),
                "group_values": {
                    _text(group.group_key): _text(
                        row.group_values.get(group.group_key, "")
                    )
                    for group in group_items
                },
            }
            for row in rows
            if not bool(getattr(row, "is_sample_row", False))
        ],
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _text(value: object | None) -> str:
    return str(value or "").strip()
