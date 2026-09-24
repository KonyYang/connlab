"""Commit LTR workbook writes through the locked transaction gateway."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Protocol

from backend.application.ltr_service import LtrService, RegisterLtrCommand
from backend.application.ltr_duplicate_resolution_service import (
    DuplicateResolutionCommand,
    LocalLtrDuplicateResolutionService,
)
from backend.application.ltr_workbook_write_preview_service import (
    LtrWorkbookWritePreviewError,
    LtrWorkbookWritePreviewService,
    PreviewLtrWorkbookWriteCommand,
)
from backend.application.specified_ltr_workbook_authority_preview_service import (
    SpecifiedLtrWorkbookAuthorityPreviewAck,
    _proposed_fingerprint,
    _proposed_row_values,
    _row_fingerprint,
    _row_values,
)
from backend.domain import LtrRecord, LtrStatus, Project
from backend.infrastructure.office import (
    LtrWorkbookDropdownEnsureResult,
    LtrWorkbookExistingRow,
    LtrWorkbookRowPointer,
    LtrWorkbookTransactionGateway,
)
from backend.modules.ltr import (
    LtrNumberError,
    base_ltr_number,
    is_alphanumeric_ltr_suffix_token,
    next_monthly_dl_number,
    parse_ltr_number,
)


class LtrWorkbookWriteCommitError(ValueError):
    """Raised when an LTR workbook write commit cannot proceed."""


class LtrWorkbookTransactionGatewayPort(Protocol):
    """Transaction gateway behavior required by the commit service."""

    def run_short_transaction(self, operation):
        """Run one locked workbook transaction and save if the operation succeeds."""


class LtrServicePort(Protocol):
    """LTR local registration behavior required after workbook save."""

    def register_ltr(self, project_id: str, command: RegisterLtrCommand) -> LtrRecord:
        """Register the committed LTR in local storage."""


class LtrRecordStore(Protocol):
    """Local LTR lookup behavior required before workbook write."""

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        """Return local LTR records for one project."""


class ProjectStore(Protocol):
    """Project lookup behavior required for duplicate confirmation."""

    def get(self, project_id: str) -> Project | None:
        """Return one project by ID."""


@dataclass(frozen=True, slots=True)
class CommitLtrWorkbookWriteCommand:
    """Input command for a confirmed external workbook write commit."""

    plan_date: date
    operator_confirmed: bool
    preview_acknowledged: bool
    allow_year_sheet_bootstrap: bool = False
    number_input: str | None = None
    test_item: str = ""
    sample_description: str = ""
    location: str = ""
    test_type_in_sheet: str = ""
    project_leader: str = ""
    requested_by: str | None = None
    requested_date: date | None = None
    operator_note: str | None = None
    current_case_id: str | None = None
    duplicate_resolution: DuplicateResolutionCommand | None = None
    specified_ltr_workbook_preview_ack: SpecifiedLtrWorkbookAuthorityPreviewAck | None = None


@dataclass(frozen=True, slots=True)
class LtrWorkbookWriteCommitResult:
    """Result of one committed LTR workbook write."""

    ltr: LtrRecord
    pointer: LtrWorkbookRowPointer
    action: str
    workbook_path: Path
    backup_path: Path
    ltr_number: str


@dataclass(frozen=True, slots=True)
class LtrWorkbookYearSheetBootstrapPolicy:
    """Policy for controlled annual-sheet bootstrap during workbook commit."""

    allow_system_assisted_create_year_sheet: bool = False
    require_operator_confirmation_for_year_sheet_bootstrap: bool = True
    template_sheet_name: str | None = None
    sheet_bootstrap_clear_start_row: int = 2


@dataclass(frozen=True, slots=True)
class _NumberDecision:
    """Resolved workbook write decision."""

    ltr_number: str
    action: str
    target_sheet: str
    existing_row: LtrWorkbookExistingRow | None = None


class LtrWorkbookWriteCommitService:
    """Commit an operator-confirmed LTR workbook write and local LTR record."""

    def __init__(
        self,
        *,
        preview_service: LtrWorkbookWritePreviewService,
        transaction_gateway: LtrWorkbookTransactionGatewayPort | LtrWorkbookTransactionGateway,
        ltr_service: LtrServicePort | LtrService,
        ltr_store: LtrRecordStore,
        project_store: ProjectStore | None = None,
        duplicate_resolution_service: LocalLtrDuplicateResolutionService | None = None,
        year_sheet_bootstrap_policy: LtrWorkbookYearSheetBootstrapPolicy = (
            LtrWorkbookYearSheetBootstrapPolicy()
        ),
    ) -> None:
        """Create the commit service."""
        self._preview = preview_service
        self._transaction = transaction_gateway
        self._ltr_service = ltr_service
        self._ltr_store = ltr_store
        self._projects = project_store
        self._duplicates = duplicate_resolution_service
        self._bootstrap_policy = year_sheet_bootstrap_policy

    def commit_project(
        self,
        project_id: str,
        command: CommitLtrWorkbookWriteCommand,
    ) -> LtrWorkbookWriteCommitResult:
        """Write the workbook row, save, and register the local LTR record."""
        _validate_confirmation(command)
        _reject_existing_local_ltr(self._ltr_store.list_by_project(project_id))

        def _operation(context):
            sheet_names = _annual_sheet_names(context.session.list_sheets())
            decision = _resolve_number_decision(
                context.session,
                command,
                sheet_names,
                self._bootstrap_policy,
            )
            _verify_specified_ltr_intent(context.session, decision, command)
            if self._duplicates is not None:
                project = self._projects.get(project_id) if self._projects is not None else None
                if project is None:
                    raise LtrWorkbookWriteCommitError(
                        "Project not found for local LTR duplicate confirmation."
                    )
                self._duplicates.ensure_no_conflict_or_valid_confirmation(
                    ltr_number=decision.ltr_number,
                    current_project=project,
                    current_case_id=command.current_case_id or project_id,
                    resolution=command.duplicate_resolution,
                )
            try:
                preview = self._preview.preview_project(
                    project_id,
                    PreviewLtrWorkbookWriteCommand(
                        ltr_number=decision.ltr_number,
                        plan_date=command.plan_date,
                        test_item=command.test_item,
                        sample_description=command.sample_description,
                        location=command.location,
                        test_type_in_sheet=command.test_type_in_sheet,
                        project_leader=command.project_leader,
                    ),
                )
            except LtrWorkbookWritePreviewError as exc:
                raise LtrWorkbookWriteCommitError(str(exc)) from exc
            _verify_proposed_row_intent(preview.row_data, decision, command)
            context.session.prepare_sheet_for_operation(
                decision.target_sheet,
                mode="write",
            )
            dropdown_result = context.session.ensure_location_dropdown_value(
                decision.target_sheet,
                preview.row_data.location or "",
                row_number=(
                    decision.existing_row.row_number
                    if decision.existing_row is not None
                    else None
                ),
            )
            if decision.existing_row is not None:
                pointer = context.session.write_registration_row(
                    decision.existing_row.sheet_name,
                    decision.existing_row.row_number,
                    preview.row_data,
                )
            else:
                pointer = context.session.append_registration_row(
                    decision.target_sheet,
                    preview.row_data,
                )
            return (
                decision,
                pointer,
                context.workbook_path,
                context.backup_path,
                dropdown_result,
            )

        decision, pointer, workbook_path, backup_path, dropdown_result = (
            self._transaction.run_short_transaction(_operation)
        )
        ltr = self._ltr_service.register_ltr(
            project_id,
            RegisterLtrCommand(
                ltr_number=pointer.dl_number,
                requested_by=command.requested_by,
                requested_date=command.requested_date or command.plan_date,
                notes=_audit_notes(command, decision, pointer, backup_path, dropdown_result),
                current_case_id=command.current_case_id,
                duplicate_resolution=command.duplicate_resolution,
            ),
        )
        return LtrWorkbookWriteCommitResult(
            ltr=ltr,
            pointer=pointer,
            action=decision.action,
            workbook_path=workbook_path,
            backup_path=backup_path,
            ltr_number=pointer.dl_number,
        )


def _validate_confirmation(command: CommitLtrWorkbookWriteCommand) -> None:
    """Require both preview acknowledgement and final operator confirmation."""
    if not command.preview_acknowledged:
        raise LtrWorkbookWriteCommitError("LTR workbook write preview must be acknowledged.")
    if not command.operator_confirmed:
        raise LtrWorkbookWriteCommitError("Operator confirmation is required.")


def _reject_existing_local_ltr(records: list[LtrRecord]) -> None:
    """Reject workbook writes when the project already has an active local LTR."""
    if any(record.status is LtrStatus.REGISTERED for record in records):
        raise LtrWorkbookWriteCommitError("Project already has an active registered LTR.")


def _verify_specified_ltr_intent(session, decision: _NumberDecision, command) -> None:
    """Revalidate preview intent against locked workbook state before writing."""
    ack = command.specified_ltr_workbook_preview_ack
    if ack is None:
        return
    if (
        not ack.acknowledged
        or ack.ltr_number != decision.ltr_number
        or not ack.preview_token
        or not ack.proposed_fingerprint
    ):
        raise LtrWorkbookWriteCommitError(
            "Specified LTR preview authorization is invalid; refresh before applying."
        )
    if ack.action != decision.action:
        raise LtrWorkbookWriteCommitError(
            "Specified LTR action changed after preview; refresh before applying."
        )

    if ack.action == "replace_existing":
        row = decision.existing_row
        if row is None or (
            row.sheet_name != ack.sheet_name
            or row.row_number != ack.row_number
            or _row_fingerprint(
                ltr_number=row.dl_number,
                sheet_name=row.sheet_name,
                row_number=row.row_number,
                values=_row_values(row),
                workbook_values=row.values,
            )
            != ack.row_fingerprint
        ):
            raise LtrWorkbookWriteCommitError(
                "LTR workbook row changed after preview; refresh before replacing it."
            )
        return

    if ack.action != "append_associated":
        raise LtrWorkbookWriteCommitError(
            "Unsupported specified LTR preview action; refresh before applying."
        )
    if decision.existing_row is not None:
        raise LtrWorkbookWriteCommitError(
            "Associated LTR now exists in the workbook; refresh before applying."
        )
    base_number = base_ltr_number(decision.ltr_number)
    if ack.base_ltr_number != base_number:
        raise LtrWorkbookWriteCommitError(
            "Associated base LTR does not match the confirmed preview."
        )
    annual_sheets = _annual_sheet_names(session.list_sheets())
    if session.find_ltr_number(decision.ltr_number, annual_sheets) is not None:
        raise LtrWorkbookWriteCommitError(
            "Associated LTR now exists in the workbook; refresh before applying."
        )
    base_row = session.find_ltr_number(base_number, annual_sheets)
    if base_row is None:
        raise LtrWorkbookWriteCommitError(
            f"Associated base LTR does not exist in the workbook: {base_number}"
        )
    base_fingerprint = _row_fingerprint(
        ltr_number=base_row.dl_number,
        sheet_name=base_row.sheet_name,
        row_number=base_row.row_number,
        values=_row_values(base_row),
        workbook_values=base_row.values,
    )
    if (
        base_row.sheet_name != ack.base_ltr_number[3:7]
        or base_row.sheet_name != ack.base_sheet_name
        or base_row.row_number != ack.base_row_number
        or base_fingerprint != ack.base_fingerprint
        or base_fingerprint != ack.row_fingerprint
    ):
        raise LtrWorkbookWriteCommitError(
            "Associated base LTR changed after preview; refresh before appending."
        )


def _verify_proposed_row_intent(row_data, decision: _NumberDecision, command) -> None:
    """Ensure the row written is exactly the row shown in the confirmed preview."""
    ack = command.specified_ltr_workbook_preview_ack
    if ack is None:
        return
    proposed = _proposed_fingerprint(
        decision.ltr_number,
        _proposed_row_values(row_data),
        row_data,
    )
    if proposed != ack.proposed_fingerprint:
        raise LtrWorkbookWriteCommitError(
            "Proposed LTR row changed after preview; refresh before applying."
        )


def _resolve_number_decision(
    session,
    command: CommitLtrWorkbookWriteCommand,
    sheet_names: tuple[str, ...],
    bootstrap_policy: LtrWorkbookYearSheetBootstrapPolicy,
) -> _NumberDecision:
    """Resolve final number and write action from operator input and workbook state."""
    target_sheet = f"{command.plan_date.year:04d}"
    raw_input = (command.number_input or "").strip()
    if not raw_input:
        sheet_names = _ensure_target_sheet(
            session, command, sheet_names, target_sheet, bootstrap_policy
        )
        return _auto_base_decision(session, command, sheet_names, target_sheet)
    try:
        parsed = parse_ltr_number(raw_input)
    except LtrNumberError:
        if is_alphanumeric_ltr_suffix_token(raw_input):
            sheet_names = _ensure_target_sheet(
                session, command, sheet_names, target_sheet, bootstrap_policy
            )
            return _suffix_token_decision(session, command, sheet_names, target_sheet, raw_input)
        raise LtrWorkbookWriteCommitError(
            "Specified LTR input must be a DL number or a letter-led alphanumeric suffix token."
        )
    if parsed.is_base_monthly_dl:
        existing = session.find_ltr_number(parsed.normalized, sheet_names)
        if existing is None:
            raise LtrWorkbookWriteCommitError(
                f"Specified base LTR does not exist in the workbook: {parsed.normalized}"
            )
        return _NumberDecision(
            ltr_number=parsed.normalized,
            action="replace_existing",
            target_sheet=existing.sheet_name,
            existing_row=existing,
        )
    if parsed.is_associated_dl:
        exact = session.find_ltr_number(parsed.normalized, sheet_names)
        if exact is not None:
            return _NumberDecision(
                ltr_number=parsed.normalized,
                action="replace_existing",
                target_sheet=exact.sheet_name,
                existing_row=exact,
            )
        base = base_ltr_number(parsed.normalized)
        base_row = session.find_ltr_number(base, sheet_names)
        if base_row is None:
            raise LtrWorkbookWriteCommitError(
                f"Associated base LTR does not exist in the workbook: {base}"
            )
        preview_ack = command.specified_ltr_workbook_preview_ack
        if preview_ack is not None and preview_ack.action == "append_associated":
            expected_sheet = f"{parsed.year:04d}"
            if base_row.sheet_name != expected_sheet:
                raise LtrWorkbookWriteCommitError(
                    f"Associated base LTR is stored on {base_row.sheet_name}, "
                    f"but its number belongs to workbook year {expected_sheet}."
                )
            return _NumberDecision(
                ltr_number=parsed.normalized,
                action="append_associated",
                target_sheet=base_row.sheet_name,
            )
        sheet_names = _ensure_target_sheet(
            session, command, sheet_names, target_sheet, bootstrap_policy
        )
        _reject_duplicate(session, parsed.normalized, sheet_names)
        return _NumberDecision(
            ltr_number=parsed.normalized,
            action="append_associated",
            target_sheet=target_sheet,
        )
    raise LtrWorkbookWriteCommitError("Specified LTR number is not supported.")


def _auto_base_decision(
    session,
    command: CommitLtrWorkbookWriteCommand,
    sheet_names: tuple[str, ...],
    target_sheet: str,
) -> _NumberDecision:
    """Return the next base DL decision for the command month."""
    number = next_monthly_dl_number(
        year=command.plan_date.year,
        month=command.plan_date.month,
        existing_numbers=session.list_ltr_numbers(sheet_names),
    )
    _reject_duplicate(session, number, sheet_names)
    return _NumberDecision(number, "append_auto", target_sheet)


def _suffix_token_decision(
    session,
    command: CommitLtrWorkbookWriteCommand,
    sheet_names: tuple[str, ...],
    target_sheet: str,
    suffix: str,
) -> _NumberDecision:
    """Return an auto-base plus suffix decision."""
    base = next_monthly_dl_number(
        year=command.plan_date.year,
        month=command.plan_date.month,
        existing_numbers=session.list_ltr_numbers(sheet_names),
    )
    number = f"{base}{suffix.upper()}"
    _reject_duplicate(session, number, sheet_names)
    return _NumberDecision(number, "append_auto_suffix", target_sheet)


def _reject_duplicate(session, ltr_number: str, sheet_names: tuple[str, ...]) -> None:
    """Reject exact full-number duplicates before appending."""
    if session.find_ltr_number(ltr_number, sheet_names) is not None:
        raise LtrWorkbookWriteCommitError(
            f"LTR number already exists in the workbook: {ltr_number}"
        )


def _ensure_target_sheet(
    session,
    command: CommitLtrWorkbookWriteCommand,
    sheet_names: tuple[str, ...],
    target_sheet: str,
    bootstrap_policy: LtrWorkbookYearSheetBootstrapPolicy,
) -> tuple[str, ...]:
    """Require or bootstrap the target year sheet before appending."""
    if target_sheet in sheet_names:
        return sheet_names
    if not bootstrap_policy.allow_system_assisted_create_year_sheet:
        raise LtrWorkbookWriteCommitError(
            f"Target annual sheet is missing and must be created with operator confirmation: {target_sheet}"
        )
    if bootstrap_policy.require_operator_confirmation_for_year_sheet_bootstrap and (
        not command.operator_confirmed or not command.allow_year_sheet_bootstrap
    ):
        raise LtrWorkbookWriteCommitError(
            f"Target annual sheet is missing and requires explicit bootstrap confirmation: {target_sheet}"
        )
    template_sheet_name = bootstrap_policy.template_sheet_name
    if not template_sheet_name:
        raise LtrWorkbookWriteCommitError(
            "Year-sheet bootstrap template is not configured."
        )
    session.bootstrap_year_sheet(
        target_sheet,
        template_sheet_name=template_sheet_name,
        clear_start_row=bootstrap_policy.sheet_bootstrap_clear_start_row,
    )
    next_sheet_names = _annual_sheet_names(session.list_sheets())
    if target_sheet not in next_sheet_names:
        raise LtrWorkbookWriteCommitError(
            f"Failed to bootstrap target annual sheet: {target_sheet}"
        )
    return next_sheet_names


def _annual_sheet_names(sheet_names: list[str]) -> tuple[str, ...]:
    """Return annual workbook sheet names to scan for LTR numbers."""
    return tuple(name for name in sheet_names if re.fullmatch(r"\d{4}", str(name)))


def _audit_notes(
    command: CommitLtrWorkbookWriteCommand,
    decision: _NumberDecision,
    pointer: LtrWorkbookRowPointer,
    backup_path: Path,
    dropdown_result: LtrWorkbookDropdownEnsureResult,
) -> str:
    """Return local LTR audit notes for the committed workbook write."""
    return json.dumps(
        {
            "commit_mode": "external_ltr_workbook",
            "action": decision.action,
            "sheet_name": pointer.sheet_name,
            "row_number": pointer.row_number,
            "backup_path": str(backup_path),
            "location_dropdown_appended": dropdown_result.appended,
            "location_dropdown_appended_value": dropdown_result.appended_value,
            "location_dropdown_source_range_before": dropdown_result.source_range_before,
            "location_dropdown_source_range_after": dropdown_result.source_range_after,
            "operator_note": command.operator_note,
        },
        ensure_ascii=True,
        sort_keys=True,
    )
