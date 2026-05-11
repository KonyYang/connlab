from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.application.ltr_workbook_write_commit_service import (
    CommitLtrWorkbookWriteCommand,
    LtrWorkbookYearSheetBootstrapPolicy,
    LtrWorkbookWriteCommitError,
    LtrWorkbookWriteCommitService,
)
from backend.application.ltr_workbook_write_preview_service import (
    LtrWorkbookWritePreviewService,
)
from backend.domain import ApplicationForm, LtrRecord, LtrStatus, Project, ProjectStatus
from backend.infrastructure.office import (
    LtrWorkbookDropdownEnsureResult,
    LtrWorkbookExistingRow,
    LtrWorkbookRowPointer,
    LtrWorkbookSheetPreparationResult,
)
from backend.shared.config import LtrWorkbookSettings


def test_ltr_workbook_commit_auto_appends_next_base_number() -> None:
    """Blank number input writes the next monthly base DL number."""
    service, session, ltr_service = _service(
        {"2026": [("May", 1, 1, "DL-2026-05-001")]}
    )

    result = service.commit_project("P1", _command(number_input=None))

    assert result.action == "append_auto"
    assert result.ltr_number == "DL-2026-05-002"
    assert session.prepared_calls == [("2026", "write")]
    assert session.appended[0].dl_number == "DL-2026-05-002"
    assert session.dropdown_calls == [("2026", "Nantong", None)]
    assert ltr_service.created[0].ltr_number == "DL-2026-05-002"


def test_ltr_workbook_commit_appends_missing_location_to_dropdown_source() -> None:
    """When location is missing in dropdown source, commit appends it once."""
    service, session, ltr_service = _service(
        {"2026": [("May", 1, 1, "DL-2026-05-001")]},
        dropdown_contains_location=False,
    )

    service.commit_project("P1", _command(number_input=None))

    assert session.dropdown_calls == [("2026", "Nantong", None)]
    note = ltr_service.created[0].notes or ""
    assert '"location_dropdown_appended": true' in note
    assert '"location_dropdown_source_range_after": "=$AB$1:$AB$37"' in note


def test_ltr_workbook_commit_specified_base_replaces_existing_row() -> None:
    """A specified base number must already exist and is replaced in place."""
    service, session, _ = _service({"2026": [("May", 7, 7, "DL-2026-05-007")]})

    result = service.commit_project("P1", _command(number_input="DL-2026-05-007"))

    assert result.action == "replace_existing"
    assert result.pointer.row_number == 2
    assert session.replaced[0].dl_number == "DL-2026-05-007"


def test_ltr_workbook_commit_associated_number_requires_base_and_appends_current_year() -> None:
    """A new associated number may use a prior-year base and write to current sheet."""
    service, session, _ = _service(
        {
            "2025": [("Dec", 3, 3, "DL-2025-12-003")],
            "2026": [("May", 1, 1, "DL-2026-05-001")],
        }
    )

    result = service.commit_project("P1", _command(number_input="DL-2025-12-003A9"))

    assert result.action == "append_associated"
    assert result.pointer.sheet_name == "2026"
    assert result.ltr_number == "DL-2025-12-003A9"


def test_ltr_workbook_commit_suffix_token_auto_allocates_base_and_suffix() -> None:
    """Alphanumeric token input appends to an auto-allocated base DL number."""
    service, session, _ = _service({"2026": [("May", 1, 1, "DL-2026-05-001")]})

    result = service.commit_project("P1", _command(number_input="AA"))

    assert result.action == "append_auto_suffix"
    assert result.ltr_number == "DL-2026-05-002AA"
    assert session.appended[0].dl_number == "DL-2026-05-002AA"


def test_ltr_workbook_commit_rejects_associated_number_when_base_missing() -> None:
    """Associated specified input requires an existing base number in workbook."""
    service, _, _ = _service({"2026": [("May", 1, 1, "DL-2026-05-001")]})

    with pytest.raises(LtrWorkbookWriteCommitError, match="Associated base LTR does not exist"):
        service.commit_project("P1", _command(number_input="DL-2025-12-003A9"))


