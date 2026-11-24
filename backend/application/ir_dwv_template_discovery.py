"""Find the approved IR/DWV workbook in the configured Template folder."""

from collections.abc import Callable
from pathlib import Path


IR_DWV_FORM_NUMBER = "FDQF-E-033"


def is_ir_dwv_template_name(path: Path) -> bool:
    name = path.name.casefold()
    return (
        path.suffix.casefold() == ".xlsx"
        and not name.startswith("~$")
        and ("ir&dwv" in name or IR_DWV_FORM_NUMBER.casefold() in name)
    )


def discover_ir_dwv_template(
    folder: Path | None,
    *,
    validate_layout: Callable[[Path], None],
) -> Path:
    if folder is None:
        raise ValueError(
            "IR/DWV template not found. Set Template folder in Settings, then place the approved "
            f".xlsx file named with IR&DWV or {IR_DWV_FORM_NUMBER} directly in that folder."
        )
    try:
        candidates = sorted(
            (path for path in folder.iterdir() if is_ir_dwv_template_name(path) and path.is_file()),
            key=lambda path: path.name.casefold(),
        )
    except OSError as exc:
        raise ValueError(
            f"ConnLab cannot open Template folder: {folder}. "
            "In Settings, select a folder this computer can read."
        ) from exc
    if not candidates:
        raise ValueError(
            f"IR/DWV template not found in Template folder: {folder}. "
            f"Place the approved .xlsx file named with IR&DWV or {IR_DWV_FORM_NUMBER} directly in that folder."
        )
    if len(candidates) == 1:
        # The caller validates the selected workbook when opening it for use.
        return candidates[0]

    compatible: list[Path] = []
    for path in candidates:
        try:
            validate_layout(path)
        except ValueError:
            # A workbook can share the name without matching the approved form.
            continue
        compatible.append(path)
    if len(compatible) == 1:
        return compatible[0]
    names = ", ".join(path.name for path in compatible or candidates)
    if compatible:
        raise ValueError(
            f"Multiple compatible IR/DWV templates in Template folder: {names}. "
            f"Keep only the approved {IR_DWV_FORM_NUMBER} workbook in that folder."
        )
    raise ValueError(
        f"No compatible {IR_DWV_FORM_NUMBER} IR/DWV template in Template folder: {names}. "
        "Add the approved workbook with the original form layout."
    )
