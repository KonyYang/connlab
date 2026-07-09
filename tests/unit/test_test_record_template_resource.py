from __future__ import annotations

from pathlib import Path

import pytest

from backend.application.test_record_template_resource import (
    TestRecordTemplateResourceError,
    resolve_test_record_template_path,
)
from backend.domain import (
    ExternalResource,
    ExternalResourceType,
    ExternalResourceValidationStatus,
)


def test_resolves_configured_test_record_template_before_settings_folder(
    tmp_path: Path,
) -> None:
    configured = tmp_path / "custom.docx"
    configured.write_bytes(b"custom")

    resolved = resolve_test_record_template_path(
        _Store(None),
        configured_template_path=configured,
    )

    assert resolved == configured


def test_resolves_test_record_template_from_settings_template_folder(
    tmp_path: Path,
) -> None:
    template_folder = tmp_path / "settings-template-folder"
    template_folder.mkdir()
    template = template_folder / "FDQF-E-036 Test Record Template-Even.docx"
    template.write_bytes(b"template")

    resolved = resolve_test_record_template_path(_Store(_resource(template_folder)))

    assert resolved == template


def test_missing_settings_template_folder_resource_is_blocked() -> None:
    with pytest.raises(
        TestRecordTemplateResourceError,
        match="Test Record template path is not configured",
    ):
        resolve_test_record_template_path(_Store(None))


def test_missing_test_record_template_in_settings_folder_is_blocked(
    tmp_path: Path,
) -> None:
    template_folder = tmp_path / "settings-template-folder"
    template_folder.mkdir()

    with pytest.raises(
        TestRecordTemplateResourceError,
        match="Test Record template not found",
    ):
        resolve_test_record_template_path(_Store(_resource(template_folder)))


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
