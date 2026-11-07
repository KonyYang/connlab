"""A reviewed set of existing section updates produces one immutable working version."""
from dataclasses import asdict, replace
from hashlib import sha256
import json
from uuid import uuid4

from backend.domain.report_authoring import ReportAuthoringConflict, ReportSource
from backend.application.report_authoring.llcr_projection import coverage_results, dataset_sha256


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()


class ReportAssembly:
    def __init__(self, authoring, writer):
        self.authoring = authoring
        self.writer = writer

    def is_current(self, state, context, plan):
        if not state.outputs or state.outputs[-1]['output_id'] != plan['base_output_id']:
            return False
        if context != plan.get('context_snapshot'):
            return False
        if plan.get('request', {}).get('photo_plan_id') != (state.outputs[-1].get('photo_plan', {}).get('plan_id') if plan.get('request', {}).get('photo_plan_id') else None):
            return False
        sources = {item.source_id: item for item in state.sources}
        for recorded in plan.get('source_snapshots', []):
            source = sources.get(recorded['source_id'])
            if source is None or asdict(source) != recorded:
                return False
            family = (source.role, source.file_name.casefold(), source.source_locator)
            latest = next(item for item in reversed(state.sources)
                          if (item.role, item.file_name.casefold(), item.source_locator) == family)
            if latest.source_id != source.source_id:
                return False
        mappings = {item.mapping_id: asdict(item) for item in state.mappings}
        if any(mappings.get(item['mapping_id']) != item for item in plan.get('mapping_snapshots', [])):
            return False
        if plan.get('llcr_snapshot'):
            try:
                dataset = self.authoring.sections.selected_llcr_dataset(
                    state.project_id, plan['llcr_snapshot']['dataset_id'], context['matrix_id'])
            except (ValueError, LookupError):
                return False
            if dataset_sha256(dataset) != plan['llcr_snapshot']['sha256']:
                return False
        return True

    def _inputs(self, project_id, state, context, request):
        service = self.authoring
        output = service._current_output(state, request['output_id'])
        artifact = ReportSource(**output['artifact'])
        service.assets.read(project_id, artifact)
        if artifact.sha256 != request['output_sha256']:
            raise ReportAuthoringConflict('The report changed after selecting batch updates. Reload its working copy.')
        if not any(request.get(key) for key in ('mapping_ids', 'results', 'assignments', 'llcr_dataset_id', 'photo_plan_id', 'renumber_figures')):
            raise ValueError('Choose at least one confirmed fact, result or photo replacement.')
        dataset = service.sections.selected_llcr_dataset(project_id, request['llcr_dataset_id'], context['matrix_id']) if request.get('llcr_dataset_id') else None
        facts = service.preview_facts(project_id, {'expected_revision': state.revision,
            'output_id': output['output_id'], 'mapping_ids': request.get('mapping_ids', [])})
        replacements = [{key: item[key] for key in ('old', 'new', 'target') if key in item} for item in facts['changes']]
        path = service.assets.path(project_id, artifact)
        numbering = service.document_review.inspector.numbering(path) if request.get('renumber_figures') else None
        if numbering:
            if not numbering['ready']:
                raise ValueError('Figure numbering needs review: ' + '; '.join(item['message'] for item in numbering['issues']))
        results, seen = [], set()
        for selection in request.get('results', []):
            key = selection['result_id']
            if key in seen:
                raise ValueError('Choose each result once in a batch.')
            seen.add(key)
            result = service._confirmed_result(state, context, key)
            if any(selection.get(name) is not None for name in ('evidence_start', 'evidence_end')) and not selection.get('evidence_selection_confirmed'):
                raise ValueError('Review and confirm the old evidence region before replacing it in a batch.')
            target = {name: value for name, value in selection.items()
                      if name not in {'result_id', 'evidence_selection_confirmed'} and value is not None}
            # A wholly automatic target has no positional arguments. Other choices
            # remain explicit and are validated together by the Word adapter.
            if not target.get('appendix_title') and not any(name in target for name in ('result_table', 'result_row', 'appendix_table', 'evidence_start', 'evidence_end')):
                target = None
            results.append({'result': result, 'target': target})
        photos, photo_sources = [], []
        assignments = request.get('assignments', [])
        if request.get('photo_plan_id'):
            if assignments:
                raise ValueError('Use the confirmed photo plan or individual replacements, not both.')
            assignments = service.photo_plan.assignments(state, context, output, request['photo_plan_id'])
        for assignment in assignments:
            source = service._source(state, assignment['source_id'])
            if source.role != 'photo':
                raise ValueError('Choose a retained photo source for each report slot.')
            photos.append({name: value for name, value in assignment.items() if name != 'source_id'} |
                          {'content': service.assets.read(project_id, source)})
            photo_sources.append({'source_id': source.source_id, 'sha256': source.sha256})
        llcr = {'llcr_dataset': dataset} if dataset is not None else {}
        document_plan = self.writer.preview(path, fact_replacements=replacements, results=results, photos=photos,
            **({'figure_numbering': numbering} if numbering else {}), **llcr)
        input_facts = {'matrix': context, 'facts': facts, 'results': [item['result'] for item in results],
                       'photos': photo_sources, 'document_plan': document_plan, 'numbering': numbering,
                       'llcr_dataset_sha256': dataset_sha256(dataset) if dataset else None}
        return output, path, facts, replacements, results, photos, document_plan, dataset, digest(input_facts)

    def preview(self, project_id, request):
        service = self.authoring
        state, context = service._editable(project_id, request['expected_revision'])
        selected = {key: value for key, value in request.items() if key != 'expected_revision'}
        output, _, facts, _, results, _, document_plan, dataset, fingerprint = self._inputs(project_id, state, context, selected)
        coverage = service.coverage(project_id)
        selected_ids = {item['result']['result_id'] for item in results}
        if dataset:
            selected_ids.update(item['result_id'] for item in coverage_results(dataset))
        omitted = [f"Group {row['group_label']} / Step {row['step_token']}: {', '.join(row['reasons']) or 'not included in this batch'}"
                   for row in coverage['rows'] if not selected_ids.intersection(row['usable_result_ids'])]
        issues = [item['message'] for item in document_plan['conflicts']]
        issues += [f"{item['result']['target']['group_label']} / {item['result']['target']['step_token']}: engineering acceptance is pending."
                   for item in results if item['result']['outcome'] == 'pending']
        if dataset:
            issues += [f"{item.group_label} / {item.matrix_step_token}: LLCR engineering acceptance is pending."
                       for item in dataset.payload.entries if item.confirmed_outcome == 'not_determined']
        used_sources = {item['result']['source_id'] for item in results}
        used_sources.update(item['source_id'] for item in facts['mapping_snapshots'])
        used_sources.update(item['source_id'] for item in selected.get('assignments', []))
        if selected.get('photo_plan_id'):
            used_sources.update(item['source_id'] for item in output['photo_plan']['assignments'])
        plan = {'plan_id': uuid4().hex, 'status': 'prepared', 'prepared_revision': state.revision + 1,
                'base_output_id': output['output_id'], 'output_sha256': output['artifact']['sha256'],
                'matrix_id': context['matrix_id'], 'request': selected,
                'can_apply': document_plan['ready'], 'changes': document_plan['changes'],
                'issues': issues, 'omitted': omitted, 'document_plan': document_plan,
                'input_fingerprint': fingerprint, 'mapping_snapshots': facts['mapping_snapshots'],
                'context_snapshot': context,
                'llcr_snapshot': {'dataset_id': dataset.dataset_id, 'sha256': dataset_sha256(dataset)} if dataset else None,
                'source_snapshots': [asdict(item) for item in state.sources if item.source_id in used_sources]}
        plan['preview_sha256'] = digest(plan)
        return service.repository.save(replace(state, assembly_plan=plan), state.revision)

    def apply(self, project_id, request):
        service = self.authoring
        state, context = service.state(project_id)
        # A retry after a lost response must not duplicate a successful business version.
        completed = next((output for output in state.outputs if output.get('evidence', {}).get('plan_id') == request['plan_id']), None)
        if completed and completed['evidence']['preview_sha256'] == request['preview_sha256']:
            service.assets.read(project_id, ReportSource(**completed['artifact']))
            return state
        state, context = service._editable(project_id, request['expected_revision'])
        plan = state.assembly_plan
        if (not plan or plan['plan_id'] != request['plan_id'] or plan['preview_sha256'] != request['preview_sha256']
                or plan['status'] != 'prepared' or not self.is_current(state, context, plan)):
            raise ReportAuthoringConflict('The prepared report batch is stale. Review a new preview.')
        if not plan['can_apply']:
            raise ValueError('Resolve the report target conflicts before applying this batch.')
        output, path, facts, replacements, results, photos, document_plan, dataset, fingerprint = self._inputs(
            project_id, state, context, plan['request'])
        if fingerprint != plan['input_fingerprint']:
            raise ReportAuthoringConflict('Batch inputs or report targets changed after preview.')

        def generate(source, target):
            llcr = {'llcr_dataset': dataset} if dataset is not None else {}
            return self.writer.update(source, target, document_plan, fact_replacements=replacements, results=results, photos=photos,
                **({'figure_numbering': document_plan['figure_numbering']} if document_plan.get('figure_numbering') else {}), **llcr)

        def revalidate():
            current, now = service._editable(project_id, state.revision)
            *_, current_fingerprint = self._inputs(project_id, current, now, plan['request'])
            if current_fingerprint != fingerprint:
                raise ReportAuthoringConflict('Batch inputs changed during report assembly. The previous working copy is retained.')

        generated = service.drafts.update(project_id, context['dl_number'], path, generate, revalidate,
            matrix_id=context['matrix_id'], make_current=False, operation_id=plan['plan_id'],
            operation_sha256=plan['preview_sha256'])
        content = generated.file_path.read_bytes()
        artifact = ReportSource(generated.report_revision_id, 'working_copy', generated.file_name,
                                sha256(content).hexdigest(), len(content), service._now(), context['dl_number'])
        service.assets.retain(project_id, artifact, content)
        record = {'output_id': artifact.source_id, 'artifact': asdict(artifact),
                  'base_source_id': state.base_source_id, 'parent_output_id': output['output_id'],
                  'status': 'needs_review', 'operation': 'batch_assembly',
                  'issues': list(dict.fromkeys([*output['issues'], *plan['issues'], *plan['omitted']])),
                  'evidence': {'plan_id': plan['plan_id'], 'preview_sha256': plan['preview_sha256'],
                      'result_ids': [item['result']['result_id'] for item in results],
                      'llcr_dataset_id': dataset.dataset_id if dataset else None,
                      'llcr_dataset_sha256': dataset_sha256(dataset) if dataset else None,
                      'mapping_snapshots': facts['mapping_snapshots'],
                      'assignments': output['photo_plan']['assignments'] if plan['request'].get('photo_plan_id') else plan['request'].get('assignments', []),
                      'photo_plan': output.get('photo_plan') if plan['request'].get('photo_plan_id') else None,
                      'document_plan': document_plan}}
        record['evidence']['applied_photo_slots'] = service.photos.inspect(service.assets.path(project_id, artifact)) if photos else []
        if service.document_review.inspector:
            record['evidence']['applied_regions'] = [
                {key: region[key] for key in ('region_id', 'sha256', 'owned_result')}
                for region in service.document_review.inspector.inspect(service.assets.path(project_id, artifact))['regions']
                if any((region['owned_result'] or region.get('associated_result', '')) == 'connlab-report-result:' + item['result']['result_id'] for item in results)]
        completed_plan = {**plan, 'status': 'completed', 'can_apply': False, 'applied_output_id': artifact.source_id}
        return service.repository.save(replace(state, outputs=(*state.outputs, record), assembly_plan=completed_plan), state.revision)
