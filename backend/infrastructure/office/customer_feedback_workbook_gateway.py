"""Customer Feedback workbook generation gateway."""

from __future__ import annotations

import shutil
from pathlib import Path

from openpyxl import load_workbook


class CustomerFeedbackWorkbookGatewayError(RuntimeError):
    """Raised when Customer Feedback workbook generation cannot proceed."""


class CustomerFeedbackWorkbookGateway:
    """Generate Customer Feedback workbooks through a safe Office boundary."""

    def generate(
        self,
        *,
        template_path: Path,
        output_path: Path,
        identity: dict[str, str],
    ) -> tuple[Path, tuple[str, ...]]:
        """Copy the Customer Feedback template and fill known header labels."""
        template = Path(template_path)
        target = Path(output_path)
        if template.suffix.lower() != ".xlsx":
            raise CustomerFeedbackWorkbookGatewayError(
                f"Customer Feedback template must be an .xlsx file: {template}"
            )
        if target.suffix.lower() != ".xlsx":
            raise CustomerFeedbackWorkbookGatewayError(
                f"Customer Feedback output must be an .xlsx file: {target}"
            )
        if not template.is_file():
            raise CustomerFeedbackWorkbookGatewayError(
                f"Customer Feedback template does not exist: {template}"
            )
        if template.resolve() == target.resolve():
            raise CustomerFeedbackWorkbookGatewayError(
                "Customer Feedback output must not overwrite the source template."
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(template, target)
        warnings = _fill_identity_fields(target, identity)
        return target, tuple(warnings)


def _fill_identity_fields(path: Path, identity: dict[str, str]) -> list[str]:
    """Fill simple label/value header cells in the copied workbook."""
    aliases = {
        "ltr_number": ("ltr number", "dl number", "project number", "project no"),
        "requestor": ("requestor", "requester", "requested by"),
        "product_name": ("product name", "product description", "product"),
    }
    workbook = load_workbook(path)
    warnings: list[str] = []
    changed = False
    for field_key, value in identity.items():
        if not value or field_key not in aliases:
            continue
        location = _find_label_cell(workbook, aliases[field_key])
        if location is None:
            warnings.append(f"Customer Feedback header field not found: {field_key}")
            continue
        sheet_name, row, column = location
        sheet = workbook[sheet_name]
        target = sheet.cell(row=row, column=column + 1)
        if target.value != value:
            target.value = value
            changed = True
    if changed:
        workbook.save(path)
    workbook.close()
    return warnings


def _find_label_cell(workbook, aliases: tuple[str, ...]) -> tuple[str, int, int] | None:
    normalized_aliases = {_normalize(alias) for alias in aliases}
    for sheet in workbook.worksheets:
        max_row = min(sheet.max_row, 30)
        max_column = min(sheet.max_column, 12)
        for row in range(1, max_row + 1):
            for column in range(1, max_column + 1):
                value = sheet.cell(row=row, column=column).value
                if _normalize(str(value or "")) in normalized_aliases:
                    return sheet.title, row, column
    return None


def _normalize(value: str) -> str:
    return " ".join(
        "".join(ch.lower() if ch.isalnum() else " " for ch in value).split()
    )
