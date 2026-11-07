"""Version-bound photograph proposals and one explicit project-specific decision."""
from collections import Counter
from dataclasses import asdict, replace
import re
from uuid import uuid4

from backend.application.report_authoring.assembly import digest
from backend.domain.report_authoring import ReportAuthoringConflict, ReportSource


def slot_digest(slot):
    return digest({key: value for key, value in slot.items() if key != 'coverage'}) if slot else None


def photo_candidates(state, slots):
    candidates = []
    for source in state.sources:
        if source.role != 'photo':
            continue
        family = (source.role, source.file_name.casefold(), source.source_locator)
        if next(item for item in reversed(state.sources) if (item.role, item.file_name.casefold(), item.source_locator) == family).source_id != source.source_id:
            continue
        tokens = set(re.findall(r'[a-z0-9]+', source.file_name.casefold())) - {'jpg', 'jpeg', 'png', 'group', 'photo'}
        scores = []
        for slot in slots:
            words = set(re.findall(r'[a-z0-9]+', slot['caption'].casefold()))
            common = sorted(tokens & words)
            scores.append({'slot_id': slot['slot_id'], 'score': len(common), 'hints': common})
        candidates.append({'source_id': source.source_id, 'source_sha256': source.sha256,
            'file_name': source.file_name, 'source_locator': source.source_locator,
            'suggestions': sorted(scores, key=lambda item: -item['score'])[:5],
            'warning': 'Filename/location are suggestions only. Confirm specimen, stage and target from evidence.'})
    return candidates


class ReportPhotoPlan:
    def __init__(self, authoring):
        self.authoring = authoring

    def confirm(self, project_id, request):
        service = self.authoring
        state, context, output, review = service.document_review.current(project_id, request)
        if review['review_sha256'] != request['review_sha256']:
            raise ReportAuthoringConflict('The report or retained evidence changed; inspect the photo proposals again.')
        slots = {item['slot_id']: item for item in review['slots']}
        sources = {item['source_id']: service._source(state, item['source_id']) for item in request['assignments']}
        duplicates = Counter(sources[item['source_id']].sha256 for item in request['assignments'])
        seen, assignments, snapshots = set(), [], []
        valid_steps = {(step['group_id'], step['row_id'], step['step_token']) for step in context['steps']}
        for item in request['assignments']:
            slot = slots.get(item['slot_id'])
            if not slot or not slot['supported'] or item['slot_id'] in seen:
                raise ValueError('Choose each supported photo slot once.')
            seen.add(item['slot_id'])
            scope = item.get('scope', 'step')
            if scope == 'step' and (item['group_id'], item['row_id'], item['step_token']) not in valid_steps:
                raise ValueError('Choose a current confirmed Matrix Group and Step for each photo.')
            if (scope != 'project_context' and not item['sample_ids']) or any(not value.strip() for value in item['sample_ids']) or not item['stage'].strip() or not item['reason'].strip():
                raise ValueError('Each photo needs specimen IDs, before/after stage and the supporting reason.')
            if scope != 'step' and any(item[key] for key in ('group_id', 'row_id', 'step_token')):
                raise ValueError('Overview photos must not carry a fictional Matrix step.')
            if duplicates[sources[item['source_id']].sha256] > 1 and not item['reuse_reason'].strip():
                raise ValueError('Explain each intentional reuse of the same photograph.')
            source = sources[item['source_id']]
            latest = next(entry for entry in reversed(state.sources) if service._source_family(entry) == service._source_family(source))
            if latest.source_id != source.source_id:
                raise ReportAuthoringConflict('Choose the latest retained version of the replacement photograph.')
            if scope == 'step':
                step = next(step for step in context['steps'] if (step['group_id'], step['row_id'], step['step_token']) == (item['group_id'], item['row_id'], item['step_token']))
                caption_group = re.search(r'\bGroup\s+#?([a-z0-9]+)\b', slot['caption'], re.I)
                if caption_group and caption_group.group(1).casefold() != step['group_label'].casefold() and not item.get('accept_context_change'):
                    raise ValueError('The old slot caption names another Group. Review the intended context change and explicitly acknowledge it; the caption is not automatically rewritten.')
            if source.role != 'photo':
                raise ValueError('Choose a retained photograph, not a report or measurement file.')
            service.assets.read(project_id, source)
            assignments.append({**item, 'source_sha256': source.sha256, 'slot_sha256': slot_digest(slot)})
            snapshots.append(asdict(source))
        if not assignments:
            raise ValueError('Choose at least one photo mapping to confirm.')
        plan = {'plan_id': uuid4().hex, 'output_sha256': output['artifact']['sha256'],
            'matrix_id': context['matrix_id'], 'assignments': assignments, 'source_snapshots': snapshots,
            'confirmed_by': request['confirmed_by'], 'confirmed_at': service._now()}
        return service.repository.save(replace(state, outputs=tuple(
            {**entry, 'photo_plan': plan} if entry['output_id'] == output['output_id'] else entry
            for entry in state.outputs)), state.revision)

    def assignments(self, state, context, output, plan_id):
        service = self.authoring
        plan = output.get('photo_plan')
        if not plan or plan['plan_id'] != plan_id or plan['output_sha256'] != output['artifact']['sha256'] or plan['matrix_id'] != context['matrix_id']:
            raise ReportAuthoringConflict('The confirmed photo mapping no longer matches this report and Matrix.')
        slots = {item['slot_id']: item for item in service.photos.inspect(service.assets.path(state.project_id, ReportSource(**output['artifact'])))}
        for item in plan['assignments']:
            source = service._source(state, item['source_id'])
            latest = next(entry for entry in reversed(state.sources) if (entry.role, entry.file_name.casefold(), entry.source_locator) == (source.role, source.file_name.casefold(), source.source_locator))
            if latest.source_id != source.source_id or source.sha256 != item['source_sha256'] or slot_digest(slots.get(item['slot_id'])) != item['slot_sha256']:
                raise ReportAuthoringConflict('A photo source or target changed; review only the affected photo mapping again.')
            service.assets.read(state.project_id, source)
        return [{key: item[key] for key in ('slot_id', 'source_id', 'crop_mode', 'accept_slot_transform')}
                for item in plan['assignments']]
