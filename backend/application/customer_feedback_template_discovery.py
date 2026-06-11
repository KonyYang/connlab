"""Pure Customer Feedback template discovery helpers."""

from __future__ import annotations

from pathlib import Path


class CustomerFeedbackTemplateDiscoveryError(RuntimeError):
    """Base error for Customer Feedback template discovery failures."""


class CustomerFeedbackTemplateMissingError(CustomerFeedbackTemplateDiscoveryError):
    """Raised when the Customer Feedback template cannot be found."""


class CustomerFeedbackTemplateAmbiguousError(CustomerFeedbackTemplateDiscoveryError):
    """Raised when more than one Customer Feedback template candidate exists."""


def discover_customer_feedback_template(template_folder: Path) -> Path:
    """Return the unique E-4243 `.xlsx` Customer Feedback template."""
    candidates = sorted(
        (
            path
            for path in Path(template_folder).iterdir()
            if path.is_file()
            and path.suffix.lower() == ".xlsx"
            and "e-4243" in path.name.lower()
        ),
        key=lambda path: path.name.lower(),
    )
    if not candidates:
        raise CustomerFeedbackTemplateMissingError(
            "Customer Feedback template was not found in Template folder. "
            "Add an .xlsx file whose name contains E-4243."
        )
    if len(candidates) > 1:
        names = ", ".join(path.name for path in candidates)
        raise CustomerFeedbackTemplateAmbiguousError(
            "Multiple Customer Feedback templates were found. "
            f"Keep exactly one E-4243 .xlsx template in Template folder: {names}"
        )
    return candidates[0]
