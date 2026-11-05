from contextlib import contextmanager
from copy import deepcopy
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from fastapi import Depends
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import event

from backend.api.dependencies import get_session, get_settings, get_temporary_project_registration_service
from backend.api.main import app
from backend.application.temporary_project_registration_service import TemporaryProjectRegistrationService
from backend.application.ltr_service import LtrService
from backend.application.project_lifecycle_service import ProjectLifecycleService
from backend.domain import Project, ProjectStatus, ApplicationForm, ProjectTestPlanDraft, ProjectTestPlanDraftStatus, ProjectTemporaryContext, IntakePackage, IntakePackageSourceType, IntakePackageStatus, IntakeAsset, IntakeAssetRole, IntakeCase, IntakeCaseStatus, IntakeDraft
from backend.application.temporary_project_intake_source import TemporaryProjectIntakeSource, LinkedIntakeCandidateSource
from backend.infrastructure.storage.repositories.intake_package import IntakePackageRepository, IntakeAssetRepository, IntakeCaseRepository, IntakeDraftRepository
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.office import LtrWorkbookExistingRow, LtrWorkbookRowPointer
from backend.infrastructure.storage.database import create_database_engine, create_session_factory, init_db
from backend.infrastructure.storage.repositories import ProjectRepository, ApplicationFormRepository, LtrRecordRepository, SampleInfoRepository, ProjectTemporaryContextRepository, ProjectTestPlanDraftRepository
from backend.infrastructure.storage.repositories.project_basic_information import ProjectBasicInformationRepository
from backend.shared.config import Settings


class IsolatedWorkbook:
    """Only the Office boundary is replaced; database and API lifecycle are real."""
    def __init__(self, root):
        self.path = root / 'isolated-LTR.xlsx'
        self.rows, self.saved, self.saves = [], [], 0

    @contextmanager
    def open_read_only_transaction(self):
        self.rows = deepcopy(self.saved)
        yield SimpleNamespace(session=self, workbook_path=self.path)

    @contextmanager
    def open_transaction(self):
        self.rows = deepcopy(self.saved)
        try:
            yield SimpleNamespace(session=self, workbook_path=self.path, backup_path=self.path.with_suffix('.bak'))
        finally:
            self.rows = deepcopy(self.saved)

    def list_sheets(self): return ['2026']
    def list_ltr_numbers(self, sheets): return [row.dl_number for row in self.rows]
    def read_annual_sheet(self, sheet): return tuple(row.values for row in self.rows)
    def find_ltr_number(self, number, sheets): return next((row for row in self.rows if row.dl_number == number), None)
    def prepare_sheet_for_operation(self, *args, **kwargs): pass
    def prune_transaction_backups(self, context): pass

    def append_registration_row(self, sheet, row):
        found = LtrWorkbookExistingRow(sheet, len(self.rows) + 2, row.dl_number, tuple(row.as_excel_row()))
        self.rows.append(found)
        return LtrWorkbookRowPointer(sheet, found.row_number, row.dl_number)

    def save_transaction(self, context):
        self.saved = deepcopy(self.rows)
        self.saves += 1


