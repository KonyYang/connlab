"""Read-only report views of the existing LLCR authority; no duplicate result store."""
from dataclasses import asdict
from decimal import Decimal
from hashlib import sha256
import json


def dataset_sha256(dataset):
    def decimal(value):
        if isinstance(value, Decimal):
            return str(value)
        raise TypeError(f'Unsupported dataset value: {type(value).__name__}')
    snapshot = asdict(dataset)
    # Applied report evidence predates raw lineage: older readers substituted the
    # calculated result in these three fingerprint fields. Keep that wire identity
    # here, while leaving absent raw readings unavailable in the workspace.
    for entry in snapshot['payload']['entries']:
        for measurement in entry['measurements']:
            if measurement['raw_value'] is None:
                measurement['raw_value'] = measurement['value']
            if not measurement['raw_unit']:
                measurement['raw_unit'] = measurement['unit']
            if not measurement['raw_source_cell']:
                measurement['raw_source_cell'] = measurement['source_cell']
    return sha256(json.dumps(snapshot, sort_keys=True, separators=(',', ':'),
        ensure_ascii=False, allow_nan=False, default=decimal).encode('utf-8')).hexdigest()


def entry_id(dataset, entry):
    return f'llcr:{dataset.dataset_id}:{entry.result_id}'


def describe_dataset(dataset):
    return {'dataset_id': dataset.dataset_id, 'revision': dataset.revision,
        'source_file_name': dataset.source.file_name, 'source_sha256': dataset.source.sha256,
        'entries': [{'entry_id': entry_id(dataset, item), 'group_id': item.confirmed_group_id,
            'row_id': item.confirmed_row_id, 'group_label': item.group_label,
            'step_token': item.matrix_step_token, 'stage': item.stage, 'stage_label': item.stage_label,
            'outcome': item.confirmed_outcome,
            'summary': {'min': str(item.summary_min), 'max': str(item.summary_max),
                'average': str(item.summary_average), 'unit': item.requirement_unit}}
            for item in dataset.payload.entries]}


def coverage_results(dataset):
    return tuple({'result_id': entry_id(dataset, item), 'kind': 'llcr',
        'target': {'group_id': item.confirmed_group_id, 'row_id': item.confirmed_row_id,
            'group_label': item.group_label, 'step_token': item.matrix_step_token},
        'outcome': 'pending' if item.confirmed_outcome == 'not_determined' else item.confirmed_outcome,
        'data': {}} for item in dataset.payload.entries)


def applied_dataset_evidence(outputs):
    for output in reversed(outputs):
        if output.get('operation') == 'prepare_base':
            break
        evidence = output.get('evidence', {})
        if output.get('operation') == 'llcr_update':
            return {'dataset_id': evidence.get('dataset_revision_id'),
                    'sha256': evidence.get('llcr_dataset_sha256')}
        if output.get('operation') == 'batch_assembly' and evidence.get('llcr_dataset_id'):
            return {'dataset_id': evidence['llcr_dataset_id'],
                    'sha256': evidence.get('llcr_dataset_sha256')}
    return None
