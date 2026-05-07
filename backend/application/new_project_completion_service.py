"""Thin orchestration for completing the New Project single-page workflow."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Protocol

from backend.application.folder_service import (
    FolderCommand,
    FolderGenerationRecord,
    FolderService,
)
from backend.application.intake_confirmation_service import (
    IntakeConfirmationResult,
    IntakeConfirmationService,
)
from backend.application.ltr_local_commit_service import (
    CommitLocalLtrCommand,
    LtrLocalCommitResult,
    LtrLocalCommitService,
)
from backend.application.ltr_registration_preview_service import (
    LtrPreviewMode,
    LtrRegistrationType,
)
from backend.domain import IntakeCase, LtrRecord, LtrStatus, Project, ProjectStatus
from backend.modules.folder import FolderPlan
from backend.modules.ltr import LtrNumberError, next_monthly_dl_number, parse_ltr_number


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
    """Input command for one-action New Project completion."""

    case_id: str
    ltr_mode: NewProjectLtrMode
    specified_ltr_number: str | None = None
    folder_template_path: Path | None = None
    folder_target_root: Path | None = None
    operator_confirmed: bool = True
    plan_date: date | None = None
    test_item: str | None = None
    sample_description: str | None = None
    location: str | None = None
    test_type_in_sheet: str | None = None
    project_leader: str | None = None


@dataclass(frozen=True, slots=True)
class NewProjectCompletionResult:
    """Result returned after project, LTR, and folder creation are complete."""

    project: Project
    ltr: LtrRecord
    folder: FolderGenerationRecord
    folder_preview: FolderPlan


@dataclass(frozen=True, slots=True)
class ExistingLtrCommitResult:
    """Compatibility result for an LTR already committed before folder generation."""

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


class NewProjectCompletionService:
    """Complete the New Project workflow by coordinating existing services."""

    def __init__(
        self,
        *,
        intake_case_store: IntakeCaseStore,
        project_store: ProjectStore,
        ltr_store: LtrRecordStore,
        confirmation_service: IntakeConfirmationService,
        ltr_commit_service: LtrLocalCommitService,
        folder_service: FolderService,
        default_folder_template_path: Path,
        default_folder_target_root: Path,
    ) -> None:
        self._intake_cases = intake_case_store
        self._projects = project_store
        self._ltrs = ltr_store
        self._confirmation = confirmation_service
        self._ltr_commit = ltr_commit_service
        self._folders = folder_service
        self._default_template = default_folder_template_path
        self._default_target_root = default_folder_target_root

    def complete(self, command: CompleteNewProjectCommand) -> NewProjectCompletionResult:
        """Confirm intake data, commit LTR, preview folder, and generate folder."""
        self._validate_setup_confirmation(command)
        project = self._confirm_or_load_project(command.case_id)
        project = self._ensure_ltr_ready_status(project)
        ltr_result = self._commit_or_load_ltr(project, command)
        folder_command = self._folder_command(command, ltr_result.ltr.ltr_number)
        folder_preview = self._folders.preview_folder(project.project_id, folder_command)
        if folder_preview.conflict or any(item.conflict for item in folder_preview.items):
            raise NewProjectCompletionError(
                f"Project folder target already exists: {folder_preview.project_folder_path}"
            )
        folder = self._folders.generate_folder(project.project_id, folder_command)
        final_project = self._projects.get(project.project_id) or project
        return NewProjectCompletionResult(
            project=final_project,
            ltr=ltr_result.ltr,
            folder=folder,
            folder_preview=folder_preview,
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
    ) -> LtrLocalCommitResult:
        """Commit a new LTR unless a previous partial completion already did it."""
        active_ltrs = [
            ltr
            for ltr in self._ltrs.list_by_project(project.project_id)
            if ltr.status is LtrStatus.REGISTERED
        ]
        if active_ltrs:
            if len(active_ltrs) > 1:
                raise NewProjectCompletionError(
                    "Project has more than one registered LTR; open the project workbench "
                    "for correction or folder recovery."
                )
            return ExistingLtrCommitResult(active_ltrs[0])

        ltr_number = self._resolve_ltr_number(command)
        parsed = parse_ltr_number(ltr_number)
        return self._ltr_commit.commit_project(
            project.project_id,
            CommitLocalLtrCommand(
                year=parsed.year or date.today().year,
                month=parsed.month or date.today().month,
                operator_confirmed=command.operator_confirmed,
                registration_type=LtrRegistrationType.NORMAL,
                mode=LtrPreviewMode.LOCAL_ONLY,
                proposed_ltr_number=ltr_number,
                requested_by=project.requestor,
                requested_date=command.plan_date or date.today(),
                operator_note=_operator_note(command),
            ),
        )

    def _validate_setup_confirmation(self, command: CompleteNewProjectCommand) -> None:
        """Require operator-confirmed values that will map to LTR workbook fields."""
        required = {
            "Test Item": command.test_item,
            "Sample Description": command.sample_description,
            "Location": command.location,
            "Test Type in sheet": command.test_type_in_sheet,
            "Project Leader": command.project_leader,
        }
        missing = [label for label, value in required.items() if not _text(value)]
        if missing:
            raise NewProjectCompletionError(
                "Project setup confirmation is incomplete: " + ", ".join(missing)
            )

    def _resolve_ltr_number(self, command: CompleteNewProjectCommand) -> str:
        """Return the explicit LTR number to pass through existing LTR services."""
        if command.ltr_mode is NewProjectLtrMode.SPECIFIED:
            if not command.specified_ltr_number:
                raise NewProjectCompletionError("Specified LTR number is required.")
            try:
                parsed = parse_ltr_number(command.specified_ltr_number)
            except LtrNumberError as exc:
                raise NewProjectCompletionError(str(exc)) from exc
            if not parsed.is_base_monthly_dl:
                raise NewProjectCompletionError(
                    "Specified LTR number must use DL-YYYY-MM-NNN format."
                )
            return parsed.normalized

        today = command.plan_date or date.today()
        existing = [ltr.ltr_number for ltr in self._ltrs.search("DL-")]
        return next_monthly_dl_number(
            year=today.year,
            month=today.month,
            existing_numbers=existing,
        )

    def _folder_command(
        self,
        command: CompleteNewProjectCommand,
        ltr_number: str,
    ) -> FolderCommand:
        """Build the existing folder service command with defaults."""
        return FolderCommand(
            template_path=command.folder_template_path or self._default_template,
            target_root=command.folder_target_root or self._default_target_root,
            dl_number=ltr_number,
            plan_date=command.plan_date or date.today(),
        )


def _operator_note(command: CompleteNewProjectCommand) -> str:
    """Build audit context for values that will later map to LTR.xls."""
    payload = {
        "source": "new_project_setup_confirmation",
        "test_item": _text(command.test_item),
        "sample_description": _text(command.sample_description),
        "location": _text(command.location),
        "test_type_in_sheet": _text(command.test_type_in_sheet),
        "project_leader": _text(command.project_leader),
    }
    return json.dumps(payload, ensure_ascii=True, sort_keys=True)


def _text(value: str | None) -> str | None:
    """Return stripped non-empty text."""
    if value is None:
        return None
    text = value.strip()
    return text or None