@pytest.fixture
def registration_api(tmp_path):
    settings = Settings(data_dir=tmp_path / 'data', projects_dir=tmp_path / 'projects',
        templates_dir=tmp_path / 'templates', database_path=tmp_path / 'isolated.sqlite3')
    settings.ensure_directories()
    engine = create_database_engine(settings)
    init_db(engine)
    factory = create_session_factory(engine)
    workbook = IsolatedWorkbook(tmp_path)
    failure = {'commit': False}

    def override_session():
        with factory() as session:
            def before_commit(_):
                if failure['commit']:
                    failure['commit'] = False
                    raise RuntimeError('Injected request database commit failure')
            event.listen(session, 'before_commit', before_commit)
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    def service(session=Depends(get_session)):
        projects, ltrs = ProjectRepository(session), LtrRecordRepository(session)
        return TemporaryProjectRegistrationService(projects=projects, forms=ApplicationFormRepository(session),
            samples=SampleInfoRepository(session), ltrs=ltrs, basic_information=ProjectBasicInformationRepository(session),
            temporary_context=ProjectTemporaryContextRepository(session), workbook=workbook,
            journal=GenerationJournal(settings.data_dir / 'ltr_registration'),
            ltr_service=LtrService(projects, ltrs, ProjectLifecycleService(projects)), commit_local=session.commit,
            intake_source=TemporaryProjectIntakeSource(LinkedIntakeCandidateSource(assets=IntakeAssetRepository(session), cases=IntakeCaseRepository(session), drafts=IntakeDraftRepository(session))))

    with factory() as session:
        ProjectRepository(session).create(Project(project_id='P1', project_no=None, product_name='Connector',
            requestor='Alice', status=ProjectStatus.DRAFT))
        ApplicationFormRepository(session).create(ApplicationForm(form_id='F1', project_id='P1',
            form_no='Request', revision='A', requester='Alice', phone='123', project_type='New Product Development',
            manufacturing_site='Nantong', lab='Dongguan', assigned_personnel='White'))
        ProjectTestPlanDraftRepository(session).create(ProjectTestPlanDraft(draft_id='M1', project_id='P1',
            source_document_path='retained.docx', source_document_name='retained.docx', source_format='docx',
            status=ProjectTestPlanDraftStatus.DRAFT, version=1, payload_json='{"retained_manual_edit":"Do not replace"}',
            created_at='2026-11-05T00:00:00Z', updated_at='2026-11-05T00:00:00Z'))
        session.commit()
    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_temporary_project_registration_service] = service
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, workbook, failure, factory
    app.dependency_overrides.clear()
    engine.dispose()


def values():
    return dict(sample_description='Connector', test_item='Qualification', requested_by='Alice',
        project_type='New Product Development', location='Nantong', test_type_in_sheet='Partial Qualification',
        project_leader='White', lab_performing_tests='Dongguan')


def test_api_registers_current_project_and_keeps_matrix_form_and_route(registration_api):
    client, workbook, _, _ = registration_api
    before = client.get('/api/projects/P1/test-plan/drafts').json()
    assert before[0]['payload']['retained_manual_edit'] == 'Do not replace'
    prepared = client.get('/api/projects/P1/ltr-registration')
    assert prepared.status_code == 200
    assert prepared.json()['values']['project_leader'] == 'White'
    preview = client.post('/api/projects/P1/ltr-registration/preview', json={'values': values(), 'plan_date': '2026-11-05'})
    assert preview.status_code == 200, preview.text
    assert not workbook.saved
    token = preview.json()['preview_token']
    result = client.post('/api/projects/P1/ltr-registration/commit', json={'preview_token': token, 'operator_confirmed': True})
    assert result.status_code == 200, result.text
    assert result.json() == {'project_id': 'P1', 'ltr_number': 'DL-2026-11-001'}
    assert client.get('/api/projects/P1').json()['project_id'] == 'P1'
    assert client.get('/api/projects/P1/test-plan/drafts').json() == before
    assert len(client.get('/api/projects').json()) == 1
    assert len(client.get('/api/projects/P1/ltr').json()) == 1
    assert workbook.saves == 1


def test_api_recovers_after_request_commit_fails_without_reallocating_number(registration_api):
    client, workbook, failure, factory = registration_api
    preview = client.post('/api/projects/P1/ltr-registration/preview', json={'values': values(), 'plan_date': '2026-11-05'}).json()
    command = {'preview_token': preview['preview_token'], 'operator_confirmed': True}
    failure['commit'] = True
    failed = client.post('/api/projects/P1/ltr-registration/commit', json=command)
    assert failed.status_code == 500
    assert workbook.saves == 1 and len(workbook.saved) == 1
    assert client.get('/api/projects/P1/ltr').json() == []
    assert client.get('/api/projects/P1').json()['status'] == 'draft'
    pending = client.get('/api/projects/P1/ltr-registration').json()['recovery_preview']
    assert pending['ltr_number'] == 'DL-2026-11-001' and pending['recovery_required'] is True
    recovered = client.post('/api/projects/P1/ltr-registration/commit', json=command)
    assert recovered.status_code == 200, recovered.text
    assert recovered.json()['ltr_number'] == 'DL-2026-11-001'
    assert workbook.saves == 1 and len(client.get('/api/projects/P1/ltr').json()) == 1


