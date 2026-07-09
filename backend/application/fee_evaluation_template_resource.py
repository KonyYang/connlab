"""Resolve Fee Evaluation templates from configured external resources."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from backend.application.fee_evaluation_template_discovery import (
    discover_fee_evaluation_template,
)
from backend.domain import ExternalResource, ExternalResourceType


class FeeEvaluationTemplateResourceError(ValueError):
    """Raised when the Settings Template folder cannot provide a Fee template."""


class FeeEvaluationTemplateResourceStore(Protocol):
    """Repository behavior required to resolve the Fee Evaluation template."""

    def get_by_type(
        self,
        resource_type: ExternalResourceType,
    ) -> ExternalResource | None:
        """Return a registered resource by type."""


def resolve_fee_evaluation_template_path(
    resource_store: FeeEvaluationTemplateResourceStore,
) -> Path:
    """Return the Fee Evaluation template from the Settings Template folder."""
    resource = resource_store.get_by_type(ExternalResourceType.PROJECT_FOLDER_TEMPLATE)
    if resource is None:
        raise FeeEvaluationTemplateResourceError("Template folder is not configured.")
    if not resource.active:
        raise FeeEvaluationTemplateResourceError("Template folder is inactive.")
    return discover_fee_evaluation_template(Path(resource.path))
