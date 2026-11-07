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
        try:
            source = self.authoring._source(state, source_id)
            latest = next(item for item in reversed(state.sources)
                          if self.authoring._source_family(item) == self.authoring._source_family(source))
            self.authoring.assets.read(state.project_id, source)
            return source.sha256 == expected_sha and latest.source_id == source_id
        except (LookupError, ValueError, OSError):
            return False

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
        customer = next((item for item in state.customer_outputs if item['output_id'] == request['output_id']), None)
        if customer:
            if not state.outputs or customer['parent_output_id'] != state.outputs[-1]['output_id']:
                raise ReportAuthoringConflict('The customer copy belongs to an older Internal Report. Regenerate it before review.')
            if customer['artifact']['sha256'] != request['output_sha256']:
                raise ReportAuthoringConflict('The selected customer copy changed.')
            service.assets.read(project_id, ReportSource(**customer['artifact']))
            return state, context, customer, {'complete': False, 'regions': [], 'numbering': {}, 'slots': []}
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
        valid_results = {}
        for result in results:
            try:
                valid_results[result['result_id']] = service._confirmed_result(state, context, result['result_id'])
            except (LookupError, ValueError, OSError):
                continue
        source_cache = {}
        sources = {item.source_id: item for item in state.sources}
        def source_current(source_id, expected_sha):
            key = (source_id, expected_sha)
            if key not in source_cache:
                source_cache[key] = self._source_current(state, source_id, expected_sha)
            return source_cache[key]
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
            recorded = applied_regions.get(region['region_id'])
            result_tag = region['owned_result'] or region.get('associated_result', '')
            region_result = next((item for key, item in valid_results.items()
                if result_tag == 'connlab-report-result:' + key and recorded and recorded['sha256'] == region['sha256']), None)
            adopted = (region_result or {}).get('data', {}).get('adoption', {})
            allowed_ids = {context['dl_number'].upper()}
            if adopted.get('confirmed') and region_result['kind'] in {'external_reference', 'linked_temperature'}:
                allowed_ids.update(value.upper() for value in re.findall(r'\bDL-\d{4}-\d{2}-\d{3}[A-Za-z0-9]*\b', adopted.get('report_identity', ''), re.I))
            if {value.upper() for value in identities} - allowed_ids:
                conflicts.append('Old project identity remains outside a scoped adopted result.')
            targeted_mappings = [item for item in state.mappings if item.status == 'confirmed' and item.report_target
                        and (not item.matrix_id or item.matrix_id == context['matrix_id'])
                        and (item.report_target['part'], item.report_target['paragraph']) ==
                        (region['target']['part'], region['target']['paragraph'])]
            mappings = [item for item in targeted_mappings if item.source_id in sources and source_current(item.source_id, sources[item.source_id].sha256)]
            for mapping in mappings:
                if mapping.value not in value:
                    conflicts.append(f'Confirmed {mapping.fact_role} value is not present at the recorded location: {mapping.value}. If content moved, reselect its target and confirm the mapping; this check does not establish that the business value is wrong.')
                if region['kind'] in {'revision_date', 'authorization_date'} and mapping.fact_role != region['kind']:
                    conflicts.append('Revision date and authorization date refer to different facts.')
            for result in valid_results.values():
                if result_tag != 'connlab-report-result:' + result['result_id'] or not region.get('semantic_heading'):
                    continue
                data = result.get('data', {})
                if result['kind'] == 'mechanical':
                    kind = data.get('test_type', '')
                    if kind == 'retention' and re.search(r'\bmating\b', value, re.I):
                        conflicts.append('Mating heading is attached to confirmed retention evidence.')
                    colors = {str(row.get('color', '')).casefold() for row in data.get('rows', [])} - {''}
                    mentioned_colors = {color for color in colors if re.search(r'\b' + re.escape(color) + r'\b', value, re.I)}
                    if mentioned_colors and len(colors) > 1 and mentioned_colors != colors:
                        conflicts.append('A single-color heading does not describe all confirmed specimen colors.')
            decision = decisions.get(region['region_id']) or decisions.get(region['group_id'])
            if decision:
                try:
                    expected_hash = group_hashes[region['group_id']] if decision['region_id'] == region['group_id'] else region['sha256']
                    if (decision['region_sha256'] != expected_hash or decision.get('matrix_id') != context['matrix_id']
                            or not source_current(decision['source_id'], decision['source_sha256'])):
                        decision = None
                except (LookupError, ValueError, OSError):
                    decision = None
            owned = region_result is not None and region_result['outcome'] != 'pending'
            structural = value.strip() in {'E-3707', 'E-4515'} or bool(re.fullmatch(r'[\s*\-–—]*End of Report[\s*\-–—]*', value, re.I))
            whole_fact = any(value.strip() == mapping.value.strip() for mapping in mappings)
            status = 'conflict' if conflicts else ('verified' if whole_fact or owned or structural or decision else
                ('partially_verified' if mappings else ('needs_review' if reference else 'retained')))
            reasons = conflicts or (['Confirmed mappings prove only the listed facts, not the other wording, measurements or Pass in this region.'] if status == 'partially_verified' else
                (['Confirm this inherited region against current project evidence.'] if status == 'needs_review' else []))
            if len(mappings) != len(targeted_mappings):
                reasons.append('Supporting evidence is missing or superseded; its old confirmation is not reused.')
            region.update(status=status, reasons=reasons, decision=decision,
                          confirmed_facts=[{'fact_role': item.fact_role, 'value': item.value, 'source_id': item.source_id} for item in mappings])
            findings.extend({'code': 'semantic_conflict', 'message': message, 'location': region['region_id']} for message in conflicts)
        assigned = {}
        for ancestor in reversed(ancestry):
            evidence = ancestor.get('evidence', {})
            if evidence.get('photo_plan') and evidence['photo_plan']['matrix_id'] != context['matrix_id']:
                continue
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
                source = sources.get(assignment['source_id'])
                valid = bool(source) and prior == slot and source_current(source.source_id, assignment.get('source_sha256', source.sha256))
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
                    'mappings': [asdict(item) for item in state.mappings], 'results': list(state.results),
                    'active_results': sorted(applied), 'context': context, 'decisions': decisions}
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
        if output in state.customer_outputs:
            raise ValueError('Regional content decisions apply to the Internal Report, not its customer projection.')
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
        collection = 'customer_outputs' if output in state.customer_outputs else 'outputs'
        entries = tuple({**entry, **updates} if entry['output_id'] == output['output_id'] else entry
                        for entry in getattr(state, collection))
        return self.authoring.repository.save(replace(state, **{collection: entries}), state.revision)

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
        output = next((item for item in (*state.outputs, *state.customer_outputs) if item['output_id'] == output_id), None)
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
