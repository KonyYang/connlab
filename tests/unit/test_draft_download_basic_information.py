from types import SimpleNamespace

from backend.application.project_basic_information_output import ProjectBasicInformationSnapshotReader


class Repository:
    def __init__(self, *, draft=None, confirmed=None, project_id='P1'):
        self.draft, self.confirmed = draft, confirmed
        self.project_id = project_id

    def get_latest_draft(self, project_id):
        assert project_id == self.project_id
        return self.draft

    def get_latest_confirmed(self, project_id):
        assert project_id == self.project_id
        return self.confirmed


def record(values, *, status='draft', project_id='P1'):
    return SimpleNamespace(project_id=project_id, values=values, version=4, source_signature='{}',
                           confirmed_at=None, confirmed_by=None, sample_rows=(), status=status)


def test_download_uses_draft_values_without_claiming_confirmed_authority():
    repository = Repository(draft=record({'product_description': 'Draft connector', 'project_leader': 'Min'}))
    snapshot = ProjectBasicInformationSnapshotReader(repository).get_download_snapshot('P1')
    assert snapshot.values == {'product_description': 'Draft connector', 'project_leader': 'Min'}
    assert snapshot.version is None
    assert snapshot.source_signature_hash is None
    assert repository.get_latest_confirmed('P1') is None


def test_download_overlays_present_draft_fields_and_preserves_deliberate_blank():
    repository = Repository(
        draft=record({'product_description': 'New connector', 'requested_by': ''}),
        confirmed=record({'dl_number': 'DL-2026-09-002A', 'product_description': 'Old connector',
                          'requested_by': 'Old requester'}, status='confirmed'),
    )
    reader = ProjectBasicInformationSnapshotReader(repository)
    snapshot = reader.get_download_snapshot('P1')
    assert snapshot.values == {'dl_number': 'DL-2026-09-002A', 'product_description': 'New connector',
                               'requested_by': ''}
    assert snapshot.version is None
    assert reader.get_latest_confirmed('P1').values['product_description'] == 'Old connector'
    assert reader.get_preview_snapshot('P1').version == 4


def test_download_falls_back_to_confirmed_and_missing_information_stays_unavailable():
    repository = Repository(confirmed=record({'dl_number': 'DL-2026-09-002A'}, status='confirmed'))
    reader = ProjectBasicInformationSnapshotReader(repository)
    assert reader.get_download_snapshot('P1').values['dl_number'] == 'DL-2026-09-002A'
    assert reader.get_download_snapshot('P1').version == 4
    assert ProjectBasicInformationSnapshotReader(Repository()).get_download_snapshot('P1') is None


def test_download_uses_available_project_sources_without_initializing_or_saving_a_draft():
    reader = ProjectBasicInformationSnapshotReader(
        Repository(), download_sources=lambda project_id: {'dl_number': 'DL-2026-09-002A',
                                                          'requested_by': 'Customer'},
    )
    snapshot = reader.get_download_snapshot('P1')
    assert snapshot.values == {'dl_number': 'DL-2026-09-002A', 'requested_by': 'Customer'}
    assert snapshot.version is None
    assert reader.get_latest_confirmed('P1') is None


def test_source_augmented_download_does_not_claim_a_confirmed_snapshot():
    reader = ProjectBasicInformationSnapshotReader(
        Repository(confirmed=record({'dl_number': 'DL-2026-09-002A'}, status='confirmed')),
        download_sources=lambda project_id: {'requested_by': 'Available requester'},
    )
    snapshot = reader.get_download_snapshot('P1')
    assert snapshot.values['requested_by'] == 'Available requester'
    assert snapshot.version is None
    assert snapshot.source_signature_hash is None
