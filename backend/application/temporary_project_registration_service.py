"""Register an LTR on an existing project, retaining its entire aggregate."""

from __future__ import annotations

from dataclasses import asdict, replace
from datetime import date
import json
from pathlib import Path
from uuid import uuid4

from backend.application.ltr_service import RegisterLtrCommand
from backend.application.ltr_workbook_write_commit_service import (
    CommitLtrWorkbookWriteCommand, write_previewed_registration_row,
)
from backend.application.ltr_workbook_write_preview_service import (
    LtrWorkbookWritePreviewService, PreviewLtrWorkbookWriteCommand,
)
from backend.application.specified_ltr_workbook_authority_preview_service import (
    SpecifiedLtrWorkbookAuthorityPreviewAck, SpecifiedLtrWorkbookAuthorityPreviewService,
)
from backend.application.new_project_setup_policy import normalize_lab_performing_tests
from backend.application.project_basic_information_source import ProjectBasicInformationSourceAssembler
from backend.domain import ApplicationForm, LtrStatus, ProjectStatus, ProjectLifecycleState
from backend.infrastructure.files.generation_journal import fingerprint, json_value
from backend.infrastructure.office import LtrWorkbookRowData, LtrWorkbookExistingRow
from backend.modules.ltr import next_monthly_dl_number, parse_ltr_number, LtrNumberKind, base_ltr_number


class TemporaryProjectRegistrationError(ValueError):
    """Registration could not safely proceed; the temporary project is retained."""


REQUIRED_FIELDS = {
    'sample_description': 'Sample Description', 'test_item': 'Test Item',
    'requested_by': 'Requested By', 'project_type': 'Project Type',
    'location': 'Mfg. Site', 'test_type_in_sheet': 'Test Type in sheet',
    'project_leader': 'Project Leader', 'lab_performing_tests': 'Lab Performing the Tests',
}


