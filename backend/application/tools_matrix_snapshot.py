"""Non-authoritative in-memory projection for the shared Matrix consumers."""
from decimal import Decimal
import json

from backend.domain.confirmed_matrix_authority_models import (
    ConfirmedMatrixSnapshot, ConfirmedMatrixVersion, ConfirmedMatrixGroup,
    ConfirmedMatrixRow, ConfirmedMatrixCell, ConfirmedMatrixDurationAuthority,
    ConfirmedMatrixStepTextOverride,
)
from backend.domain.enums import ConfirmedMatrixStatus
from backend.domain.matrix_contact_measurement_models import (
    point_profile_from_json, point_overrides_from_json,
)


def planning_snapshot(payload: dict) -> ConfirmedMatrixSnapshot:
    """Preserve browser row identities without creating a Project or an authority."""
    matrix_id = 'tools-planning'
    version = ConfirmedMatrixVersion(
        confirmed_matrix_id=matrix_id, project_id='', project_matrix_draft_id='',
        source_import_id='', source_snapshot_id='', confirmed_revision=0,
        is_active_authority=False, status=ConfirmedMatrixStatus.SUPERSEDED,
        confirmed_by='', confirmed_at='',
        **{key: payload.get(key) for key in ('pre_test_buffer_days', 'post_test_buffer_days',
            'sample_received_date', 'planned_test_start_date', 'planned_test_complete_date', 'estimated_completion_date')},
        point_profile=point_profile_from_json(json.dumps(payload['point_profile'])) if payload.get('point_profile') else None,
        point_overrides=point_overrides_from_json(json.dumps((payload.get('point_overrides') or []))),
    )
    groups = tuple(ConfirmedMatrixGroup(
        confirmed_group_id=g['draft_group_id'], confirmed_matrix_id=matrix_id,
        draft_group_id=g['draft_group_id'], source_group_snapshot_id=None,
        group_order=g['group_order'], group_key=g['group_key'], group_label=g['group_label'],
        sample_quantity_expression=g.get('sample_quantity_expression') or '', sample_note=g.get('sample_note'),
    ) for g in payload['groups'] if g.get('is_selected', True))
    if not groups:
        raise ValueError('Select at least one Matrix group.')
    rows = tuple(ConfirmedMatrixRow(
        confirmed_row_id=r['draft_row_id'], confirmed_matrix_id=matrix_id,
        draft_row_id=r['draft_row_id'], source_row_snapshot_id=None,
        row_order=r['row_order'], test_item=r['test_item'],
        **{k:r.get(k) for k in ('source_section','method','condition','requirement','day_expression')},
    ) for r in payload['rows'] if not r.get('is_sample_row'))
    group_ids = {g.confirmed_group_id for g in groups}
    row_ids = {r.confirmed_row_id for r in rows}
    cells = tuple(ConfirmedMatrixCell(
        confirmed_cell_id=f"{c['draft_group_id']}:{c['draft_row_id']}", confirmed_matrix_id=matrix_id,
        confirmed_group_id=c['draft_group_id'], confirmed_row_id=c['draft_row_id'], **c,
    ) for c in payload['cells'] if c['draft_group_id'] in group_ids and c['draft_row_id'] in row_ids and c['cell_value'].strip())
    durations = tuple(_duration(d, matrix_id) for d in payload.get('duration_authorities', [])
                      if d['draft_group_id'] in group_ids and d['draft_row_id'] in row_ids)
    overrides = tuple(ConfirmedMatrixStepTextOverride(
        confirmed_group_id=o['draft_group_id'], confirmed_row_id=o['draft_row_id'],
        **{k:v for k,v in o.items() if k not in ('draft_group_id','draft_row_id')},
    ) for o in (payload.get('step_text_overrides') or []) if o['draft_group_id'] in group_ids and o['draft_row_id'] in row_ids)
    return ConfirmedMatrixSnapshot(version=version, groups=groups, rows=rows, cells=cells,
                                   duration_authorities=durations, step_text_overrides=overrides)


def _duration(d: dict, matrix_id: str) -> ConfirmedMatrixDurationAuthority:
    value = Decimal(str(d['duration_value']))
    unit = d['duration_unit']
    factors = {'hour':Decimal(1), 'hours':Decimal(1), 'h':Decimal(1),
               'day':Decimal(24), 'days':Decimal(24), 'd':Decimal(24),
               'minute':Decimal(1)/60, 'minutes':Decimal(1)/60, 'min':Decimal(1)/60}
    if unit not in factors or not value.is_finite() or value < 0:
        raise ValueError('Invalid Matrix duration.')
    return ConfirmedMatrixDurationAuthority(
        confirmed_duration_authority_id=d.get('draft_duration_authority_id') or f"{d['draft_group_id']}:{d['draft_row_id']}",
        confirmed_matrix_id=matrix_id, confirmed_group_id=d['draft_group_id'], confirmed_row_id=d['draft_row_id'],
        step_sequence=d['step_sequence'], step_suffix_note=d.get('step_suffix_note') or '',
        duration_value=value, duration_unit=unit, normalized_hours=value*factors[unit],
        source_kind=d.get('source_kind','manual'), source_field=d.get('source_field',''),
        source_import_id=None, source_fingerprint=d.get('source_fingerprint',''),
        lineage_fingerprint=d.get('lineage_fingerprint',''), authority_revision=d.get('authority_revision',''),
        status=d.get('status', 'review_required'), diagnostic_code=None, diagnostic_message=None, created_at='', updated_at='',
    )
