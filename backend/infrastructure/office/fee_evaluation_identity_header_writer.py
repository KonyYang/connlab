"""Basic Information header writer for Fee Evaluation workbooks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.infrastructure.office.fee_evaluation_anchor_snapshot import (
    FeeEvaluationAnchorSnapshot,
)


DETAIL_START_ROW = 5


@dataclass(frozen=True, slots=True)
class IdentityFieldRule:
    """Label-based Fee Form header write rule."""

    field_key: str
    aliases: tuple[str, ...]


def write_basic_information_identity(
    sheet: Any,
    values: dict[str, str] | None,
    *,
    anchors: FeeEvaluationAnchorSnapshot | None = None,
) -> None:
    """Write Basic Information header values beside existing Fee Form labels."""
    if not values:
        return
    field_values = {
        "dl_number": (values.get("dl_number") or "").strip(),
        "test_description": _fee_test_description(values),
        "requestor": (values.get("requested_by") or "").strip(),
        "site": (values.get("location") or "").strip(),
    }
    rules = (
        IdentityFieldRule("dl_number", ("LTR Number", "DL/LTR Number")),
        IdentityFieldRule("test_description", ("Test Description",)),
        IdentityFieldRule("requestor", ("Requestor", "Requested by")),
        IdentityFieldRule("site", ("Site", "Mfg. Site", "Location")),
    )
    for rule in rules:
        value = field_values.get(rule.field_key, "")
        if not value:
            continue
        target = _find_identity_target_cell(sheet, rule, anchors=anchors)
        if target is None:
            continue
        row, column = target
        sheet.Cells(row, column).Value = value


def _fee_test_description(values: dict[str, str]) -> str:
    product_description = (values.get("product_description") or "").strip()
    test_item = (values.get("test_item") or "").strip()
    if not product_description:
        return test_item
    if not test_item:
        return product_description
    if test_item.lower() in product_description.lower():
        return product_description
    return f"{product_description} {test_item}"


def _find_identity_target_cell(
    sheet: Any,
    rule: IdentityFieldRule,
    *,
    anchors: FeeEvaluationAnchorSnapshot | None = None,
) -> tuple[int, int] | None:
    if anchors is not None:
        return anchors.find_identity_target(rule.aliases, max_row=DETAIL_START_ROW - 1)
    aliases = {_normalize_identity_label(alias) for alias in rule.aliases}
    for row in range(1, DETAIL_START_ROW):
        for column in range(1, 10):
            text = _normalize_identity_label(_cell_text(sheet, row, column))
            if text in aliases:
                return row, column + 1
    return None


def _normalize_identity_label(value: str) -> str:
    return " ".join(value.replace(":", " ").split()).strip().lower()


def _cell_text(sheet: Any, row: int, column: int) -> str:
    value = sheet.Cells(row, column).Value
    if value is None:
        return ""
    return str(value).strip()