class TemporaryProjectRegistrationService:
    """Preview first; journal external intent before Save; bind locally afterwards."""

    def __init__(self, *, projects, forms, samples, ltrs, basic_information,
                 temporary_context, workbook, journal, ltr_service, commit_local=lambda: None):
        self._projects, self._forms, self._samples, self._ltrs = projects, forms, samples, ltrs
        self._basic, self._temporary = basic_information, temporary_context
        self._workbook, self._journal, self._ltr_service = workbook, journal, ltr_service
        self._commit_local = commit_local

    def prepare(self, project_id: str) -> dict:
        project = self._project(project_id)
        values = self._prefill(project)
        state = self._journal.read(project_id)
        recovery = state is not None and state['status'] in {'writing', 'saving'}
        return {
            'project_id': project_id, 'values': state['effects']['values'] if recovery else values,
            'required_fields': REQUIRED_FIELDS,
            'recovery_preview': self._public_preview(state) if recovery else None,
            'registered_ltr_number': self._registered_number(project_id),
        }

    def preview(self, project_id: str, values: dict[str, str], *, plan_date: date,
                mode: str = 'auto', specified_number: str | None = None) -> dict:
        with self._journal.lock(project_id):
            project = self._eligible_project(project_id)
            pending = self._journal.read(project_id)
            if pending and pending['status'] in {'writing', 'saving'}:
                return self._public_preview(pending)
            values = self._validated_values(values, self._prefill(project))
            effective_project, effective_form = self._effective_sources(project, values)
            with self._workbook.open_read_only_transaction() as context:
                sheets = tuple(str(s) for s in context.session.list_sheets() if str(s).isdigit() and len(str(s)) == 4)
                if mode == 'auto':
                    number = next_monthly_dl_number(year=plan_date.year, month=plan_date.month,
                        existing_numbers=context.session.list_ltr_numbers(sheets))
                    if str(plan_date.year) not in sheets:
                        raise TemporaryProjectRegistrationError(f'Target annual sheet is missing: {plan_date.year}. Check the LTR workbook.')
                elif mode == 'specified':
                    parsed = parse_ltr_number(specified_number or '')
                    if parsed.kind is not LtrNumberKind.STANDARD_DL:
                        raise TemporaryProjectRegistrationError('Enter a full DL number.')
                    number = parsed.normalized
                else:
                    raise TemporaryProjectRegistrationError('Choose automatic or specified numbering.')
                self._unique_workbook_row(context.session, number, sheets)
                if mode == 'specified' and base_ltr_number(number) != number:
                    self._unique_workbook_row(context.session, base_ltr_number(number), sheets)
                workbook_path = str(Path(context.workbook_path).resolve())
            self._reject_other_owner(project_id, number)
            row = LtrWorkbookWritePreviewService.project_row_data(
                effective_project, effective_form, self._samples.list_by_project(project_id),
                PreviewLtrWorkbookWriteCommand(ltr_number=number, plan_date=plan_date,
                    test_item=values['test_item'], sample_description=values['sample_description'],
                    location=values['location'], test_type_in_sheet=values['test_type_in_sheet'],
                    project_leader=values['project_leader']),
            )
            # These two registration facts may have been corrected in Basic
            # Information independently of the original application document.
            row = replace(row, **{target: values[source] or None for source, target in
                (('sample_deposition', 'sample_deposition'), ('sub_contract', 'sub_contract')) if source in values})
            comparison = None
            action = 'append_auto'
            ack = None
            if mode == 'specified':
                compared = SpecifiedLtrWorkbookAuthorityPreviewService(
                    transaction_gateway=self._workbook, intake_confirmation_service=None,
                    row_preview_service=None,
                ).preview_projected_row(row)
                if compared.preview_ack is None or compared.blockers:
                    raise TemporaryProjectRegistrationError(compared.message)
                if str(Path(compared.workbook_path).resolve()) != workbook_path:
                    raise TemporaryProjectRegistrationError('LTR workbook changed during preview. Refresh before applying.')
                action = compared.preview_ack.action
                ack = asdict(compared.preview_ack)
                comparison = json_value(compared)
            state = self._journal.create(project_id, None, 'temporary_project_registration')
            state['status'] = 'preview'
            state['effects'] = {
                'values': values, 'plan_date': plan_date.isoformat(), 'mode': mode,
                'ltr_number': number, 'row': asdict(row), 'action': action,
                'ack': ack, 'comparison': comparison, 'workbook_path': workbook_path,
                'source_signature': self._source_signature(project),
            }
            self._journal.save(state)
            return self._public_preview(state)

    def commit(self, project_id: str, preview_token: str, *, operator_confirmed: bool) -> dict:
        if not operator_confirmed:
            raise TemporaryProjectRegistrationError('Confirm the registration preview before applying.')
        with self._journal.lock(project_id):
            project = self._project(project_id)
            state = self._journal.read(project_id)
            if not state or state['operation_id'] != preview_token:
                raise TemporaryProjectRegistrationError('Registration preview expired. Refresh before applying.')
            intent = state['effects']
            registered = self._registered_number(project_id)
            if registered:
                if registered != intent['ltr_number']:
                    raise TemporaryProjectRegistrationError('This project has a different registered LTR. Refresh the project.')
                return self._result(project_id, registered)
            self._eligible_project(project_id)
            if self._source_signature(project) != intent['source_signature']:
                raise TemporaryProjectRegistrationError('Project information changed after preview. Refresh before applying.')
            self._reject_other_owner(project_id, intent['ltr_number'])
            with self._workbook.open_transaction() as context:
                if str(Path(context.workbook_path).resolve()) != intent['workbook_path']:
                    raise TemporaryProjectRegistrationError('LTR workbook location changed. Restore the original workbook before recovery.')
                self._reject_other_owner(project_id, intent['ltr_number'])
                sheets = tuple(str(s) for s in context.session.list_sheets() if str(s).isdigit() and len(str(s)) == 4)
                existing = self._unique_workbook_row(context.session, intent['ltr_number'], sheets)
                recovered = False
                if state['status'] == 'saving' and existing is not None:
                    saved = intent['saved_row']
                    recovered = self._row_identity(existing) == saved
                if not recovered:
                    if intent['action'] == 'append_associated':
                        self._unique_workbook_row(context.session, base_ltr_number(intent['ltr_number']), sheets)
                    def retain_intent_before_write():
                        state['status'] = 'writing'
                        self._journal.save(state)
                    command = self._write_command(intent)
                    pointer = write_previewed_registration_row(context, LtrWorkbookRowData(**intent['row']),
                        command, expected_action=intent['action'], before_write=retain_intent_before_write)
                    actual = self._unique_workbook_row(context.session, intent['ltr_number'], sheets)
                    if actual is None or actual.sheet_name != pointer.sheet_name or actual.row_number != pointer.row_number:
                        raise TemporaryProjectRegistrationError('Cannot verify the prepared LTR row; workbook was not saved.')
                    # Append adjusts Total and merged Month cells. Record the actual
                    # complete A:Q result before Save, not an approximate projection.
                    intent['saved_row'] = self._row_identity(actual)
                    intent['backup_path'] = str(context.backup_path)
                    state['status'] = 'saving'
                    self._journal.save(state)
                    self._workbook.save_transaction(context)
                else:
                    self._workbook.prune_transaction_backups(context)
                self._bind_local(project, intent)
                # Commit locally before returning success and before releasing the
                # workbook lock, so another project cannot interleave ownership.
                self._commit_local()
            # Retain the journal for response loss/process interruption as well as
            # explicit local commit failure; a later request can check the result.
            return self._result(project_id, intent['ltr_number'])

    def _bind_local(self, project, intent):
        values = intent['values']
        effective_project, effective_form = self._effective_sources(project, values)
        if project.status in {ProjectStatus.DRAFT, ProjectStatus.INTAKE_RECEIVED}:
            effective_project = effective_project.with_status(ProjectStatus.CONFIRMED)
        self._projects.update(effective_project)
        forms = self._forms.list_by_project(project.project_id)
        if forms:
            self._forms.update(effective_form)
        else:
            self._forms.create(effective_form)
        setup = {'source': 'new_project_setup_confirmation', **values}
        notes = json.dumps({'commit_mode': 'external_ltr_workbook', 'action': intent['action'],
            'sheet_name': intent['saved_row']['sheet_name'], 'row_number': intent['saved_row']['row_number'],
            'backup_path': intent.get('backup_path'), 'operator_note': json.dumps(setup, ensure_ascii=True)}, ensure_ascii=True)
        self._ltr_service.register_ltr(project.project_id, RegisterLtrCommand(
            ltr_number=intent['ltr_number'], requested_by=values['requested_by'],
            requested_date=date.fromisoformat(intent['plan_date']), notes=notes,
        ))

    def _project(self, project_id):
        project = self._projects.get(project_id)
        if project is None:
            raise LookupError('Project not found.')
        return project

    def _eligible_project(self, project_id):
        project = self._project(project_id)
        if project.lifecycle_state != ProjectLifecycleState.ACTIVE or project.status in {ProjectStatus.CLOSED, ProjectStatus.CANCELLED}:
            raise TemporaryProjectRegistrationError('Reopen this project before applying an LTR number.')
        if getattr(project, 'registry_state', 'active') != 'active':
            raise TemporaryProjectRegistrationError('Restore this project before applying an LTR number.')
        if project.status not in {ProjectStatus.DRAFT, ProjectStatus.INTAKE_RECEIVED, ProjectStatus.CONFIRMED, ProjectStatus.PRECHECK_PASSED}:
            raise TemporaryProjectRegistrationError('This project requires LTR correction rather than temporary-project registration.')
        if any(r.status is LtrStatus.CANCELLED for r in self._ltrs.list_by_project(project_id)):
            raise TemporaryProjectRegistrationError('A previous LTR was cancelled. Use the LTR correction workflow for this project.')
        if self._registered_number(project_id):
            raise TemporaryProjectRegistrationError('This project already has a registered LTR.')
        return project

    def _registered_number(self, project_id):
        records = [r for r in self._ltrs.list_by_project(project_id) if r.status is LtrStatus.REGISTERED]
        if len(records) > 1:
            raise TemporaryProjectRegistrationError('Multiple registered LTR records require manual review.')
        return records[0].ltr_number if records else None

    def _reject_other_owner(self, project_id, number):
        if any(r.project_id != project_id and r.ltr_number == number and r.status is LtrStatus.REGISTERED and r.is_current_owner
               for r in self._ltrs.search(number)):
            raise TemporaryProjectRegistrationError('This LTR number is already assigned to another local project. Open that project or choose another number.')

    @staticmethod
    def _unique_workbook_row(session, number, sheets):
        # list_ltr_numbers intentionally de-duplicates values for auto numbering;
        # recovery must inspect physical rows so a duplicate cannot masquerade as
        # the original saved registration.
        matches = [LtrWorkbookExistingRow(sheet, index, number, tuple(row))
            for sheet in sheets for index, row in enumerate(session.read_annual_sheet(sheet), start=2)
            if len(row) >= 4 and str(row[3] or '').strip().upper() == number]
        if len(matches) > 1:
            raise TemporaryProjectRegistrationError('Duplicate LTR rows require manual review before registration.')
        return matches[0] if matches else None

    def _prefill(self, project):
        suggestions = ProjectBasicInformationSourceAssembler(ltr_store=self._ltrs,
            application_form_store=self._forms, sample_store=self._samples).assemble(project)
        values = {key: item.source_value for key, item in suggestions.items()}
        forms = self._forms.list_by_project(project.project_id)
        if forms and forms[-1].subcontract_allowed is not None:
            values['sub_contract'] = 'Yes' if forms[-1].subcontract_allowed else 'No'
        temporary = self._temporary.get_by_project(project.project_id)
        if temporary:
            for key in ('sample_description', 'test_item'):
                values[key] = getattr(temporary, key, None) or values.get(key, '')
        draft = self._basic.get_latest_draft(project.project_id)
        confirmed = self._basic.get_latest_confirmed(project.project_id)
        for record in (draft, confirmed):
            if record:
                values.update(record.values)
        descriptions = [record.values.get('description_pn') or record.values.get('product_description')
            for record in (confirmed, draft) if record]
        values['sample_description'] = next((value for value in descriptions if value and value.strip()), None) or values.get('sample_description') or values.get('description_pn') or project.product_name or ''
        if str(values.get('requested_by', '')).strip().casefold() in {'unknown requestor', 'unknown requester'}:
            values['requested_by'] = ''
        result = {key: str(values.get(key, '') or '') for key in REQUIRED_FIELDS}
        if 'sub_contract' in values:
            result['sub_contract'] = str(values['sub_contract'] or '')
        if 'sample_deposition' in values or 'post_testing_disposition' in values:
            disposition = str(values.get('sample_deposition', values.get('post_testing_disposition', '')) or '')
            result['sample_deposition'] = 'Send Back' if disposition == 'Send Back to Requestor' else disposition
        return result

    @staticmethod
    def _validated_values(values, defaults):
        cleaned = {key: str(values.get(key, '')).strip() for key in REQUIRED_FIELDS}
        missing = [label for key, label in REQUIRED_FIELDS.items() if not cleaned[key]]
        if missing:
            raise TemporaryProjectRegistrationError('Complete registration information: ' + ', '.join(missing))
        normalize_lab_performing_tests(cleaned['lab_performing_tests'], required=True)
        for key in ('sample_deposition', 'sub_contract'):
            if key in values or key in defaults:
                cleaned[key] = str(values.get(key, defaults.get(key)) or '').strip()
        if cleaned.get('sub_contract') not in {None, '', 'Yes', 'No'}:
            raise TemporaryProjectRegistrationError('Sub-contract must be Yes or No.')
        return cleaned

    def _effective_sources(self, project, values):
        forms = self._forms.list_by_project(project.project_id)
        form = forms[-1] if forms else ApplicationForm(form_id=uuid4().hex, project_id=project.project_id,
            form_no='', revision='', requester=values['requested_by'])
        return (replace(project, requestor=values['requested_by'], product_name=values['sample_description']),
            replace(form, requester=values['requested_by'], project_type=values['project_type'],
                manufacturing_site=values['location'], assigned_personnel=values['project_leader'],
                lab=values['lab_performing_tests']))

    def _source_signature(self, project):
        return fingerprint({'project': project, 'forms': self._forms.list_by_project(project.project_id),
            'samples': self._samples.list_by_project(project.project_id),
            'basic_draft': self._basic.get_latest_draft(project.project_id),
            'basic_confirmed': self._basic.get_latest_confirmed(project.project_id)})

    @staticmethod
    def _write_command(intent):
        values = intent['values']
        return CommitLtrWorkbookWriteCommand(plan_date=date.fromisoformat(intent['plan_date']),
            operator_confirmed=True, preview_acknowledged=True,
            number_input=intent['ltr_number'] if intent['mode'] == 'specified' else None,
            specified_ltr_workbook_preview_ack=SpecifiedLtrWorkbookAuthorityPreviewAck(**intent['ack']) if intent['ack'] else None,
            test_item=values['test_item'], sample_description=values['sample_description'],
            test_type_in_sheet=values['test_type_in_sheet'], project_leader=values['project_leader'])

    @staticmethod
    def _row_identity(row):
        return json_value({'sheet_name': row.sheet_name, 'row_number': row.row_number, 'values': list(row.values)})

    @staticmethod
    def _public_preview(state):
        intent = state['effects']
        return {'project_id': state['project_id'], 'preview_token': state['operation_id'],
            'ltr_number': intent['ltr_number'], 'action': intent['action'],
            'workbook_path': intent['workbook_path'], 'values': intent['values'],
            'comparison': intent['comparison'], 'row': list(LtrWorkbookRowData(**intent['row']).as_excel_row()),
            'recovery_required': state['status'] in {'writing', 'saving'}}

    @staticmethod
    def _result(project_id, number):
        return {'project_id': project_id, 'ltr_number': number}
