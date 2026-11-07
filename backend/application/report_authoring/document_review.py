"""Coverage and rendering evidence for the selected working copy, never release authority."""
from dataclasses import asdict, replace
from hashlib import sha256
from pathlib import Path
import re
from uuid import uuid4

from backend.application.report_authoring.assembly import digest
from backend.application.report_authoring.photo_plan import photo_candidates
from backend.domain.report_authoring import ReportAuthoringConflict, ReportSource


class ReportDocumentReview:
    def __init__(self, authoring, inspector, renderer):
        self.authoring, self.inspector, self.renderer = authoring, inspector, renderer

    def _source_current(self, state, source_id, expected_sha):
        source = self.authoring._source(state, source_id)
        latest = next(item for item in reversed(state.sources)
                      if self.authoring._source_family(item) == self.authoring._source_family(source))
        self.authoring.assets.read(state.project_id, source)
        return source.sha256 == expected_sha and latest.source_id == source_id

    @staticmethod
    def _ancestors(state, output):
        outputs = {item['output_id']: item for item in state.outputs}
        seen = set()
        while output and output['output_id'] not in seen:
            seen.add(output['output_id'])
            yield output
            if output['operation'] == 'prepare_base':
                break
            output = outputs.get(output.get('parent_output_id'))

    def current(self, project_id, request):
        service = self.authoring
        state, context = service._editable(project_id, request['expected_revision'])
        output = service._current_output(state, request['output_id'])
        if output['artifact']['sha256'] != request.get('output_sha256', output['artifact']['sha256']):
            raise ReportAuthoringConflict('The selected report changed. Reload its working copy.')
        review = self.inspect(project_id, output['output_id'], state.revision)
        return state, context, output, review

    def inspect(self, project_id, output_id, expected_revision):
        service = self.authoring
        state, context = service._editable(project_id, expected_revision)
        output = service._current_output(state, output_id)
        artifact = ReportSource(**output['artifact'])
        service.assets.read(project_id, artifact)
        path = service.assets.path(project_id, artifact)
        report = self.inspector.inspect(path)
        grouped = {}
        for region in report['regions']:
            grouped.setdefault(region['group_id'], []).append(region)
        group_hashes = {key: digest([{'id': item['region_id'], 'sha256': item['sha256']} for item in items]) for key, items in grouped.items()}
        base = service._source(state, output['base_source_id'])
        reference = base.role == 'layout_reference'
        applied = set(service.active_result_ids(state))
        results = [item for item in state.results if item['result_id'] in applied]
        ancestry = list(self._ancestors(state, output))
        decisions = {item['region_id']: item for ancestor in reversed(ancestry)
                     for item in ancestor.get('region_decisions', [])}
        applied_regions = {item['region_id']: item for ancestor in reversed(ancestry)
                           for item in ancestor.get('evidence', {}).get('applied_regions', [])}
        findings = list(report['issues'])
        for region in report['regions']:
            value = region['text']
            conflicts = []
            identities = set(re.findall(r'\bDL-\d{4}-\d{2}-\d{3}[A-Za-z0-9]*\b', value, re.I))
            if identities - {context['dl_number']} and not region['owned_result'].startswith('connlab-report-result:'):
                conflicts.append('Old project identity remains outside a scoped adopted result.')
            mappings = [item for item in state.mappings if item.status == 'confirmed' and item.report_target
                        and (not item.matrix_id or item.matrix_id == context['matrix_id'])
                        and self._source_current(state, item.source_id, service._source(state, item.source_id).sha256)
                        and (item.report_target['part'], item.report_target['paragraph']) ==
                        (region['target']['part'], region['target']['paragraph'])]
            for mapping in mappings:
                if mapping.value not in value:
                    conflicts.append(f'Confirmed {mapping.fact_role} value is not present: {mapping.value}')
                if region['kind'] in {'revision_date', 'authorization_date'} and mapping.fact_role != region['kind']:
                    conflicts.append('Revision date and authorization date refer to different facts.')
            for result in results:
                if not region['owned_result'].endswith(result['result_id']):
                    continue
                data = result.get('data', {})
                if result['kind'] == 'mechanical':
                    kind = data.get('test_type', '')
                    if kind == 'retention' and re.search(r'\bmating\b', value, re.I):
                        conflicts.append('Mating heading is attached to confirmed retention evidence.')
                    colors = {str(row.get('color', '')).casefold() for row in data.get('rows', [])} - {''}
                    if 'orange' in value.casefold() and len(colors) > 1 and not all(color in value.casefold() for color in colors):
                        conflicts.append('A single-color heading does not describe all confirmed specimen colors.')
            decision = decisions.get(region['region_id']) or decisions.get(region['group_id'])
            if decision:
                try:
                    expected_hash = group_hashes[region['group_id']] if decision['region_id'] == region['group_id'] else region['sha256']
                    if (decision['region_sha256'] != expected_hash or decision.get('matrix_id') != context['matrix_id']
                            or not self._source_current(state, decision['source_id'], decision['source_sha256'])):
                        decision = None
                except (LookupError, ValueError, OSError):
                    decision = None
            owned = False
            record = applied_regions.get(region['region_id'])
            for result in results:
                if (region['owned_result'].endswith(result['result_id']) and record
                        and record['sha256'] == region['sha256'] and result['outcome'] != 'pending'):
                    try:
                        service._confirmed_result(state, context, result['result_id'])
                        owned = True
                    except (ValueError, LookupError, OSError):
                        pass  # The region stays unverified and its stale source remains visible.
            structural = region['text'].strip() in {'E-3707', 'E-4515'} or 'End of Report' in region['text']
            status = 'conflict' if conflicts else ('verified' if mappings or owned or structural or decision else ('needs_review' if reference else 'retained'))
            region.update(status=status, reasons=conflicts or (['Confirm this inherited region against current project evidence.'] if status == 'needs_review' else []), decision=decision)
            findings.extend({'code': 'semantic_conflict', 'message': message, 'location': region['region_id']} for message in conflicts)
        assigned = {}
        for ancestor in reversed(ancestry):
            evidence = ancestor.get('evidence', {})
            selected = {item['slot_id']: item for item in evidence.get('assignments', [])}
            for slot in evidence.get('applied_photo_slots', []):
                assignment = selected.get(slot['slot_id'])
                if assignment:
                    assigned[slot['slot_id']] = (slot, assignment)
        for slot in report['slots']:
            recorded = assigned.get(slot['slot_id'])
            valid = False
            if recorded:
                prior, assignment = recorded
                source = service._source(state, assignment['source_id'])
                valid = prior == slot and self._source_current(state, source.source_id, assignment.get('source_sha256', source.sha256))
            slot['coverage'] = 'replaced' if valid else ('needs_review' if reference else 'retained')
            if reference and not valid:
                findings.append({'code': 'inherited_photo', 'message': 'An inherited photograph has not been replaced or scoped to this project.', 'location': slot['slot_id']})
        numbering = self.inspector.numbering(path)
        groups = []
        for key, items in grouped.items():
            statuses = {item['status'] for item in items}
            status = 'conflict' if 'conflict' in statuses else ('verified' if statuses == {'verified'} else 'needs_review')
            groups.append({'region_id': key, 'sha256': group_hashes[key], 'kind': items[0]['group_title'],
                'text': '\n'.join(item['text'] for item in items), 'status': status,
                'reasons': list(dict.fromkeys(reason for item in items for reason in item['reasons'])),
                'paragraph_count': len(items), 'region_ids': [item['region_id'] for item in items]})
        snapshot = {'output': artifact.sha256, 'sources': [asdict(item) for item in state.sources],
                    'mappings': [asdict(item) for item in state.mappings], 'context': context, 'decisions': decisions}
        return {**report, 'output_id': output_id, 'output_sha256': artifact.sha256,
            'base_role': base.role, 'findings': findings, 'numbering': numbering,
            'photo_candidates': photo_candidates(state, report['slots']),
            'region_groups': groups,
            'review_sha256': digest(snapshot),
            'complete': not findings and all(item['status'] == 'verified' for item in report['regions'])
                and service.coverage(project_id)['complete'],
            'notice': 'Structural checks do not confirm measurements, visual layout or formal release.'}

    def confirm_regions(self, project_id, request):
        service = self.authoring
        state, context, output, review = self.current(project_id, request)
        if review['review_sha256'] != request['review_sha256']:
            raise ReportAuthoringConflict('The report evidence changed. Inspect again before recording regional decisions.')
        regions = {item['region_id']: item for item in [*review['regions'], *review['region_groups']]}
        decisions = {item['region_id']: item for item in output.get('region_decisions', [])}
        for selected in request['decisions']:
            region = regions.get(selected['region_id'])
            if not region or region['sha256'] != selected['region_sha256']:
                raise ReportAuthoringConflict('A selected region changed.')
            if region['status'] == 'conflict':
                raise ValueError('Correct the conflicting report content; an acknowledgement cannot clear a detected error.')
            source = service._source(state, selected['source_id'])
            service.assets.read(project_id, source)
            if source.source_id == state.base_source_id:
                raise ValueError('Use current project evidence, not the historical layout itself, to adopt inherited content.')
            if not self._source_current(state, source.source_id, source.sha256):
                raise ValueError('Choose the latest retained evidence version for this regional decision.')
            decisions[region['region_id']] = {**selected, 'source_sha256': source.sha256, 'matrix_id': context['matrix_id'],
                'confirmed_by': request['confirmed_by'], 'confirmed_at': service._now()}
        return self._save_output(state, output, region_decisions=list(decisions.values()))

    def _save_output(self, state, output, **updates):
        return self.authoring.repository.save(replace(state, outputs=tuple(
            {**entry, **updates} if entry['output_id'] == output['output_id'] else entry for entry in state.outputs)), state.revision)

    def render(self, project_id, request):
        service = self.authoring
        state, context, output, review = self.current(project_id, request)
        existing = output.get('visual_preview')
        if existing and existing['output_sha256'] == output['artifact']['sha256']:
            service.assets.read(project_id, ReportSource(**existing['artifact']))
            return state
        if self.renderer is None:
            raise ValueError('Microsoft Word preview is not configured on this computer.')
        artifact = ReportSource(**output['artifact'])
        content = service.assets.read(project_id, artifact)
        plan = output.get('evidence', {}).get('document_plan', {})
        anchors = [item['new'] for item in plan.get('facts', [])]
        anchors += [item['new'] for item in (plan.get('figure_numbering') or {}).get('replacements', [])]
        anchors += [item[key] for item in plan.get('results', []) for key in ('new_result', 'new_comment') if item.get(key)]
        selected_slots = {item['slot_id'] for item in output.get('evidence', {}).get('assignments', [])}
        anchors += [slot['caption'] for slot in review['slots'] if slot['slot_id'] in selected_slots and slot['caption']]
        review['changed_text_anchors'] = anchors
        rendered = self.renderer.render(content, review=review)
        current, now = service._editable(project_id, state.revision)
        if now != context or service.assets.read(project_id, artifact) != content:
            raise ReportAuthoringConflict('The report or project changed while Word was rendering. Reload before previewing.')
        pdf = ReportSource(uuid4().hex, 'visual_preview', Path(artifact.file_name).stem + '.pdf',
            sha256(rendered['content']).hexdigest(), len(rendered['content']), service._now(), context['dl_number'])
        service.assets.retain(project_id, pdf, rendered['content'])
        record = {key: value for key, value in rendered.items() if key != 'content'}
        record.update(artifact=asdict(pdf), output_sha256=artifact.sha256, created_at=service._now(),
                      status='rendered_not_reviewed')
        return self._save_output(current, output, visual_preview=record)

    def preview_content(self, project_id, output_id):
        service = self.authoring
        state, _ = service.state(project_id)
        output = next((item for item in state.outputs if item['output_id'] == output_id), None)
        preview = output.get('visual_preview') if output else None
        if not preview or preview['output_sha256'] != output['artifact']['sha256']:
            raise LookupError('No Word preview is retained for this exact working version.')
        artifact = ReportSource(**preview['artifact'])
        return service.assets.read(project_id, artifact), artifact.file_name

    def review_pages(self, project_id, request):
        state, _, output, review = self.current(project_id, request)
        preview = output.get('visual_preview')
        if not preview or preview['artifact']['sha256'] != request['preview_sha256']:
            raise ReportAuthoringConflict('The Word preview changed; review this version again.')
        pages = sorted(set(request['pages']))
        if pages != list(range(1, preview['page_count'] + 1)):
            raise ValueError('Review every page of this exact Word preview; do not assume a fixed page count.')
        return self._save_output(state, output, visual_preview={**preview, 'status': 'visually_reviewed',
            'reviewed_pages': pages, 'reviewed_by': request['confirmed_by'], 'reviewed_at': self.authoring._now(),
            'notes': request['notes'], 'content_complete': review['complete']})
