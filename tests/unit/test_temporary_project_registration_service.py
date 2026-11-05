from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.application.temporary_project_registration_service import (
    TemporaryProjectRegistrationService, TemporaryProjectRegistrationError,
)
from backend.application.ltr_service import LtrService
from backend.application.project_lifecycle_service import ProjectLifecycleService
from backend.domain import Project, ProjectStatus, ApplicationForm
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.office import LtrWorkbookExistingRow, LtrWorkbookRowPointer


class Store:
    def __init__(self, *items):
        self.items = list(items)

    def get(self, identity):
        return next((item for item in self.items if item.project_id == identity), None)

    def get_by_project(self, identity):
        return self.get(identity)

    def list_by_project(self, identity):
        return [item for item in self.items if item.project_id == identity]

    def get_latest_confirmed(self, identity):
        return next((item for item in self.items if getattr(item, 'project_id', None) == identity and getattr(item, 'status', None) == 'confirmed'), None)

    def get_latest_draft(self, identity):
        return None

    def create(self, item):
        self.items.append(item)
        return item

    def update(self, item):
        self.items = [item if old.project_id == item.project_id else old for old in self.items]
        return item

    def search(self, number):
        return [item for item in self.items if item.ltr_number == number]


class Workbook:
    """A transaction-bound file-system boundary with save/rollback behavior."""
    def __init__(self, root):
        self.path = root / 'LTR.xlsx'
        self.rows = []
        self.saved = []
        self.saves = 0
        self.fail_save = False

    @contextmanager
    def open_read_only_transaction(self):
        yield SimpleNamespace(session=self, workbook_path=self.path)

    @contextmanager
    def open_transaction(self):
        self.rows = deepcopy(self.saved)
        try:
            yield SimpleNamespace(session=self, workbook_path=self.path, backup_path=self.path.with_suffix('.bak'))
        finally:
            self.rows = deepcopy(self.saved)

    def list_sheets(self):
        return ['2026']

    def list_ltr_numbers(self, sheets):
        return [row.dl_number for row in self.rows if row.sheet_name in sheets]

    def read_annual_sheet(self, sheet):
        return tuple(row.values for row in self.rows if row.sheet_name == sheet)

    def find_ltr_number(self, number, sheets):
        return next((row for row in self.rows if row.dl_number == number and row.sheet_name in sheets), None)

    def prepare_sheet_for_operation(self, *args, **kwargs):
        pass

    def append_registration_row(self, sheet, row):
        row = replace(row, total=len(self.rows) + 1)
        found = LtrWorkbookExistingRow(sheet, len(self.rows) + 2, row.dl_number, tuple(row.as_excel_row()))
        self.rows.append(found)
        return LtrWorkbookRowPointer(sheet, found.row_number, row.dl_number)

    def write_registration_row(self, sheet, index, row):
        self.rows = [LtrWorkbookExistingRow(sheet, index, row.dl_number, tuple(row.as_excel_row())) if old.row_number == index and old.sheet_name == sheet else old for old in self.rows]
        return LtrWorkbookRowPointer(sheet, index, row.dl_number)

    def save(self):
        if self.fail_save:
            raise ValueError('Excel Save failed')
        self.saved = deepcopy(self.rows)
        self.saves += 1

    def save_transaction(self, context):
        self.save()

    def prune_transaction_backups(self, context):
        pass


def build(tmp_path, basic_information=None):
    projects = Store(Project(project_id='P1', project_no=None, product_name='Connector', requestor='Alice', status=ProjectStatus.DRAFT))
    forms, ltrs = Store(), Store()
    workbook = Workbook(tmp_path)
    journal = GenerationJournal(tmp_path / 'journal')
    service = TemporaryProjectRegistrationService(
        projects=projects, forms=forms, samples=Store(), ltrs=ltrs,
        basic_information=basic_information or Store(), temporary_context=Store(), workbook=workbook,
        journal=journal, ltr_service=LtrService(projects, ltrs, ProjectLifecycleService(projects)),
    )
    values = dict(sample_description='Connector', test_item='Qualification', requested_by='Alice',
        project_type='New Product Development', location='Nantong', test_type_in_sheet='Partial Qualification',
        project_leader='White', lab_performing_tests='Dongguan')
    return service, projects, forms, ltrs, workbook, journal, values


