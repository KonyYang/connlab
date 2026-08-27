from __future__ import annotations

from pathlib import Path

import pytest

from backend.application.test_report_template_resource import (
    TestReportTemplateResourceError,
    resolve_test_report_template_path,
)
from backend.domain import (
    ExternalResource,
    ExternalResourceType,
    ExternalResourceValidationStatus,
)


def test_resolves_unique_e3707_h_template_from_settings_template_folder(
    tmp_path: Path,
) -> None:
    template_folder = tmp_path / "templates"
    template_folder.mkdir()
    approved = template_folder / "E-3707_H Laboratory Test Report_241216.docx"
    approved.write_bytes(b"approved")
    (template_folder / "E-4515_F Customer Report.docx").write_bytes(b"other")

    assert resolve_test_report_template_path(_Store(_resource(template_folder))) == approved


def test_rejects_ambiguous_e3707_h_templates(tmp_path: Path) -> None:
    template_folder = tmp_path / "templates"
    template_folder.mkdir()
    (template_folder / "E-3707_H Laboratory Test Report.docx").write_bytes(b"one")
    (template_folder / "E-3707_H Laboratory Test Report copy.docx").write_bytes(b"two")

    with pytest.raises(TestReportTemplateResourceError, match="Multiple E-3707_H"):
        resolve_test_report_template_path(_Store(_resource(template_folder)))


def test_rejects_missing_or_inactive_template_folder(tmp_path: Path) -> None:
    with pytest.raises(TestReportTemplateResourceError, match="Template folder is not configured"):
        resolve_test_report_template_path(_Store(None))

    template_folder = tmp_path / "templates"
    template_folder.mkdir()
    with pytest.raises(TestReportTemplateResourceError, match="inactive"):
        resolve_test_report_template_path(_Store(_resource(template_folder, active=False)))


class _Store:
    def __init__(self, resource: ExternalResource | None) -> None:
        self._resource = resource

    def get_by_type(self, resource_type: ExternalResourceType) -> ExternalResource | None:
        return (
            self._resource
            if resource_type is ExternalResourceType.PROJECT_FOLDER_TEMPLATE
            else None
        )


def _resource(path: Path, *, active: bool = True) -> ExternalResource:
    return ExternalResource(
        resource_id="template-folder",
        resource_type=ExternalResourceType.PROJECT_FOLDER_TEMPLATE,
        path=path,
        active=active,
        validation_status=ExternalResourceValidationStatus.VALID,
    )
