from __future__ import annotations

from datetime import date

from backend.application.public_folder_year_resolver import PublicFolderYearResolver
from backend.domain import LtrRecord, LtrStatus, Project, ProjectStatus


def test_year_resolver_prefers_local_registered_ltr_date() -> None:
    resolver = PublicFolderYearResolver(
        project_repository=_Projects(_project()),
        ltr_repository=_Ltrs(
            LtrRecord(
                ltr_id="ltr-1",
                project_id="P1",
                ltr_number="DL-2026-06-001",
                status=LtrStatus.REGISTERED,
                registered_on=date(2026, 6, 30),
            )
        ),
        workbook_lookup=_Workbook("2025"),
    )

    result = resolver.resolve("P1")

    assert result.year == 2026
    assert result.source == "local_ltr_registered_on"


def test_year_resolver_uses_exact_workbook_sheet_without_dl_year_inference() -> None:
    resolver = PublicFolderYearResolver(
        project_repository=_Projects(_project(project_no="DL-2026-06-001", created_on=None)),
        ltr_repository=_Ltrs(),
        workbook_lookup=_Workbook("2024"),
    )

    result = resolver.resolve("P1")

    assert result.year == 2024
    assert result.source == "ltr_workbook_sheet_year"


def test_year_resolver_falls_back_to_project_creation_date() -> None:
    resolver = PublicFolderYearResolver(
        project_repository=_Projects(_project(created_on=date(2023, 1, 2))),
        ltr_repository=_Ltrs(),
        workbook_lookup=_Workbook(None),
    )

    result = resolver.resolve("P1")

    assert result.year == 2023
    assert result.source == "project_created_on"


def test_year_resolver_blocks_when_no_authority_exists() -> None:
    resolver = PublicFolderYearResolver(
        project_repository=_Projects(_project(created_on=None)),
        ltr_repository=_Ltrs(),
        workbook_lookup=None,
    )

    result = resolver.resolve("P1")

    assert result.year is None
    assert result.requires_human_confirmation is True
    assert result.blockers


def _project(
    *,
    project_no: str | None = None,
    created_on: date | None = date(2022, 1, 1),
) -> Project:
    return Project(
        project_id="P1",
        project_no=project_no,
        product_name="Product",
        requestor="User",
        status=ProjectStatus.LTR_REGISTERED,
        created_on=created_on,
    )


class _Projects:
    def __init__(self, project: Project) -> None:
        self._project = project

    def get(self, project_id: str) -> Project | None:
        return self._project if project_id == self._project.project_id else None


class _Ltrs:
    def __init__(self, *ltrs: LtrRecord) -> None:
        self._ltrs = list(ltrs)

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        return [ltr for ltr in self._ltrs if ltr.project_id == project_id]


class _Workbook:
    def __init__(self, sheet_name: str | None) -> None:
        self._sheet_name = sheet_name

    def find_sheet_name(self, ltr_number: str) -> str | None:
        return self._sheet_name