def test_registers_on_same_project_and_repeat_does_not_allocate_another_number(tmp_path):
    service, projects, forms, ltrs, workbook, journal, values = build(tmp_path)
    preview = service.preview('P1', values, plan_date=date(2026, 11, 5))
    assert preview['ltr_number'] == 'DL-2026-11-001'
    assert projects.get('P1').status == ProjectStatus.DRAFT
    assert forms.items == [] and workbook.saves == 0
    result = service.commit('P1', preview['preview_token'], operator_confirmed=True)
    assert result['project_id'] == 'P1'
    assert result['ltr_number'] == 'DL-2026-11-001'
    assert len(projects.items) == 1
    assert forms.items[0].manufacturing_site == 'Nantong'
    assert workbook.saved[0].values[16] == 'N/A'
    again = service.commit('P1', preview['preview_token'], operator_confirmed=True)
    assert again == result and workbook.saves == 1


def test_recovers_saved_excel_after_local_rollback_without_second_write(tmp_path):
    service, projects, forms, ltrs, workbook, journal, values = build(tmp_path)
    original = projects.get('P1')
    preview = service.preview('P1', values, plan_date=date(2026, 11, 5))
    service.commit('P1', preview['preview_token'], operator_confirmed=True)
    # Simulate API transaction commit failure and a newly constructed service/process.
    projects.items, forms.items, ltrs.items = [original], [], []
    service = TemporaryProjectRegistrationService(projects=projects, forms=forms, samples=Store(),
        ltrs=ltrs, basic_information=Store(), temporary_context=Store(), workbook=workbook,
        journal=GenerationJournal(tmp_path / 'journal'), ltr_service=LtrService(projects, ltrs, ProjectLifecycleService(projects)))
    recovered = service.commit('P1', preview['preview_token'], operator_confirmed=True)
    assert recovered['ltr_number'] == 'DL-2026-11-001'
    assert workbook.saves == 1 and len(ltrs.items) == 1


def test_auto_preview_cannot_silently_change_number_when_taken(tmp_path):
    service, _, _, _, workbook, _, values = build(tmp_path)
    preview = service.preview('P1', values, plan_date=date(2026, 11, 5))
    workbook.rows = [LtrWorkbookExistingRow('2026', 2, preview['ltr_number'], ('other',))]
    workbook.saved = deepcopy(workbook.rows)
    with pytest.raises(ValueError, match='changed|Refresh|refresh|exists'):
        service.commit('P1', preview['preview_token'], operator_confirmed=True)
    assert workbook.saves == 0
    refreshed = service.preview('P1', values, plan_date=date(2026, 11, 5))
    assert refreshed['ltr_number'] == 'DL-2026-11-002'
    assert service.commit('P1', refreshed['preview_token'], operator_confirmed=True)['ltr_number'] == 'DL-2026-11-002'


def existing(number='DL-2026-11-007'):
    return LtrWorkbookExistingRow('2026', 2, number, ('Nov', 1, 7, number, 'OPS', 'Old connector', 'Old testing',
        'Qualification', 'Bob', 'Dongguan', 'Leader', None, None, 'Scrap', 'No', None, 'N/A'))


def test_existing_number_requires_fresh_comparison_and_preserves_other_form_fields(tmp_path):
    service, _, forms, _, workbook, _, values = build(tmp_path)
    forms.items = [ApplicationForm(form_id='F1', project_id='P1', form_no='REQ-1', revision='A', requester='Alice', phone='123', post_testing_disposition='Scrap')]
    workbook.rows = workbook.saved = [existing()]
    preview = service.preview('P1', values, plan_date=date(2026, 11, 5), mode='specified', specified_number='DL-2026-11-007')
    assert preview['comparison']['status'] == 'found'
    changed = replace(existing(), values=existing().values[:5] + ('Another connector',) + existing().values[6:])
    workbook.rows = workbook.saved = [changed]
    with pytest.raises(ValueError, match='changed'):
        service.commit('P1', preview['preview_token'], operator_confirmed=True)
    refreshed = service.preview('P1', values, plan_date=date(2026, 11, 5), mode='specified', specified_number='DL-2026-11-007')
    service.commit('P1', refreshed['preview_token'], operator_confirmed=True)
    assert forms.items[0].phone == '123' and forms.items[0].post_testing_disposition == 'Scrap'
    assert workbook.saved[0].values[5] == 'Connector'