def test_ltr_workbook_commit_associated_existing_full_replaces_across_year_sheets() -> None:
    """Associated full number uses replacement when already present in scanned annual sheets."""
    service, _, _ = _service(
        {
            "2025": [("Dec", 3, 3, "DL-2025-12-003A9")],
            "2026": [("May", 1, 1, "DL-2026-05-001")],
        }
    )

    result = service.commit_project("P1", _command(number_input="DL-2025-12-003A9"))
    assert result.action == "replace_existing"
    assert result.pointer.sheet_name == "2025"


def test_ltr_workbook_commit_rejects_invalid_specified_input() -> None:
    """Non-letter-led token and non-DL inputs are rejected."""
    service, _, _ = _service({"2026": []})

    with pytest.raises(
        LtrWorkbookWriteCommitError,
        match="DL number or a letter-led alphanumeric",
    ):
        service.commit_project("P1", _command(number_input="A-9"))

    with pytest.raises(
        LtrWorkbookWriteCommitError,
        match="DL number or a letter-led alphanumeric",
    ):
        service.commit_project("P1", _command(number_input="123"))

    with pytest.raises(
        LtrWorkbookWriteCommitError,
        match="DL number or a letter-led alphanumeric",
    ):
        service.commit_project("P1", _command(number_input="DL-2026-05-003123"))


def test_ltr_workbook_commit_rejects_missing_specified_base() -> None:
    """Specified base numbers cannot create arbitrary missing workbook numbers."""
    service, _, _ = _service({"2026": []})

    with pytest.raises(LtrWorkbookWriteCommitError, match="does not exist"):
        service.commit_project("P1", _command(number_input="DL-2026-05-007"))


def test_ltr_workbook_commit_requires_target_year_sheet_for_append() -> None:
    """Missing annual sheets block append writes instead of creating silently."""
    service, _, _ = _service({"2025": [("Dec", 1, 1, "DL-2025-12-001")]})

    with pytest.raises(LtrWorkbookWriteCommitError, match="annual sheet is missing"):
        service.commit_project("P1", _command(number_input=None))


def test_ltr_workbook_commit_bootstraps_missing_year_sheet_when_confirmed() -> None:
    """Missing annual sheets can be bootstrapped when policy and confirmation allow it."""
    service, session, _ = _service(
        {"2025": [("Dec", 1, 1, "DL-2025-12-001")]},
        bootstrap_policy=LtrWorkbookYearSheetBootstrapPolicy(
            allow_system_assisted_create_year_sheet=True,
            require_operator_confirmation_for_year_sheet_bootstrap=True,
            template_sheet_name="2025",
            sheet_bootstrap_clear_start_row=2,
        ),
    )

    result = service.commit_project(
        "P1",
        _command(number_input=None, allow_year_sheet_bootstrap=True),
    )

    assert result.pointer.sheet_name == "2026"
    assert session.bootstrap_calls == [("2026", "2025", 2)]


def test_ltr_workbook_commit_rejects_bootstrap_without_explicit_confirmation() -> None:
    """Bootstrap policy still requires explicit operator bootstrap acknowledgement."""
    service, _, _ = _service(
        {"2025": [("Dec", 1, 1, "DL-2025-12-001")]},
        bootstrap_policy=LtrWorkbookYearSheetBootstrapPolicy(
            allow_system_assisted_create_year_sheet=True,
            require_operator_confirmation_for_year_sheet_bootstrap=True,
            template_sheet_name="2025",
            sheet_bootstrap_clear_start_row=2,
        ),
    )

    with pytest.raises(LtrWorkbookWriteCommitError, match="explicit bootstrap confirmation"):
        service.commit_project("P1", _command(number_input=None, allow_year_sheet_bootstrap=False))


def test_ltr_workbook_commit_requires_operator_confirmation() -> None:
    """Commit requires explicit preview acknowledgement and final confirmation."""
    service, _, _ = _service({"2026": []})

    with pytest.raises(LtrWorkbookWriteCommitError, match="preview"):
        service.commit_project("P1", _command(preview_acknowledged=False))
    with pytest.raises(LtrWorkbookWriteCommitError, match="Operator confirmation"):
        service.commit_project("P1", _command(operator_confirmed=False))


