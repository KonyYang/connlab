import json
from dataclasses import replace
from types import SimpleNamespace

import pytest

from backend.application.temporary_project_intake_source import (
    TemporaryProjectIntakeSource, normalize_intake_snapshot, project_snapshot_records,
)


def snapshot(**field_overrides):
    return {'version': 1, 'fields': {'requester': 'Alice', 'phone': '123', 'email': 'alice@example.com',
        'project_type': 'New Product Development', 'manufacturing_site': 'Nantong',
        'requested_testing': 'Durability', 'request_date': '2026/11/05', **field_overrides},
        'samples': [{'product_name': 'Connector', 'part_number': 'PN-1', 'quantity': '5', 'material': 'Copper'}],
        'requested_testing_rows': [{'test_to_be_performed': 'Durability', 'applicable_specification': 'EIA-364'}],
        'project_setup': {'test_item': 'Qualification', 'sample_description': 'Connector',
            'project_leader': 'Even Yang', 'lab_performing_tests': 'Dongguan', 'test_type_in_sheet': 'Partial Qualification'},
        'source_case_id': 'C1', 'selected_form_asset_id': 'A1'}


def test_snapshot_projection_retains_complete_form_and_samples_without_completing_intake():
    frozen = normalize_intake_snapshot(snapshot())
    form, samples = project_snapshot_records('P1', frozen)
    assert form.phone == '123' and form.email == 'alice@example.com'
    assert form.manufacturing_site == 'Nantong' and form.project_type == 'New Product Development'
    assert form.lab == 'Dongguan' and form.assigned_personnel == 'Even Yang'
    assert samples[0].part_number == 'PN-1' and samples[0].quantity == 5
    assert frozen['requested_testing_rows'][0]['applicable_specification'] == 'EIA-364'


def test_partial_planning_quantity_is_retained_without_requiring_formal_confirmation():
    partial = snapshot()
    partial['fields']['requester'] = ''
    partial['samples'][0]['quantity'] = 'TBD'
    frozen = normalize_intake_snapshot(partial)
    form, samples = project_snapshot_records('P1', frozen)
    assert frozen['samples'][0]['quantity'] == 'TBD'
    assert samples[0].quantity is None
    assert form.requester == 'Unknown requestor'


class Sources:
    def __init__(self, candidates): self.candidates = candidates
    def eligible_snapshots(self, project_id, asset_ids): return self.candidates


def test_frozen_snapshot_is_self_contained_and_legacy_different_candidates_require_selection():
    frozen = normalize_intake_snapshot(snapshot())
    context = SimpleNamespace(intake_snapshot_json=json.dumps(frozen), source_asset_ids=('missing',))
    resolver = TemporaryProjectIntakeSource(Sources([]))
    result = resolver.resolve('P1', context)
    assert result['snapshot']['fields']['phone'] == '123'
    assert result['candidates'] == []
    legacy = SimpleNamespace(intake_snapshot_json=None, source_asset_ids=('A1',))
    candidates = [normalize_intake_snapshot(snapshot()), normalize_intake_snapshot(snapshot(phone='999'))]
    resolver = TemporaryProjectIntakeSource(Sources(candidates))
    ambiguous = resolver.resolve('P1', legacy)
    assert ambiguous['snapshot'] is None and len(ambiguous['candidates']) == 2
    chosen = resolver.resolve('P1', legacy, source_id=ambiguous['candidates'][1]['source_id'])
    assert chosen['snapshot']['fields']['phone'] == '999'
    stale = ambiguous['candidates'][1]['source_id']
    resolver = TemporaryProjectIntakeSource(Sources(candidates[:1]))
    with pytest.raises(ValueError, match='source changed'):
        resolver.resolve('P1', legacy, source_id=stale)
    manual = resolver.resolve('P1', legacy, source_id='manual')
    assert manual['snapshot'] is None and manual['source_id'] == 'manual'


def test_identical_legacy_facts_are_deduplicated_with_both_provenances():
    first, second = snapshot(), snapshot()
    second['source_case_id'] = 'C2'
    resolver = TemporaryProjectIntakeSource(Sources([first, second]))
    resolved = resolver.resolve('P1', SimpleNamespace(intake_snapshot_json=None, source_asset_ids=('A1',)))
    assert resolved['snapshot']['fields']['phone'] == '123'
    assert resolved['candidates'] == []


def test_additive_snapshot_migration_preserves_old_rows_and_is_idempotent(tmp_path):
    from backend.infrastructure.storage.database import create_database_engine, create_session_factory, init_db
    from backend.infrastructure.storage.repositories import ProjectRepository, ProjectTemporaryContextRepository
    from backend.domain import Project, ProjectTemporaryContext
    from backend.shared.config import Settings
    settings = Settings(data_dir=tmp_path/'data', projects_dir=tmp_path/'projects', templates_dir=tmp_path/'templates', database_path=tmp_path/'old.sqlite3')
    engine = create_database_engine(settings)
    init_db(engine)
    factory = create_session_factory(engine)
    with factory() as session:
        ProjectRepository(session).create(Project(project_id='P1', project_no=None, product_name='Retained', requestor='Alice'))
        ProjectTemporaryContextRepository(session).create(ProjectTemporaryContext(context_id='CTX', project_id='P1', notes='Human note', source_asset_ids=('A1',)))
        session.commit()
    with engine.begin() as connection:
        connection.exec_driver_sql('ALTER TABLE project_temporary_contexts DROP COLUMN intake_snapshot_json')
    init_db(engine)
    init_db(engine)
    with factory() as session:
        context = ProjectTemporaryContextRepository(session).get_by_project('P1')
        assert context.notes == 'Human note' and context.source_asset_ids == ('A1',)
        assert context.intake_snapshot_json is None
    engine.dispose()
