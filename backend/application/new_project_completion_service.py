"""Thin orchestration for completing the New Project single-page workflow."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import date
from enum import StrEnum
from typing import Protocol

from backend.application.intake_confirmation_service import (
    IntakeConfirmationResult,
    IntakeConfirmationService,
)
from backend.application.ltr_authority import (
    CommitLtrAuthorityCommand,
    LtrAuthorityCommitResult,
    LtrAuthorityPort,
)
from backend.application.new_project_setup_policy import normalize_lab_performing_tests
from backend.domain import ApplicationForm, IntakeCase, LtrRecord, LtrStatus, Project, ProjectStatus
from backend.modules.ltr import LtrNumberError, parse_ltr_number


class NewProjectCompletionError(ValueError):
    """Raised when New Project completion cannot proceed."""


class NewProjectCompletionNotFoundError(LookupError):
    """Raised when New Project completion prerequisites are missing."""


class NewProjectLtrMode(StrEnum):
    """LTR number modes exposed by the New Project completion UI."""

    AUTO = "auto"
    SPECIFIED = "specified"


@dataclass(frozen=True, slots=True)
class CompleteNewProjectCommand:
    """Input command for New Project LTR application."""

    case_id: str
    ltr_mode: NewProjectLtrMode
    specified_ltr_number: str | None = None
    operator_confirmed: bool = True
    plan_date: date | None = None
    test_item: str | None = None
    sample_description: str | None = None
    location: str | None = None
    test_type_in_sheet: str | None = None
    project_leader: str | None = None
    lab_performing_tests: str | None = None


@dataclass(frozen=True, slots=True)
class NewProjectCompletionResult:
    """Result returned after project creation and LTR application."""

    project: Project
    ltr: LtrRecord
    workbook_path: str | None = None
    workbook_sheet_name: str | None = None
    workbook_row_number: int | None = None
    workbook_backup_path: str | None = None


@dataclass(frozen=True, slots=True)
class ExistingLtrCommitResult:
    """Compatibility result for an LTR already applied to the project."""

    ltr: LtrRecord


class IntakeCaseStore(Protocol):
    """Intake case lookup behavior required by completion orchestration."""

    def get(self, case_id: str) -> IntakeCase | None:
        """Return an intake case by ID."""


class ProjectStore(Protocol):
    """Project repository behavior required by completion orchestration."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by ID."""

    def update(self, project: Project) -> Project:
        """Update a project record."""


class LtrRecordStore(Protocol):
    """LTR repository behavior required by completion orchestration."""

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        """Return LTR records for a project."""

    def search(self, query: str) -> list[LtrRecord]:
        """Search LTR records."""


class ApplicationFormStore(Protocol):
    """Application form behavior needed by New Project setup promotion."""

    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        """Return application forms for a project."""

    def update(self, form: ApplicationForm) -> ApplicationForm:
        """Update an application form."""


