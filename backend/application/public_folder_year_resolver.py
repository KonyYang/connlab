"""Resolve the public-folder workflow year without inferring from DL text."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from backend.domain import LtrRecord, Project


class PublicFolderYearProjectPort(Protocol):
    """Project lookup required by the public-folder year resolver."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by id."""


class PublicFolderYearLtrPort(Protocol):
    """LTR lookup required by the public-folder year resolver."""

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        """Return LTR rows for the project."""


class LtrWorkbookSheetLookupPort(Protocol):
    """Read-only workbook sheet lookup by exact DL number."""

    def find_sheet_name(self, ltr_number: str) -> str | None:
        """Return the exact DL row sheet name, or None."""


@dataclass(frozen=True, slots=True)
class PublicFolderYearResolution:
    """Resolved public folder year and supporting evidence."""

    year: int | None
    source: str
    evidence: str | None
    warnings: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    requires_human_confirmation: bool = False


class PublicFolderYearResolver:
    """Resolve public folder year from approved authority sources."""

    def __init__(
        self,
        *,
        project_repository: PublicFolderYearProjectPort,
        ltr_repository: PublicFolderYearLtrPort,
        workbook_lookup: LtrWorkbookSheetLookupPort | None = None,
    ) -> None:
        """Create the resolver."""
        self._projects = project_repository
        self._ltrs = ltr_repository
        self._workbook_lookup = workbook_lookup

    def resolve(self, project_id: str) -> PublicFolderYearResolution:
        """Resolve year by local LTR date, workbook sheet, project date, then blocker."""
        project = self._projects.get(project_id)
        if project is None:
            raise LookupError(f"Project not found: {project_id}")

        ltrs = self._ltrs.list_by_project(project_id)
        by_registered = sorted(
            (ltr for ltr in ltrs if ltr.registered_on is not None),
            key=lambda ltr: ltr.registered_on,
            reverse=True,
        )
        if by_registered:
            ltr = by_registered[0]
            assert ltr.registered_on is not None
            return PublicFolderYearResolution(
                year=ltr.registered_on.year,
                source="local_ltr_registered_on",
                evidence=f"{ltr.ltr_number} registered_on {ltr.registered_on.isoformat()}",
            )

        by_requested = sorted(
            (ltr for ltr in ltrs if ltr.requested_date is not None),
            key=lambda ltr: ltr.requested_date,
            reverse=True,
        )
        if by_requested:
            ltr = by_requested[0]
            assert ltr.requested_date is not None
            return PublicFolderYearResolution(
                year=ltr.requested_date.year,
                source="local_ltr_requested_date",
                evidence=f"{ltr.ltr_number} requested_date {ltr.requested_date.isoformat()}",
            )

        workbook_resolution = self._workbook_year(ltrs, project.project_no)
        if workbook_resolution is not None:
            return workbook_resolution

        if project.created_on is not None:
            return PublicFolderYearResolution(
                year=project.created_on.year,
                source="project_created_on",
                evidence=project.created_on.isoformat(),
            )

        return PublicFolderYearResolution(
            year=None,
            source="human_confirmation_required",
            evidence=None,
            blockers=("Public folder year could not be resolved from local LTR, workbook sheet, or project creation date.",),
            requires_human_confirmation=True,
        )

    def _workbook_year(
        self,
        ltrs: list[LtrRecord],
        project_no: str | None,
    ) -> PublicFolderYearResolution | None:
        if self._workbook_lookup is None:
            return None
        candidates = [ltr.ltr_number for ltr in ltrs]
        if project_no:
            candidates.append(project_no)
        for ltr_number in tuple(dict.fromkeys(candidates)):
            sheet_name = self._workbook_lookup.find_sheet_name(ltr_number)
            if sheet_name is None:
                continue
            if sheet_name.isdigit() and len(sheet_name) == 4:
                return PublicFolderYearResolution(
                    year=int(sheet_name),
                    source="ltr_workbook_sheet_year",
                    evidence=f"{ltr_number} found on workbook sheet {sheet_name}",
                )
            return PublicFolderYearResolution(
                year=None,
                source="ltr_workbook_sheet_unusable",
                evidence=f"{ltr_number} found on workbook sheet {sheet_name}",
                blockers=("LTR workbook sheet year is not a four-digit year.",),
                requires_human_confirmation=True,
            )
        return None
