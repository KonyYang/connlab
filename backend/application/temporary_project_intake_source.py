"""Frozen temporary-project intake facts and conservative legacy source recovery."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
import hashlib
import json
import re
from typing import Protocol

from backend.application.intake_data_projection import IntakeDataProjector
from backend.domain import IntakeCaseStatus, IntakeAssetRole


class TemporaryIntakeCandidateStore(Protocol):
    def eligible_snapshots(self, project_id: str, asset_ids: tuple[str, ...]) -> list[dict]: ...


class LinkedIntakeCandidateSource:
    """Read only cases selected from explicitly retained project asset IDs."""

    def __init__(self, *, assets, cases, drafts):
        self._assets, self._cases, self._drafts = assets, cases, drafts

    def validate_provenance(self, snapshot, asset_ids):
        case_id, asset_id = snapshot['source_case_id'], snapshot['selected_form_asset_id']
        if not case_id and not asset_id:
            return
        case = self._cases.get(case_id) if case_id else None
        asset = self._assets.get(asset_id) if asset_id else None
        if (case is None or asset is None or case.selected_form_asset_id != asset.asset_id
                or case.package_id != asset.package_id or asset.asset_id not in asset_ids):
            raise ValueError('The captured intake source does not match the selected application form. Refresh the intake page.')

    def eligible_snapshots(self, project_id, asset_ids):
        assets = [asset for identity in asset_ids if (asset := self._assets.get(identity)) is not None]
        selected_ids = {asset.asset_id for asset in assets if asset.asset_role is not IntakeAssetRole.IGNORED}
        result = []
        for package_id in sorted({asset.package_id for asset in assets}):
            for case in self._cases.list_by_package(package_id):
                if case.selected_form_asset_id not in selected_ids:
                    continue
                if case.confirmed_project_id not in {None, project_id}:
                    continue
                if case.status not in {IntakeCaseStatus.DRAFT_CREATED, IntakeCaseStatus.NEEDS_REVIEW, IntakeCaseStatus.CONFIRMED}:
                    continue
                draft = self._drafts.get_by_case(case.case_id)
                if draft is None:
                    continue
                parsed = json.loads(draft.parsed_fields_json)
                overrides = json.loads(draft.manual_overrides_json or '{}')
                if not isinstance(parsed, dict) or not isinstance(overrides, dict):
                    raise ValueError('Linked intake data is unreadable. Review the original request before registration.')
                data = {**parsed, **{key: value for key, value in overrides.items() if value not in (None, '')}}
                setup = data.pop('project_setup', {})
                samples = data.pop('samples', None)
                if samples is None:
                    samples = json.loads(draft.sample_rows_json or '[]')
                testing = data.pop('requested_testing_rows', None)
                if testing is None:
                    testing = json.loads(draft.requested_testing_json or '[]')
                # Parsed models may contain nested diagnostic fields; only form
                # scalar fields belong to this reviewed source snapshot.
                fields = {key: value for key, value in data.items() if not isinstance(value, (dict, list))}
                result.append(normalize_intake_snapshot({'version': 1, 'fields': fields, 'samples': samples,
                    'requested_testing_rows': testing, 'project_setup': setup,
                    'source_case_id': case.case_id, 'selected_form_asset_id': case.selected_form_asset_id}))
        return result


def normalize_intake_snapshot(value: dict) -> dict:
    """Retain the complete current editor payload, including explicit blanks."""
    allowed = {'version', 'fields', 'samples', 'requested_testing_rows', 'project_setup',
        'source_case_id', 'selected_form_asset_id'}
    if not isinstance(value, dict) or value.get('version') != 1 or set(value) - allowed:
        raise ValueError('Unsupported temporary intake snapshot.')

    def strings(mapping):
        if not isinstance(mapping, dict) or any(not isinstance(k, str) for k in mapping):
            raise ValueError('Intake fields must be an object of scalar values.')
        if any(isinstance(v, (dict, list)) for v in mapping.values()):
            raise ValueError('Intake field values must be scalar values.')
        return {key: '' if item is None else str(item).strip() for key, item in mapping.items()}

    def rows(key):
        entries = value.get(key, [])
        if not isinstance(entries, list):
            raise ValueError(f'{key} must be a list.')
        return [strings(row) for row in entries]

    return {'version': 1, 'fields': strings(value.get('fields', {})), 'samples': rows('samples'),
        'requested_testing_rows': rows('requested_testing_rows'), 'project_setup': strings(value.get('project_setup', {})),
        'source_case_id': value.get('source_case_id') or None,
        'selected_form_asset_id': value.get('selected_form_asset_id') or None}


def snapshot_fingerprint(snapshot: dict, *, facts_only=False) -> str:
    facts = {key: value for key, value in snapshot.items()
        if not facts_only or key not in {'source_case_id', 'selected_form_asset_id'}}
    return hashlib.sha256(json.dumps(facts, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()


def project_snapshot_records(project_id: str, snapshot: dict):
    """Reuse the actual Intake projection without creating/confirming its case."""
    data = dict(snapshot['fields'])
    setup = snapshot['project_setup']
    for source, target in (('lab_performing_tests', 'lab'), ('project_leader', 'assigned_personnel')):
        if source in setup:
            data[target] = setup[source]
    data['requester'] = data.get('requester') or 'Unknown requestor'
    data['product_name'] = data.get('product_name') or setup.get('sample_description') or 'Temporary planning project'
    testing = snapshot['requested_testing_rows']
    if testing:
        data['requested_testing'] = '\n'.join(row.get('test_to_be_performed', '') for row in testing if row.get('test_to_be_performed'))
        data.setdefault('reference_doc', '\n'.join(row.get('applicable_specification', '') for row in testing if row.get('applicable_specification')))
    # Planning accepts unresolved optional quantities. Keep raw text in the
    # frozen snapshot while materializing only quantities the typed form can use.
    data['samples'] = [{**row, 'quantity': row.get('quantity', '')
        if re.search(r'\d', row.get('quantity', '')) else ''} for row in snapshot['samples']]
    projector = IntakeDataProjector()
    form = projector.application_form(project_id, data)
    # Formal Intake keeps its existing date behavior; temporary capture also
    # retains the editor's request date for downstream Basic Information.
    raw_date = str(data.get('request_date') or '').replace('/', '-')
    try:
        captured_date = date.fromisoformat(raw_date) if raw_date else None
    except ValueError:
        captured_date = None
    form = replace(form, request_date=captured_date)
    samples = projector.sample_infos(project_id, form.form_id, data)
    return form, samples


class TemporaryProjectIntakeSource:
    """Prefer a frozen snapshot; never guess a legacy case by title or recency."""

    def __init__(self, candidates: TemporaryIntakeCandidateStore):
        self._candidates = candidates

    def validate_creation(self, snapshot, asset_ids):
        self._candidates.validate_provenance(snapshot, asset_ids)

    def resolve(self, project_id: str, context, *, source_id: str | None = None) -> dict:
        frozen = getattr(context, 'intake_snapshot_json', None)
        if frozen:
            if source_id not in {None, 'snapshot'}:
                raise ValueError('The retained intake source changed. Refresh before registering.')
            snapshot = normalize_intake_snapshot(json.loads(frozen))
            return {'snapshot': snapshot, 'source_id': 'snapshot', 'fingerprint': snapshot_fingerprint(snapshot), 'candidates': []}
        if source_id == 'manual':
            return {'snapshot': None, 'source_id': 'manual', 'fingerprint': None, 'candidates': []}
        snapshots = self._candidates.eligible_snapshots(project_id, context.source_asset_ids if context else ())
        grouped = {}
        for raw in snapshots:
            snapshot = normalize_intake_snapshot(raw)
            identity = snapshot_fingerprint(snapshot, facts_only=True)
            candidate = grouped.setdefault(identity, {'source_id': identity, 'snapshot': snapshot, 'provenance': []})
            candidate['provenance'].append({'case_id': snapshot['source_case_id'], 'asset_id': snapshot['selected_form_asset_id']})
        candidates = list(grouped.values())
        chosen = next((item for item in candidates if item['source_id'] == source_id), None)
        if len(candidates) == 1 and source_id is None:
            chosen = candidates[0]
        if source_id and chosen is None:
            raise ValueError('The selected intake source changed or is no longer available. Refresh before registering.')
        return {'snapshot': chosen['snapshot'] if chosen else None,
            'source_id': chosen['source_id'] if chosen else None,
            'fingerprint': snapshot_fingerprint(chosen['snapshot']) if chosen else None,
            'candidates': candidates if len(candidates) > 1 else []}