def test_ltr_workbook_commit_rejects_unmapped_project_type() -> None:
    """Commit is blocked when project type has no workbook mapping."""
    service, _, _ = _service(
        {"2026": []},
        project_type="Unknown Type",
    )

    with pytest.raises(
        LtrWorkbookWriteCommitError,
        match="Project Type has no LTR workbook mapping: Unknown Type",
    ):
        service.commit_project("P1", _command(number_input=None))


def _command(
    *,
    number_input: str | None = None,
    operator_confirmed: bool = True,
    preview_acknowledged: bool = True,
    allow_year_sheet_bootstrap: bool = False,
) -> CommitLtrWorkbookWriteCommand:
    """Return a complete commit command."""
    return CommitLtrWorkbookWriteCommand(
        plan_date=date(2026, 5, 7),
        operator_confirmed=operator_confirmed,
        preview_acknowledged=preview_acknowledged,
        allow_year_sheet_bootstrap=allow_year_sheet_bootstrap,
        number_input=number_input,
        test_item="Qualification bend testing",
        sample_description="CoolPower connector samples",
        location="AIPG Guangzhou",
        test_type_in_sheet="Qualification",
        project_leader="Alice",
        requested_by="Alice",
    )


def _service(
    rows_by_sheet: dict[str, list[tuple[object, ...]]],
    *,
    bootstrap_policy: LtrWorkbookYearSheetBootstrapPolicy = (
        LtrWorkbookYearSheetBootstrapPolicy()
    ),
    project_type: str = "New Product Development",
    dropdown_contains_location: bool = True,
):
    """Return service and fakes for one commit test."""
    session = _FakeWorkbookSession(
        rows_by_sheet,
        dropdown_contains_location=dropdown_contains_location,
    )
    transaction = _FakeTransactionGateway(session)
    ltr_service = _FakeLtrService()
    service = LtrWorkbookWriteCommitService(
        preview_service=LtrWorkbookWritePreviewService(
            project_store=_ProjectStore(),
            application_form_store=_FormStore(project_type=project_type),
            sample_store=_SampleStore(),
            workbook_settings=LtrWorkbookSettings(path=Path("LTR_number.xls")),
        ),
        transaction_gateway=transaction,
        ltr_service=ltr_service,
        ltr_store=_LtrStore(),
        year_sheet_bootstrap_policy=bootstrap_policy,
    )
    return service, session, ltr_service


class _FakeTransactionGateway:
    def __init__(self, session: "_FakeWorkbookSession") -> None:
        self._session = session

    def run_short_transaction(self, operation):
        context = SimpleNamespace(
            session=self._session,
            workbook_path=Path("LTR_number.xls"),
            backup_path=Path("backups/LTR_number.xls"),
        )
        result = operation(context)
        self._session.saved = True
        return result