def test_api_missing_fields_and_recycled_project_are_blocked_without_excel_write(registration_api):
    client, workbook, _, factory = registration_api
    invalid = client.post('/api/projects/P1/ltr-registration/preview', json={'values': {}})
    assert invalid.status_code == 409 and 'Complete registration' in invalid.json()['detail']
    from backend.infrastructure.storage.models import ProjectModel
    with factory() as session:
        session.get(ProjectModel, 'P1').registry_state = 'trash'
        session.commit()
    blocked = client.post('/api/projects/P1/ltr-registration/preview', json={'values': values()})
    assert blocked.status_code == 409
    assert blocked.json()['detail']['code'] == 'project_registry_read_only'
    assert workbook.saves == 0


def captured_snapshot():
    return {'version': 1, 'fields': {'requester': 'Alice', 'phone': 'immediate phone edit',
        'email': 'current@example.test', 'request_date': '2026-11-05', 'project_type': 'New Product Development',
        'manufacturing_site': 'Nantong', 'business_unit': 'Power Solutions', 'post_testing_disposition': 'Send Back to Requestor'},
        'samples': [{'product_name': 'Connector', 'part_number': 'PN-CURRENT', 'quantity': '7', 'material': 'Copper'}],
        'requested_testing_rows': [{'test_to_be_performed': 'Current test', 'applicable_specification': 'GS-current'}],
        'project_setup': {'test_item': 'Qualification', 'sample_description': 'Current connector', 'project_leader': 'Even Yang',
            'lab_performing_tests': 'Dongguan', 'test_type_in_sheet': 'Partial Qualification'},
        'source_case_id': 'CASE1', 'selected_form_asset_id': 'ASSET1'}


def seed_intake(factory):
    import json
    with factory() as session:
        IntakePackageRepository(session).create(IntakePackage(package_id='PKG1', source_type=IntakePackageSourceType.OUTLOOK_MSG,
            status=IntakePackageStatus.READY_FOR_REVIEW, source_original_name='request.msg', source_stored_path=Path('isolated-request.msg')))
        IntakeAssetRepository(session).create(IntakeAsset(asset_id='ASSET1', package_id='PKG1', original_name='request.docx',
            stored_path=Path('isolated-request.docx'), extension='.docx', mime_type=None, size_bytes=10, sha256='hash',
            asset_role=IntakeAssetRole.SELECTED_APPLICATION_FORM))
        IntakeCaseRepository(session).create(IntakeCase(case_id='CASE1', package_id='PKG1', selected_form_asset_id='ASSET1', status=IntakeCaseStatus.NEEDS_REVIEW))
        IntakeDraftRepository(session).create(IntakeDraft(draft_id='DRAFT1', case_id='CASE1', parsed_fields_json=json.dumps({
            'requester': 'Old Alice', 'phone': 'old phone', 'project_type': 'Operational Support', 'manufacturing_site': 'Old site',
            'samples': [{'product_name': 'Old connector', 'part_number': 'OLD', 'quantity': '3'}],
            'project_setup': {'project_leader': 'Old leader', 'lab_performing_tests': 'Valley Green', 'test_type_in_sheet': 'Electrical'}})))
        session.commit()


