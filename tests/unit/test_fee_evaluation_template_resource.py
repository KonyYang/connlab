from __future__ import annotations

from pathlib import Path

import pytest

from backend.application.fee_evaluation_template_resource import (
    FeeEvaluationTemplateResourceError,
    resolve_fee_evaluation_template_path,
)
from backend.domain import (
    ExternalResource,
    ExternalResourceType,
    ExternalResourceValidationStatus,
)


def test_resolves_fee_template_from_settings_template_folder(tmp_path: Path) -> None:
    template_folder = tmp_path / "settings-template-folder"
    runtime_templates = tmp_path / "runtime-templates"
    template_folder.mkdir()
    runtime_templates.mkdir()
    template = template_folder / "FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls"
    template.write_bytes(b"settings template")

    resolved = resolve_fee_evaluation_template_path(
        _Store(_resource(template_folder))
    )

    assert resolved == template


def test_missing_settings_template_folder_resource_is_blocked() -> None:
    with pytest.raises(
        FeeEvaluationTemplateResourceError,
        match="Template folder is not configured",
    ):
        resolve_fee_evaluation_template_path(_Store(None))


def test_inactive_settings_template_folder_resource_is_blocked(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        FeeEvaluationTemplateResourceError,
        match="Template folder is inactive",
    ):
        resolve_fee_evaluation_template_path(
            _Store(_resource(tmp_path, active=False))
        )


class _Store:
    def __init__(self, resource: ExternalResource | None) -> None:
        self._resource = resource

    def get_by_type(
        self,
        resource_type: ExternalResourceType,
    ) -> ExternalResource | None:
        if resource_type is ExternalResourceType.PROJECT_FOLDER_TEMPLATE:
            return self._resource
        return None


def _resource(path: Path, *, active: bool = True) -> ExternalResource:
    return ExternalResource(
        resource_id="resource-1",
        resource_type=ExternalResourceType.PROJECT_FOLDER_TEMPLATE,
        path=path,
        active=active,
        validation_status=ExternalResourceValidationStatus.VALID,
    )
