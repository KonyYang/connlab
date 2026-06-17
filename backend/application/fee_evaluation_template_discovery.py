"""Discover Fee Evaluation workbook templates from the Template folder."""

from __future__ import annotations

from pathlib import Path


FEE_EVALUATION_TEMPLATE_TOKEN = "FDQF-E-176"


class FeeEvaluationTemplateDiscoveryError(ValueError):
    """Raised when the Fee Evaluation template cannot be discovered."""


class FeeEvaluationTemplateAmbiguousError(FeeEvaluationTemplateDiscoveryError):
    """Raised when more than one matching Fee Evaluation template exists."""


def discover_fee_evaluation_template(template_folder: Path) -> Path:
    """Return the unique Fee Evaluation .xls template matching the business form id."""
    if not template_folder.exists() or not template_folder.is_dir():
        raise FeeEvaluationTemplateDiscoveryError(
            f"Template folder does not exist or is not a folder: {template_folder}"
        )
    matches = sorted(
        path
        for path in template_folder.iterdir()
        if path.is_file()
        and path.suffix.lower() == ".xls"
        and FEE_EVALUATION_TEMPLATE_TOKEN.lower() in path.name.lower()
    )
    if not matches:
        raise FeeEvaluationTemplateDiscoveryError(
            "Fee Evaluation template was not found in Template folder. "
            f"Add an .xls file whose name contains {FEE_EVALUATION_TEMPLATE_TOKEN}."
        )
    if len(matches) > 1:
        names = ", ".join(path.name for path in matches)
        raise FeeEvaluationTemplateAmbiguousError(
            "Multiple Fee Evaluation templates were found. "
            f"Keep exactly one {FEE_EVALUATION_TEMPLATE_TOKEN} .xls template "
            f"in Template folder: {names}"
        )
    return matches[0]
