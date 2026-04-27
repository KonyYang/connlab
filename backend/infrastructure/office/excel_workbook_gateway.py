"""Excel workbook gateway boundary for future Office integration."""

from __future__ import annotations

from pathlib import Path


class ExcelWorkbookGateway:
    """Boundary placeholder for future Excel workbook reading."""

    def read_workbook(self, source_path: Path) -> object:
        """Reject workbook reads until a scoped task implements them."""
        raise NotImplementedError(
            "Excel workbook reading is not implemented in Phase 6A Office boundary: "
            f"{source_path}"
        )
