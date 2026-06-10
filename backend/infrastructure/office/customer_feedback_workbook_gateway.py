"""Customer Feedback workbook generation gateway."""

from __future__ import annotations

import shutil
from pathlib import Path


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
        """Copy the Customer Feedback template to the output path.

        TASK_311 intentionally avoids guessing template cell anchors. The generated
        workbook is a safe copy, and later tasks can add verified cell filling.
        """
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
        return target, (
            "Customer Feedback workbook was copied; safe cell filling requires Excel COM implementation.",
        )