class _FakeWorkbookSession:
    def __init__(
        self,
        rows_by_sheet: dict[str, list[tuple[object, ...]]],
        *,
        dropdown_contains_location: bool = True,
    ) -> None:
        self.rows_by_sheet = rows_by_sheet
        self.appended: list[LtrWorkbookRowPointer] = []
        self.replaced: list[LtrWorkbookRowPointer] = []
        self.bootstrap_calls: list[tuple[str, str, int]] = []
        self.prepared_calls: list[tuple[str, str]] = []
        self.dropdown_calls: list[tuple[str, str, int | None]] = []
        self.dropdown_contains_location = dropdown_contains_location
        self.saved = False

    def list_sheets(self) -> list[str]:
        return list(self.rows_by_sheet)

    def list_ltr_numbers(self, sheet_names: tuple[str, ...] | None = None) -> tuple[str, ...]:
        numbers: list[str] = []
        for sheet in sheet_names or tuple(self.rows_by_sheet):
            for row in self.rows_by_sheet[sheet]:
                if len(row) >= 4 and row[3]:
                    numbers.append(str(row[3]).upper())
        return tuple(numbers)

    def find_ltr_number(
        self,
        ltr_number: str,
        sheet_names: tuple[str, ...] | None = None,
    ) -> LtrWorkbookExistingRow | None:
        for sheet in sheet_names or tuple(self.rows_by_sheet):
            for index, row in enumerate(self.rows_by_sheet[sheet], start=2):
                if len(row) >= 4 and str(row[3]).upper() == ltr_number.upper():
                    return LtrWorkbookExistingRow(sheet, index, str(row[3]).upper(), row)
        return None

    def append_registration_row(self, sheet_name, row_data) -> LtrWorkbookRowPointer:
        pointer = LtrWorkbookRowPointer(
            sheet_name=sheet_name,
            row_number=len(self.rows_by_sheet[sheet_name]) + 2,
            dl_number=row_data.dl_number,
        )
        self.appended.append(pointer)
        return pointer

    def write_registration_row(self, sheet_name, row_number, row_data) -> LtrWorkbookRowPointer:
        pointer = LtrWorkbookRowPointer(sheet_name, row_number, row_data.dl_number)
        self.replaced.append(pointer)
        return pointer

    def ensure_location_dropdown_value(
        self,
        sheet_name: str,
        location: str,
        *,
        row_number: int | None = None,
    ) -> LtrWorkbookDropdownEnsureResult:
        self.dropdown_calls.append((sheet_name, location, row_number))
        if self.dropdown_contains_location:
            return LtrWorkbookDropdownEnsureResult(
                appended=False,
                appended_value=None,
                source_range_before="=$AB$1:$AB$36",
                source_range_after="=$AB$1:$AB$36",
            )
        return LtrWorkbookDropdownEnsureResult(
            appended=True,
            appended_value=location,
            source_range_before="=$AB$1:$AB$36",
            source_range_after="=$AB$1:$AB$37",
        )

    def prepare_sheet_for_operation(
        self,
        sheet_name: str,
        *,
        mode: str = "write",
    ) -> LtrWorkbookSheetPreparationResult:
        self.prepared_calls.append((sheet_name, mode))
        return LtrWorkbookSheetPreparationResult(
            sheet_name=sheet_name,
            mode=mode,
            filter_cleared=False,
            hidden_rows_detected=False,
            hidden_columns_detected=False,
            warnings=(),
        )

    def bootstrap_year_sheet(
        self,
        target_sheet_name: str,
        *,
        template_sheet_name: str,
        clear_start_row: int = 2,
    ) -> bool:
        self.bootstrap_calls.append(
            (target_sheet_name, template_sheet_name, clear_start_row)
        )
        if template_sheet_name not in self.rows_by_sheet:
            raise LtrWorkbookWriteCommitError("template sheet missing")
        self.rows_by_sheet[target_sheet_name] = []
        return True


class _FakeLtrService:
    def __init__(self) -> None:
        self.created: list[LtrRecord] = []

    def register_ltr(self, project_id: str, command) -> LtrRecord:
        record = LtrRecord(
            ltr_id=f"L{len(self.created) + 1}",
            project_id=project_id,
            ltr_number=command.ltr_number,
            status=LtrStatus.REGISTERED,
            requested_by=command.requested_by,
            requested_date=command.requested_date,
            notes=command.notes,
        )
        self.created.append(record)
        return record


class _LtrStore:
    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        return []


class _ProjectStore:
    def get(self, project_id: str) -> Project | None:
        return Project(
            project_id=project_id,
            project_no=None,
            product_name="Connector",
            requestor="Alice",
            status=ProjectStatus.CONFIRMED,
        )


class _FormStore:
    def __init__(
        self,
        *,
        project_type: str = "New Product Development",
        manufacturing_site: str = "Nantong",
    ) -> None:
        self._project_type = project_type
        self._manufacturing_site = manufacturing_site

    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        return [
            ApplicationForm(
                form_id="F1",
                project_id=project_id,
                form_no="E-3718",
                revision="H",
                requester="Alice",
                project_type=self._project_type,
                manufacturing_site=self._manufacturing_site,
                post_testing_disposition="Keep in the Lab",
                subcontract_allowed=False,
                additional_information="PO pending",
            )
        ]


class _SampleStore:
    def list_by_project(self, project_id: str):
        return []