def test_associated_number_adds_separate_row_and_keeps_base_untouched(tmp_path):
    service, _, _, _, workbook, _, values = build(tmp_path)
    workbook.rows = workbook.saved = [existing()]
    preview = service.preview('P1', values, plan_date=date(2026, 11, 5), mode='specified', specified_number='DL-2026-11-007A')
    assert preview['comparison']['status'] == 'associated_candidate'
    service.commit('P1', preview['preview_token'], operator_confirmed=True)
    assert workbook.saved[0] == existing()
    assert workbook.saved[1].dl_number == 'DL-2026-11-007A'


def test_duplicate_base_introduced_after_preview_blocks_associated_append(tmp_path):
    service, _, _, _, workbook, _, values = build(tmp_path)
    workbook.rows = workbook.saved = [existing()]
    preview = service.preview('P1', values, plan_date=date(2026, 11, 5), mode='specified', specified_number='DL-2026-11-007A')
    workbook.saved.append(replace(existing(), row_number=3))
    with pytest.raises(ValueError, match='Duplicate'):
        service.commit('P1', preview['preview_token'], operator_confirmed=True)
    assert workbook.saves == 0


@pytest.mark.parametrize('mode,number', [('auto', None), ('specified', 'DL-2026-11-007')])
def test_save_failure_can_retry_original_intent(tmp_path, mode, number):
    service, projects, forms, _, workbook, _, values = build(tmp_path)
    if number:
        workbook.rows = workbook.saved = [existing()]
    preview = service.preview('P1', values, plan_date=date(2026, 11, 5), mode=mode, specified_number=number)
    workbook.fail_save = True
    with pytest.raises(ValueError, match='Save failed'):
        service.commit('P1', preview['preview_token'], operator_confirmed=True)
    assert projects.get('P1').status == ProjectStatus.DRAFT and not forms.items
    assert service.prepare('P1')['recovery_preview']['preview_token'] == preview['preview_token']
    workbook.fail_save = False
    result = service.commit('P1', preview['preview_token'], operator_confirmed=True)
    assert result['ltr_number'] == preview['ltr_number'] and workbook.saves == 1


def test_recovery_refuses_changed_saved_row_or_workbook_location(tmp_path):
    service, projects, forms, ltrs, workbook, _, values = build(tmp_path)
    original = projects.get('P1')
    preview = service.preview('P1', values, plan_date=date(2026, 11, 5))
    service.commit('P1', preview['preview_token'], operator_confirmed=True)
    projects.items, forms.items, ltrs.items = [original], [], []
    saved = workbook.saved[0]
    workbook.saved = [replace(saved, values=(*saved.values[:16], 'colleague edit'))]
    with pytest.raises(ValueError):
        service.commit('P1', preview['preview_token'], operator_confirmed=True)
    assert not ltrs.items and workbook.saves == 1
    workbook.saved = [saved]
    workbook.path = tmp_path / 'different.xlsx'
    with pytest.raises(ValueError, match='location changed'):
        service.commit('P1', preview['preview_token'], operator_confirmed=True)


def test_duplicate_excel_rows_block_even_when_first_row_matches_recovery(tmp_path):
    service, projects, forms, ltrs, workbook, _, values = build(tmp_path)
    original = projects.get('P1')
    preview = service.preview('P1', values, plan_date=date(2026, 11, 5))
    service.commit('P1', preview['preview_token'], operator_confirmed=True)
    projects.items, forms.items, ltrs.items = [original], [], []
    workbook.saved.append(replace(workbook.saved[0], row_number=3))
    with pytest.raises(ValueError, match='Duplicate'):
        service.commit('P1', preview['preview_token'], operator_confirmed=True)
    assert not ltrs.items


