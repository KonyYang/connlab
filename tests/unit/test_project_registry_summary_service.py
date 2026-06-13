from __future__ import annotations

import json
from datetime import date

from backend.application.project_registry_summary_service import (
    ProjectRegistrySummaryService,
)
from backend.domain import LtrRecord, LtrStatus, Project, ProjectStatus


def test_registry_summary_uses_new_project_setup_fields_from_backend_notes() -> None:
    service = ProjectRegistrySummaryService(
        project_store=_ProjectStore(
            [
                _project(
                    project_id="P1",
                    product_name="CoolPower connector samples",
                    requestor="Neo Xu",
                    business_unit="Power Solutions",
                )
            ]
        ),
        ltr_store=_LtrStore(
            {
                "P1": [
                    _ltr(
                        project_id="P1",
                        number="DL-2026-05-001",
                        notes=_audit_notes(
                            operator_note=json.dumps(
                                {
                                    "source": "new_project_setup_confirmation",
                                    "sample_description": "CoolPower connector samples",
                                    "test_item": "Qualification bend testing",
                                },
                                sort_keys=True,
                            )
                        ),
                    )
                ]
            }
        ),
    )

    rows = service.list_rows()

    assert len(rows) == 1
    assert rows[0].ltr_number == "DL-2026-05-001"
    assert rows[0].sample_description == "CoolPower connector samples"
    assert rows[0].test_item == "Qualification bend testing"
    assert rows[0].notes is None
    assert rows[0].progress == 70


def test_registry_summary_uses_project_product_name_without_raw_json_leak() -> None:
    raw_audit = json.dumps({"commit_mode": "external_ltr_workbook", "row_number": 7})
    service = ProjectRegistrySummaryService(
        project_store=_ProjectStore(
            [
                _project(
                    project_id="P1",
                    product_name="Show As Sample Description",
                    status=ProjectStatus.LTR_REGISTERED,
                )
            ]
        ),
        ltr_store=_LtrStore(
            {"P1": [_ltr(project_id="P1", number="DL-2026-05-002", notes=raw_audit)]}
        ),
    )

    row = service.list_rows()[0]

    assert row.sample_description == "Show As Sample Description"
    assert row.test_item is None
    assert row.notes is None


def test_registry_summary_surfaces_plain_operator_note_without_json_leak() -> None:
    service = ProjectRegistrySummaryService(
        project_store=_ProjectStore([_project(project_id="P1")]),
        ltr_store=_LtrStore(
            {
                "P1": [
                    _ltr(
                        project_id="P1",
                        number="DL-2026-05-003",
                        notes=_audit_notes(operator_note="Customer asked for retest priority."),
                    )
                ]
            }
        ),
    )

    row = service.list_rows()[0]

    assert row.notes == "Customer asked for retest priority."
    assert "operator_note" not in row.notes


def test_temporary_project_has_stable_temporary_identity() -> None:
    service = ProjectRegistrySummaryService(
        project_store=_ProjectStore(
            [
                _project(
                    project_id="2cd4b0e7ff6f4df99448c9ffdd78629f",
                    status=ProjectStatus.DRAFT,
                )
            ]
        ),
        ltr_store=_LtrStore({}),
    )

    row = service.list_rows()[0]

    assert row.ltr_number is None
    assert row.display_project_id == "TMP-2CD4B0E7"
    assert row.display_project_id_kind == "temporary"
    assert row.has_registered_ltr is False
    assert row.temporary_project_id == "TMP-2CD4B0E7"
    assert row.registered_ltr_number is None


def test_project_no_is_not_used_as_registered_display_identity() -> None:
    service = ProjectRegistrySummaryService(
        project_store=_ProjectStore(
            [
                _project(
                    project_id="aabbccddeeff00112233445566778899",
                    project_no="1453402",
                    status=ProjectStatus.DRAFT,
                )
            ]
        ),
        ltr_store=_LtrStore({}),
    )

    row = service.list_rows()[0]

    assert row.ltr_number is None
    assert row.display_project_id == "TMP-AABBCCDD"
    assert row.display_project_id_kind == "temporary"
    assert row.has_registered_ltr is False
    assert row.registered_ltr_number is None


def test_registered_project_has_registered_identity() -> None:
    service = ProjectRegistrySummaryService(
        project_store=_ProjectStore([_project(project_id="P1")]),
        ltr_store=_LtrStore(
            {"P1": [_ltr(project_id="P1", number="DL-2026-05-009", notes=None)]}
        ),
    )

    row = service.list_rows()[0]

    assert row.display_project_id == "DL-2026-05-009"
    assert row.display_project_id_kind == "registered"
    assert row.has_registered_ltr is True
    assert row.temporary_project_id is None
    assert row.registered_ltr_number == "DL-2026-05-009"


class _ProjectStore:
    def __init__(self, projects: list[Project]) -> None:
        self._projects = projects

    def list(self) -> list[Project]:
        return self._projects


class _LtrStore:
    def __init__(self, records: dict[str, list[LtrRecord]]) -> None:
        self._records = records

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        return self._records.get(project_id, [])


def _project(
    *,
    project_id: str,
    project_no: str | None = None,
    product_name: str = "Project product",
    requestor: str = "Requester",
    business_unit: str | None = "DG",
    status: ProjectStatus = ProjectStatus.LTR_REGISTERED,
) -> Project:
    return Project(
        project_id=project_id,
        project_no=project_no,
        product_name=product_name,
        requestor=requestor,
        business_unit=business_unit,
        status=status,
        created_on=date(2026, 6, 7),
    )


def _ltr(*, project_id: str, number: str, notes: str | None) -> LtrRecord:
    return LtrRecord(
        ltr_id=f"ltr-{number}",
        project_id=project_id,
        ltr_number=number,
        status=LtrStatus.REGISTERED,
        registered_on=date(2026, 6, 7),
        notes=notes,
    )


def _audit_notes(*, operator_note: str | None) -> str:
    return json.dumps(
        {
            "commit_mode": "external_ltr_workbook",
            "operator_note": operator_note,
            "row_number": 12,
        },
        sort_keys=True,
    )