def test_create_from_current_intake_preserves_full_snapshot_and_registration_fields(registration_api):
    import json
    from dataclasses import replace
    client, workbook, _, factory = registration_api
    seed_intake(factory)
    current = captured_snapshot()
    created = client.post('/api/projects/temporary', json={'sample_description': 'Current connector', 'test_item': 'Qualification',
        'requestor': 'Alice', 'source_asset_ids': ['ASSET1'], 'notes': 'Human notes stay unchanged', 'intake_snapshot': current})
    assert created.status_code == 201, created.text
    identity = created.json()['project_id']
    assert client.get(f'/api/projects/{identity}').json()['status'] == 'draft'
    prepared = client.get(f'/api/projects/{identity}/ltr-registration').json()
    assert {key: prepared['values'][key] for key in ('project_type', 'location', 'project_leader', 'lab_performing_tests', 'test_type_in_sheet')} == {
        'project_type': 'New Product Development', 'location': 'Nantong', 'project_leader': 'Even Yang',
        'lab_performing_tests': 'Dongguan', 'test_type_in_sheet': 'Partial Qualification'}
    with factory() as session:
        form = ApplicationFormRepository(session).list_by_project(identity)[0]
        samples = SampleInfoRepository(session).list_by_project(identity)
        context = ProjectTemporaryContextRepository(session).get_by_project(identity)
        assert form.phone == 'immediate phone edit' and form.email == 'current@example.test'
        assert samples[0].part_number == 'PN-CURRENT' and samples[0].quantity == 7
        assert json.loads(context.intake_snapshot_json)['requested_testing_rows'] == current['requested_testing_rows']
        assert context.notes == 'Human notes stay unchanged'
        draft_store = IntakeDraftRepository(session)
        original = draft_store.get_by_case('CASE1')
        assert json.loads(original.parsed_fields_json)['phone'] == 'old phone'
        draft_store.update(replace(original, parsed_fields_json=json.dumps({'phone': 'later unrelated source edit'})))
        assert IntakeCaseRepository(session).get('CASE1').confirmed_project_id is None
        session.commit()
    # New request/session reads only the frozen Project data, not the edited case.
    assert client.get(f'/api/projects/{identity}/ltr-registration').json()['values'] == prepared['values']
    preview = client.post(f'/api/projects/{identity}/ltr-registration/preview', json={'values': prepared['values'], 'plan_date': '2026-11-05'})
    assert preview.status_code == 200, preview.text
    assert workbook.saves == 0


def test_legacy_unique_unbound_case_is_recovered_readonly_and_other_project_case_is_excluded(registration_api):
    import json
    from dataclasses import replace
    client, workbook, _, factory = registration_api
    seed_intake(factory)
    with factory() as session:
        # Model the real old shape: same package/form, one case already belongs elsewhere.
        ProjectRepository(session).create(Project(project_id='LEGACY', project_no=None, product_name='Old title', requestor='Alice'))
        ProjectTemporaryContextRepository(session).create(ProjectTemporaryContext(context_id='CTX', project_id='LEGACY', source_asset_ids=('ASSET1',), notes='untouched'))
        drafts = IntakeDraftRepository(session)
        original = drafts.get_by_case('CASE1')
        data = captured_snapshot()
        drafts.update(replace(original, parsed_fields_json=json.dumps({**data['fields'], 'samples': data['samples'], 'project_setup': data['project_setup'], 'requested_testing_rows': data['requested_testing_rows']})))
        IntakeCaseRepository(session).create(IntakeCase(case_id='OTHERCASE', package_id='PKG1', selected_form_asset_id='ASSET1',
            status=IntakeCaseStatus.CONFIRMED, confirmed_project_id='P1'))
        IntakeDraftRepository(session).create(IntakeDraft(draft_id='OTHERDRAFT', case_id='OTHERCASE', parsed_fields_json=json.dumps({**data['fields'], 'project_type': 'Innovation'})))
        session.commit()
    prepared = client.get('/api/projects/LEGACY/ltr-registration')
    assert prepared.status_code == 200, prepared.text
    payload = prepared.json()
    assert payload['values']['project_type'] == 'New Product Development'
    assert payload['values']['location'] == 'Nantong' and payload['values']['project_leader'] == 'Even Yang'
    assert payload['intake_candidates'] == []
    with factory() as session:
        assert ApplicationFormRepository(session).list_by_project('LEGACY') == []
        assert SampleInfoRepository(session).list_by_project('LEGACY') == []
        assert IntakeCaseRepository(session).get('CASE1').confirmed_project_id is None
    preview = client.post('/api/projects/LEGACY/ltr-registration/preview', json={'values': payload['values'], 'plan_date': '2026-11-05', 'intake_source_id': payload['intake_source_id']}).json()
    result = client.post('/api/projects/LEGACY/ltr-registration/commit', json={'preview_token': preview['preview_token'], 'operator_confirmed': True})
    assert result.status_code == 200, result.text
    with factory() as session:
        form = ApplicationFormRepository(session).list_by_project('LEGACY')[0]
        assert form.email == 'current@example.test'
        assert SampleInfoRepository(session).list_by_project('LEGACY')[0].part_number == 'PN-CURRENT'
        assert ProjectTemporaryContextRepository(session).get_by_project('LEGACY').intake_snapshot_json is not None
        assert IntakeCaseRepository(session).get('CASE1').confirmed_project_id is None