def test_requires_confirmation_and_refuses_changed_project_or_other_local_owner(tmp_path):
    service, projects, _, ltrs, workbook, _, values = build(tmp_path)
    preview = service.preview('P1', values, plan_date=date(2026, 11, 5))
    with pytest.raises(ValueError, match='Confirm'):
        service.commit('P1', preview['preview_token'], operator_confirmed=False)
    projects.items[0] = replace(projects.items[0], requestor='Changed')
    with pytest.raises(ValueError, match='information changed'):
        service.commit('P1', preview['preview_token'], operator_confirmed=True)
    from backend.domain import LtrRecord, LtrStatus
    ltrs.items.append(LtrRecord(ltr_id='L2', project_id='P2', ltr_number='DL-2026-11-001', status=LtrStatus.REGISTERED))
    with pytest.raises(ValueError, match='another local project'):
        service.preview('P1', values, plan_date=date(2026, 11, 5))
    assert workbook.saves == 0


def test_retired_association_does_not_block_current_owner_rules(tmp_path):
    service, _, _, ltrs, _, _, values = build(tmp_path)
    from backend.domain import LtrRecord, LtrStatus
    ltrs.items.append(LtrRecord(ltr_id='L2', project_id='P2', ltr_number='DL-2026-11-001',
        status=LtrStatus.REGISTERED, is_current_owner=False))
    preview = service.preview('P1', values, plan_date=date(2026, 11, 5))
    assert preview['ltr_number'] == 'DL-2026-11-001'


@pytest.mark.parametrize('status', [ProjectStatus.LTR_REGISTERED, ProjectStatus.FOLDER_CREATED, ProjectStatus.CLOSED, ProjectStatus.CANCELLED])
def test_inconsistent_or_closed_formal_projects_cannot_write_excel(tmp_path, status):
    service, projects, _, _, workbook, _, values = build(tmp_path)
    projects.items[0] = replace(projects.items[0], status=status)
    with pytest.raises(ValueError):
        service.preview('P1', values, plan_date=date(2026, 11, 5))
    assert workbook.saves == 0


def test_confirmed_basic_information_controls_optional_row_facts_without_changing_original_form(tmp_path):
    from backend.application.project_basic_information_service import ProjectBasicInformationRecord
    confirmed = ProjectBasicInformationRecord(record_id='B1', project_id='P1', status='confirmed', version=1,
        values={'product_description': 'Confirmed connector', 'sample_deposition': 'Send Back', 'sub_contract': 'Yes'},
        source_signature='', created_at='', updated_at='')
    service, _, forms, _, workbook, _, values = build(tmp_path, Store(confirmed))
    original = ApplicationForm(form_id='F1', project_id='P1', form_no='REQ', revision='A', requester='Alice',
        post_testing_disposition='Scrap', subcontract='No', subcontract_allowed=False)
    forms.items = [original]
    prepared = service.prepare('P1')['values']
    assert prepared['sample_description'] == 'Confirmed connector'
    preview = service.preview('P1', {**values, 'sample_description': prepared['sample_description']}, plan_date=date(2026, 11, 5))
    assert preview['row'][13:15] == ['Send Back', 'Yes']
    service.commit('P1', preview['preview_token'], operator_confirmed=True)
    assert workbook.saved[0].values[13:15] == ('Send Back', 'Yes')
    assert forms.items[0].post_testing_disposition == 'Scrap'
    assert forms.items[0].subcontract_allowed is False


def test_unknown_requestor_placeholder_is_not_proposed_as_a_real_person(tmp_path):
    service, projects, _, _, _, _, _ = build(tmp_path)
    projects.items[0] = replace(projects.items[0], requestor='Unknown requestor')
    assert service.prepare('P1')['values']['requested_by'] == ''
