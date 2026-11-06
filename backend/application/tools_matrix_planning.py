"""Stateless Matrix planning operations; no project repositories or commits."""
from datetime import datetime, timezone
from backend.application.source_matrix_import_builder import prepare_source_matrix_import
from backend.application.matrix_import_draft_builder import build_selected_only_draft


def prepare_planning_matrix(preview: dict) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    keys = tuple(group['group_key'] for group in preview.get('groups', []))
    if not keys:
        raise ValueError('Select at least one Matrix group.')
    source = prepare_source_matrix_import(project_id='', draft_id=None,
        source_document_path=preview.get('source_document_path', ''), source_document_name=preview.get('source_document_name', ''),
        source_format=preview.get('source_format', ''), source_asset_id=None, source_case_id=None, source_draft_id=None,
        payload=preview, created_at=now, selected_group_keys_override=keys, task261_commit_fingerprint=None)
    draft = build_selected_only_draft(project_id='', source_import_id=source.import_record.import_id,
        source_snapshot_id=source.snapshot.snapshot_id, selected_group_keys=keys, source_snapshot=source.snapshot,
        preview_payload=preview, created_at=now)
    return {'source_import_id':source.import_record.import_id,'source_snapshot_id':source.snapshot.snapshot_id,
        'selected_group_keys_committed':keys,'commit_status':'planning_only','project_matrix_draft':draft,
        'method_authority_sync':{'status':'preserved','updated_count':0,'current_count':len(draft.rows),'review_count':0,
            'standard_resource_id':None,'effective_worksheet_name':None,'catalog_fingerprint':None,'context_fingerprint':'',
            'rows':[],'warning':None}}


def evaluate_planning_fees(payload: dict):
    from backend.application.tools_matrix_snapshot import planning_snapshot
    from backend.application.confirmed_matrix_fee_draft_service import build_fee_draft_from_snapshot
    from backend.application.matrix_test_points_authority import effective_matrix_point_profile
    from backend.modules.fee_evaluation import load_active_fee_rule_library
    snapshot = planning_snapshot(payload)
    return build_fee_draft_from_snapshot(snapshot=snapshot, library=load_active_fee_rule_library(),
        effective_point_profile=effective_matrix_point_profile(snapshot)).draft
