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
from backend.domain import Project, ProjectStatus, ApplicationForm, ProjectTestPlanDraft, ProjectTestPlanDraftStatus
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
            ltr_service=LtrService(projects, ltrs, ProjectLifecycleService(projects)), commit_local=session.commit)

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
