"""Exact-version delivery review and explicit save, not laboratory release authority."""
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
from uuid import uuid4

from backend.domain.report_authoring import ReportAuthoringConflict, ReportSource


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


class ReportDelivery:
    def __init__(self, authoring, workspace, receipts, files):
        self.authoring, self.workspace, self.receipts, self.files = authoring, workspace, receipts, files

    def _content_stamp(self, state, context, review):
        # Unused retained candidates do not revoke an otherwise unchanged content
        # review. Actual consumed sources are re-read separately before saving.
        return digest({'facts': self.authoring._review_context_sha256(state, context,
            self.authoring._llcr_review_context(state, context)),
            'regions': [{'id': item['region_id'], 'sha256': item['sha256'], 'status': item['status'],
                         'reasons': item['reasons']} for item in review['regions']],
            'findings': review['findings'], 'numbering': review['numbering']})

    @staticmethod
    def _visual(output):
        preview = output.get('visual_preview') or {}
        return (preview.get('output_sha256') == output['artifact']['sha256']
            and preview.get('status') == 'visually_reviewed'
            and preview.get('reviewed_pages') == list(range(1, preview.get('page_count', 0) + 1))
            and preview.get('page_count', 0) > 0)

    def status(self, project_id):
        state, _ = self.authoring.state(project_id)
        if not state.outputs:
            return {'can_save': False, 'issues': [{'code': 'working_copy_missing', 'message': 'Choose a report working copy first.'}],
                'operation': None, 'preview_sha256': None}
        output = state.outputs[-1]
        customer = next((item for item in reversed(state.customer_outputs) if item['parent_output_id'] == output['output_id']), None)
        return self.preview(project_id, {'expected_revision': state.revision, 'output_id': output['output_id'],
            'output_sha256': output['artifact']['sha256'], 'customer_output_id': customer['output_id'] if customer else None})

    def preview(self, project_id, request):
        service = self.authoring
        state, context = service._editable(project_id, request['expected_revision'])
        output = service._current_output(state, request['output_id'])
        if output['artifact']['sha256'] != request['output_sha256']:
            raise ReportAuthoringConflict('The working report changed. Review this version again.')
        issues = []
        def issue(code, message):
            issues.append({'code': code, 'message': message})
        service.assets.read(project_id, ReportSource(**output['artifact']))
        review = service.document_review.inspect(project_id, output['output_id'], state.revision)
        coverage = service.coverage(project_id)
        if not coverage['complete']:
            issue('coverage_incomplete', 'Some Matrix results or evidence are missing or need confirmation.')
        if review['findings'] or not review['numbering']['ready']:
            issue('content_conflict', 'Resolve the reported content, photo or figure-reference conflicts.')
        if review['base_role'] == 'layout_reference':
            if not review['complete']:
                issue('inherited_content', 'Confirm inherited regions against this project evidence before saving.')
        elif output.get('content_review', {}).get('content_sha256') != self._content_stamp(state, context, review):
            issue('content_review_required', 'Review the retained content of this exact project report.')
        if not self._visual(output):
            issue('internal_visual_required', 'Inspect every page of this exact Internal Report Word preview.')
        elif output.get('visual_preview'):
            service.assets.read(project_id, ReportSource(**output['visual_preview']['artifact']))
        selected = request.get('customer_output_id')
        customer = next((item for item in state.customer_outputs if item['output_id'] == selected), None) if selected else None
        if selected and (not customer or customer['parent_output_id'] != output['output_id']):
            issue('customer_parent_changed', 'Choose a customer copy derived from this Internal Report version.')
        if not customer:
            issue('customer_copy_required', 'Generate and check the matching customer review copy.')
        else:
            service.assets.read(project_id, ReportSource(**customer['artifact']))
            audit = customer.get('audit') or {}
            fingerprint = service._review_context_sha256(state, context, service._llcr_review_context(state, context))
            if not audit.get('passed') or audit.get('output_sha256') != customer['artifact']['sha256'] or audit.get('review_context_sha256') != fingerprint:
                issue('customer_disclosure_required', 'Run the current customer content and confidentiality check; unresolved items cannot be waived here.')
            if not self._visual(customer):
                issue('customer_visual_required', 'Inspect every page of this exact customer Word preview.')
            else:
                service.assets.read(project_id, ReportSource(**customer['visual_preview']['artifact']))
        used_sources = {state.base_source_id} | {item.source_id for item in state.mappings}
        for ancestor in service.document_review._ancestors(state, output):
            used_sources.update(item['source_id'] for item in ancestor.get('region_decisions', []))
            used_sources.update(item['source_id'] for item in ancestor.get('evidence', {}).get('assignments', []))
        for result_id in service.active_result_ids(state):
            try:
                result = service._confirmed_result(state, context, result_id)
                used_sources.add(result['source_id'])
            except (LookupError, ValueError, OSError):
                issue('source_unavailable', 'An applied result no longer has readable current evidence.')
        for source_id in used_sources - {None}:
            source = service._source(state, source_id)
            if not service.document_review._source_current(state, source_id, source.sha256):
                issue('source_unavailable', 'A report dependency is missing or superseded. Review its current source.')
        workspace = None
        if self.workspace is None:
            issue('workspace_unavailable', 'The project save location is not configured.')
        else:
            try:
                workspace = self.workspace.snapshot(project_id)
            except (ValueError, OSError, LookupError) as exc:
                issue('workspace_unavailable', str(exc))
        context_hash = digest({'review': self._content_stamp(state, context, review), 'coverage': coverage,
            'internal': output['artifact']['sha256'], 'internal_visual': output.get('visual_preview'),
            'customer': customer, 'context': context})
        preview_hash = digest({'context': context_hash, 'workspace': workspace})
        active = self.receipts.active(project_id) if self.receipts else None
        operation = self._public_receipt(active) if active else self.public_projection(state.delivery)
        pending_projection = state.delivery and state.delivery.get('status') != 'completed'
        operation_matches = bool(operation and operation.get('output_id') == output['output_id']
            and operation.get('customer_output_id') == selected and operation.get('basis_sha256') == context_hash)
        return {'can_save': not issues and not active and not pending_projection, 'issues': issues, 'output_id': output['output_id'],
            'output_sha256': output['artifact']['sha256'], 'customer_output_id': selected,
            'preview_sha256': preview_hash, 'review_sha256': review['review_sha256'],
            'context_sha256': context_hash, 'workspace': self._public_workspace(workspace),
            'operation': operation, 'operation_matches_current': operation_matches,
            'expected_revision': state.revision, '_workspace': workspace}

    @staticmethod
    def public_projection(projection):
        return {key: value for key, value in projection.items() if key != 'approved_intent'} if projection else None

    @staticmethod
    def _public_workspace(snapshot):
        if snapshot is None:
            return None
        return {'files': [{'role': item['role'], 'file_name': Path(item['target']).name,
            'replaces_existing': bool(item['current']), 'archive_required': bool(item['current'])}
            for item in snapshot['items']], 'notice': 'Existing reports are retained in History/Report. This is not formal release.'}

    @staticmethod
    def _public_receipt(record):
        request = record['context']['request'] if 'request' in record['context'] else {}
        return {'operation_id': record['operation_id'], 'status': record['status'],
            'output_id': request.get('output_id'), 'output_sha256': request.get('output_sha256'),
            'customer_output_id': request.get('customer_output_id'),
            'customer_sha256': next((item['sha256'] for item in record['items'] if item['role'] == 'customer'), None),
            'basis_sha256': record['context'].get('context_sha256'),
            'items': [{'role': item['role'], 'file_name': Path(item['target']).name, 'status': item['status']} for item in record['items']]}

    def confirm_content(self, project_id, request):
        service = self.authoring
        state, context, output, review = service.document_review.current(project_id, request)
        if output in state.customer_outputs:
            raise ValueError('Review retained content on the Internal Report, not its customer copy.')
        if review['base_role'] != 'original' or request['review_sha256'] != review['review_sha256']:
            raise ReportAuthoringConflict('Only the current project original can use this retained-content confirmation. Review its exact version.')
        if review['findings'] or not review['numbering']['ready']:
            raise ValueError('Resolve detected content conflicts before recording retained-content review.')
        record = {'review_sha256': review['review_sha256'], 'confirmed_by': request['confirmed_by'],
            'confirmed_at': service._now(), 'notes': request['notes'], 'content_sha256': self._content_stamp(state, context, review)}
        return service.document_review._save_output(state, output, content_review=record)

    def save(self, project_id, request):
        service = self.authoring
        operation_id = request.get('operation_id')
        if not operation_id:
            previous, _ = service.state(project_id)
            saved = previous.delivery or {}
            if saved.get('status') == 'completed' and saved.get('preview_sha256') == request.get('preview_sha256') and all(
                    saved.get(key) == request.get(key) for key in ('output_id', 'output_sha256', 'customer_output_id')):
                return self.save(project_id, {'operation_id': saved['operation_id']})
        if operation_id:
            state, _ = service.state(project_id)
            try:
                record = self.receipts.read(project_id, operation_id)
            except LookupError:
                stored = (state.delivery or {}).get('approved_intent')
                if not stored or stored['operation_id'] != operation_id:
                    raise ReportAuthoringConflict('The approved report save intent is unavailable.')
                approved = stored['context']
                check = self.preview(project_id, {**approved['request'], 'expected_revision': state.revision})
                if check['issues'] or check['context_sha256'] != approved['context_sha256']:
                    raise ReportAuthoringConflict('Report checks changed before the save began. Retain the pending intent for recovery review.')
                self.workspace.revalidate(project_id, approved['workspace'])
                record = self.receipts.begin(project_id, operation_id, stored['context'], stored['items'])
            if not state.delivery or state.delivery.get('intent_sha256') != record['intent_sha256']:
                raise ReportAuthoringConflict('The original save intent cannot be proven. Retain files for review.')
            if record['status'] == 'completed' and state.delivery.get('status') == 'completed':
                for item in record['items']:
                    self.files.publish_regenerated_current(source_path=Path(item['source']), expected_source_sha256=item['sha256'],
                        current_path=Path(item['current']) if item['current'] else None, expected_current_sha256=item['old_sha256'],
                        target_path=Path(item['target']), history_root=Path(item['history_root']), persist=lambda _: None,
                        receipt=self.receipts.item(project_id, operation_id, item['role']))
                return state
            approved = record['context']
            identity = {**approved['request'], 'expected_revision': state.revision}
            current = self.preview(project_id, identity)
            if current['issues'] or current['context_sha256'] != approved['context_sha256']:
                raise ReportAuthoringConflict('Report evidence changed during an unfinished save. Retain saved files and review recovery.')
            self.workspace.revalidate(project_id, approved['workspace'])
        else:
            current = self.preview(project_id, request)
            if request['preview_sha256'] != current['preview_sha256'] or not current['can_save']:
                raise ReportAuthoringConflict('Delivery checks or target reports changed. Inspect the current save preview.')
            state, _ = service._editable(project_id, request['expected_revision'])
            operation_id = uuid4().hex
            customer = next(item for item in state.customer_outputs if item['output_id'] == request['customer_output_id'])
            outputs = {'internal': state.outputs[-1], 'customer': customer}
            items = [{**item, 'source': str(service.assets.path(project_id, ReportSource(**outputs[item['role']]['artifact']))),
                'sha256': outputs[item['role']]['artifact']['sha256']} for item in current['_workspace']['items']]
            approved = {'request': {key: request[key] for key in ('output_id', 'output_sha256', 'customer_output_id')},
                'context_sha256': current['context_sha256'], 'workspace': current['_workspace'],
                'confirmed_by': request['confirmed_by'], 'preview_sha256': current['preview_sha256']}
            record = self.receipts.prepare(project_id, operation_id, approved, items)
            state = service.repository.save_durable(replace(state, delivery={**self._public_receipt(record),
                'intent_sha256': record['intent_sha256'], 'approved_intent': record}), state.revision)
            record = self.receipts.begin(project_id, operation_id, approved, items)
        for item in record['items']:
            def validate():
                self.workspace.revalidate(project_id, approved['workspace'])
                now, _ = service.state(project_id)
                check = self.preview(project_id, {**approved['request'], 'expected_revision': now.revision})
                if check['issues'] or check['context_sha256'] != approved['context_sha256']:
                    raise ReportAuthoringConflict('Report evidence changed while saving. Resume only after recovery review.')
            def persist(result):
                nonlocal state
                validate()
                now, _ = service.state(project_id)
                projected = {**(now.delivery or {}), 'status': 'saving', 'last_saved_role': item['role'],
                    'saved_sha256': result.current_sha256}
                state = service.repository.save_durable(replace(now, delivery=projected), now.revision)
            try:
                self.files.publish_regenerated_current(source_path=Path(item['source']), expected_source_sha256=item['sha256'],
                    current_path=Path(item['current']) if item['current'] else None, expected_current_sha256=item['old_sha256'],
                    target_path=Path(item['target']), history_root=Path(item['history_root']), persist=persist,
                    pre_publish=validate, receipt=self.receipts.item(project_id, operation_id, item['role']))
            except (OSError, RuntimeError, ValueError) as exc:
                raise ReportAuthoringConflict(f"{item['role'].title()} report save is unfinished. Close any open Word file, then resume this operation. {exc}") from exc
        record = self.receipts.read(project_id, operation_id)
        now, _ = service.state(project_id)
        final = service.repository.save_durable(replace(now, delivery={**self._public_receipt(record), 'status': 'completed',
            'intent_sha256': record['intent_sha256'], 'confirmed_by': approved['confirmed_by'],
            'saved_at': service._now(), 'formal_release': False, 'preview_sha256': approved['preview_sha256']}), now.revision)
        self.receipts.complete(project_id, operation_id)
        return final