class NewProjectCompletionService:
    """Complete the New Project workflow by coordinating existing services."""

    def __init__(
        self,
        *,
        intake_case_store: IntakeCaseStore,
        project_store: ProjectStore,
        ltr_store: LtrRecordStore,
        application_form_store: ApplicationFormStore,
        confirmation_service: IntakeConfirmationService,
        ltr_commit_service: LtrAuthorityPort,
    ) -> None:
        self._intake_cases = intake_case_store
        self._projects = project_store
        self._ltrs = ltr_store
        self._forms = application_form_store
        self._confirmation = confirmation_service
        self._ltr_commit = ltr_commit_service

    def complete(self, command: CompleteNewProjectCommand) -> NewProjectCompletionResult:
        """Confirm intake data and apply an LTR without generating folders."""
        self._validate_setup_confirmation(command)
        project = self._confirm_or_load_project(command.case_id)
        project = self._ensure_ltr_ready_status(project)
        if not self._registered_ltrs(project):
            self._promote_setup_confirmation(project.project_id, command)
        ltr_result = self._commit_or_load_ltr(project, command)
        final_project = self._projects.get(project.project_id) or project
        return NewProjectCompletionResult(
            project=final_project,
            ltr=ltr_result.ltr,
            workbook_path=getattr(ltr_result, "workbook_path", None),
            workbook_sheet_name=getattr(ltr_result, "workbook_sheet_name", None),
            workbook_row_number=getattr(ltr_result, "workbook_row_number", None),
            workbook_backup_path=getattr(ltr_result, "workbook_backup_path", None),
        )

    def _confirm_or_load_project(self, case_id: str) -> Project:
        """Confirm the intake case once, or load its already confirmed project."""
        intake_case = self._intake_cases.get(case_id)
        if intake_case is None:
            raise NewProjectCompletionNotFoundError(f"Intake case not found: {case_id}")
        if intake_case.confirmed_project_id:
            project = self._projects.get(intake_case.confirmed_project_id)
            if project is None:
                raise NewProjectCompletionNotFoundError(
                    f"Confirmed project not found: {intake_case.confirmed_project_id}"
                )
            return project
        result: IntakeConfirmationResult = self._confirmation.confirm_case(case_id)
        return result.project

    def _ensure_ltr_ready_status(self, project: Project) -> Project:
        """Move freshly confirmed intake projects into the LTR-allowed state."""
        if project.status is ProjectStatus.INTAKE_RECEIVED:
            return self._projects.update(project.with_status(ProjectStatus.CONFIRMED))
        return project

    def _commit_or_load_ltr(
        self,
        project: Project,
        command: CompleteNewProjectCommand,
    ) -> ExistingLtrCommitResult | LtrAuthorityCommitResult:
        """Commit a new LTR unless a previous partial completion already did it."""
        active_ltrs = self._registered_ltrs(project)
        if active_ltrs:
            if len(active_ltrs) > 1:
                raise NewProjectCompletionError(
                    "Project has more than one registered LTR; open the project workbench "
                    "for correction."
                )
            return ExistingLtrCommitResult(active_ltrs[0])

        plan_date = command.plan_date or date.today()
        return self._ltr_commit.commit_project(
            project.project_id,
            CommitLtrAuthorityCommand(
                plan_date=plan_date,
                operator_confirmed=command.operator_confirmed,
                number_input=self._resolve_ltr_input(command),
                test_item=_text(command.test_item) or "",
                sample_description=_text(command.sample_description) or "",
                location=_text(command.location) or "",
                test_type_in_sheet=_text(command.test_type_in_sheet) or "",
                project_leader=_text(command.project_leader) or "",
                requested_by=project.requestor,
                requested_date=plan_date,
                operator_note=_operator_note(command),
            ),
        )

    def _registered_ltrs(self, project: Project) -> list[LtrRecord]:
        """Return registered LTRs for a project."""
        return [
            ltr
            for ltr in self._ltrs.list_by_project(project.project_id)
            if ltr.status is LtrStatus.REGISTERED
        ]

    def _promote_setup_confirmation(
        self,
        project_id: str,
        command: CompleteNewProjectCommand,
    ) -> None:
        """Persist confirmed Project setup fields into the ApplicationForm."""
        lab = normalize_lab_performing_tests(command.lab_performing_tests, required=True)
        forms = self._forms.list_by_project(project_id)
        if not forms:
            raise NewProjectCompletionError(
                "Application form not found for Project setup confirmation."
            )
        latest = forms[-1]
        self._forms.update(
            replace(
                latest,
                lab=lab,
                assigned_personnel=_text(command.project_leader) or "",
            )
        )

    def _validate_setup_confirmation(self, command: CompleteNewProjectCommand) -> None:
        """Require operator-confirmed values that will map to LTR workbook fields."""
        required = {
            "Test Item": command.test_item,
            "Sample Description": command.sample_description,
            "Test Type in sheet": command.test_type_in_sheet,
            "Project Leader": command.project_leader,
            "Lab Performing the Tests": command.lab_performing_tests,
        }
        missing = [label for label, value in required.items() if not _text(value)]
        if missing:
            raise NewProjectCompletionError(
                "Project setup confirmation is incomplete: " + ", ".join(missing)
            )
        try:
            normalize_lab_performing_tests(command.lab_performing_tests, required=True)
        except ValueError as exc:
            raise NewProjectCompletionError(str(exc)) from exc

    def _resolve_ltr_input(self, command: CompleteNewProjectCommand) -> str | None:
        """Resolve operator LTR number input for workbook-authority commit."""
        if command.ltr_mode is NewProjectLtrMode.SPECIFIED:
            if not command.specified_ltr_number:
                raise NewProjectCompletionError("Specified LTR number is required.")
            try:
                parsed = parse_ltr_number(command.specified_ltr_number)
            except LtrNumberError as exc:
                # Let suffix-token input pass through for TASK_137/TASK_138 behavior.
                token = command.specified_ltr_number.strip()
                if token:
                    return token
                raise NewProjectCompletionError(str(exc)) from exc
            return parsed.normalized

        return None

def _operator_note(command: CompleteNewProjectCommand) -> str:
    """Build audit context for values that will later map to LTR.xls."""
    payload = {
        "source": "new_project_setup_confirmation",
        "test_item": _text(command.test_item),
        "sample_description": _text(command.sample_description),
        "location": _text(command.location),
        "test_type_in_sheet": _text(command.test_type_in_sheet),
        "project_leader": _text(command.project_leader),
        "lab_performing_tests": _text(command.lab_performing_tests),
    }
    return json.dumps(payload, ensure_ascii=True, sort_keys=True)


def _text(value: str | None) -> str | None:
    """Return stripped non-empty text."""
    if value is None:
        return None
    text = value.strip()
    return text or None
