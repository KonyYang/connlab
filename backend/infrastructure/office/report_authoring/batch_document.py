"""Preflight disjoint edits against one original, then produce one isolated Word copy."""
from hashlib import sha256
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from lxml import etree

from backend.infrastructure.office.office_protected_document_gateway import ProtectedWordPackageGateway
from backend.infrastructure.office.test_report_document_gateway import TestReportDocumentGateway, llcr_dataset_sha256
from backend.infrastructure.office.report_authoring.photo_slots import (
    PhotoReplacement, photo_occurrences, preview_photo_replacements, replace_photo_slots,
)
from backend.infrastructure.office.report_authoring.results_document import (
    ReportResultsDocument, measurement_table, result_notes, summary,
)
from backend.infrastructure.office.report_authoring.word_copy import NS, ReportCopyWriter, _paragraph_text, text, replacement_parts, fact_target_matches
from backend.infrastructure.office.report_authoring.pagination import reflow_headings


def _digest(value):
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'),
        allow_nan=False).encode('utf-8')).hexdigest()


def _overlaps(left, right):
    return left is right or left in right.iterancestors() or right in left.iterancestors()


def _conflict(code, message, result_id=None):
    return {'code': code, 'message': message, **({'result_id': result_id} if result_id else {})}


def _next_appendix(used):
    for number in range(1, 703):
        label, remaining = '', number
        while remaining:
            remaining, digit = divmod(remaining - 1, 26)
            label = chr(65 + digit) + label
        if label not in used:
            used.add(label)
            return f'Appendix {label}'
    raise ValueError('No unused appendix identifier is available; choose an explicit target.')


class ReportBatchDocument:
    def __init__(self, protected=None, temperature_chart=None):
        self.protected = protected or ProtectedWordPackageGateway()
        self.facts_writer = ReportCopyWriter(self.protected)
        self.results_writer = ReportResultsDocument(self.protected, temperature_chart)
        self.llcr_writer = TestReportDocumentGateway(protected_package_gateway=self.protected)

    def preview(self, source: Path, *, fact_replacements, results, photos, llcr_dataset=None):
        source = Path(source)
        source_digest = sha256(source.read_bytes()).hexdigest()
        photo_requests = [PhotoReplacement(**photo) for photo in photos]
        photo_facts = [{'slot_id': item.slot_id, 'content_sha256': sha256(item.content).hexdigest(),
            'crop_mode': item.crop_mode, 'accept_slot_transform': item.accept_slot_transform} for item in photo_requests]
        plan = {'source_sha256': source_digest, 'ready': False, 'conflicts': [], 'facts': [],
            'results': [], 'photos': photo_facts, 'changes': [], 'llcr': None,
            'selection_sha256': _digest({'facts': fact_replacements, 'results': results, 'photos': photo_facts,
                'llcr_dataset_sha256': llcr_dataset_sha256(llcr_dataset) if llcr_dataset is not None else None})}
        if not fact_replacements and not results and not photos and llcr_dataset is None:
            plan['conflicts'].append(_conflict('empty_batch', 'Choose at least one confirmed change.'))
        if llcr_dataset is not None:
            try:
                plan['llcr'] = self.llcr_writer.preview_llcr_results(source_path=source, dataset=llcr_dataset)
                plan['changes'].append({'kind': 'llcr', 'dataset_id': llcr_dataset.dataset_id,
                    'label': f"LLCR dataset {llcr_dataset.dataset_id}: {len(plan['llcr']['rows'])} rows; Appendix A {plan['llcr']['appendix']['action']}"})
            except ValueError as error:
                plan['conflicts'].append(_conflict('invalid_llcr_target', str(error)))
        try:
            plan['facts'] = self.facts_writer.preview_facts(source, fact_replacements) if fact_replacements else []
        except ValueError as error:
            plan['conflicts'].append(_conflict('invalid_facts', str(error)))
        with self.protected.readable_copy(source) as readable, ZipFile(readable) as package:
            root = etree.fromstring(package.read('word/document.xml'))
            used_appendices = set(re.findall(r'\bAppendix\s+([A-Z]+)\b', text(root), re.I))
            used_appendices = {label.upper() for label in used_appendices}
            if llcr_dataset is not None:
                used_appendices.add('A')
            for item in results:
                title = (item.get('target') or {}).get('appendix_title', '')
                match = re.match(r'Appendix\s+([A-Z]+|\d+)\b', title.strip(), re.I)
                if match:
                    used_appendices.add(match.group(1).upper())
            prepared = []
            identities = set()
            for item in results:
                result = item['result']
                result_id = result['result_id']
                candidate = self.results_writer.inspect_xml(root, result)
                entry = {'result_id': result_id, 'target': None, 'candidates': candidate, 'locator_sha256': None}
                plan['results'].append(entry)
                if result_id in identities:
                    plan['conflicts'].append(_conflict('duplicate_result', 'Choose each result only once.', result_id))
                    continue
                identities.add(result_id)
                target = dict(item.get('target') or {})
                if 'result_table' not in target or 'result_row' not in target:
                    if len(candidate['result_rows']) != 1:
                        plan['conflicts'].append(_conflict('ambiguous_result_target',
                            'Select the exact report row for this confirmed Group / Step.', result_id))
                        continue
                    row = candidate['result_rows'][0]
                    target.setdefault('result_table', row['table_index'])
                    target.setdefault('result_row', row['row_index'])
                target.setdefault('appendix_table', None)
                target.setdefault('evidence_start', None)
                target.setdefault('evidence_end', None)
                if not target.get('appendix_title') and target['evidence_start'] is None:
                    existing = next((value for value in candidate['appendix_tables']
                        if value['table_index'] == target['appendix_table']), None)
                    target['appendix_title'] = existing['title'] if existing else _next_appendix(used_appendices)
                target.setdefault('appendix_title', '')
                entry['target'] = target
                try:
                    frozen = self.results_writer.prepare_update(root, result, **target)
                except (ValueError, TypeError) as error:
                    plan['conflicts'].append(_conflict('invalid_result_target', str(error), result_id))
                    continue
                entry.update(
                    current_result=text(frozen['cells'][frozen['headers'].index('result')]),
                    current_comment=text(frozen['cells'][frozen['headers'].index('comment')]),
                    new_result=summary(result),
                    new_comment={'pass': 'Pass', 'fail': 'Fail', 'not_applicable': 'N/A', 'pending': ''}[result['outcome']],
                )
                # A previously generated region must be explicitly replaced, never duplicated.
                owned = root.xpath('//w:sdt[w:sdtPr/w:tag/@w:val=$tag]', namespaces=NS,
                    tag='connlab-report-result:' + result_id)
                if any(not any(_overlaps(old, write) for write in frozen['writes']) for old in owned):
                    plan['conflicts'].append(_conflict('existing_result_region',
                        'Select the existing result region or appendix instead of adding another copy.', result_id))
                entry['locator_sha256'] = sha256(b''.join(etree.tostring(node, method='c14n')
                    for node in frozen['writes'])).hexdigest()
                prepared.append(frozen)
                plan['changes'].append({'kind': 'result', 'label':
                    f"{result['kind']}: Group {result['target']['group_label']} / Step {result['target']['step_token']}",
                    'result_id': result_id})
            for label, _ in reflow_headings(root, {item['table'] for item in prepared}):
                plan['changes'].append({'kind': 'pagination', 'label': f'Keep {label} with its table after content reflow (explicit page breaks unchanged).'})
            self._check_overlaps(root, prepared, fact_replacements, photos, plan)
            if plan['llcr'] is not None:
                self._check_llcr_overlaps(root, prepared, fact_replacements, photos, plan)
            if photos:
                try:
                    changed = preview_photo_replacements(readable, photo_requests,
                        expected_source_sha256=sha256(readable.read_bytes()).hexdigest())
                    plan['changes'].extend({'kind': 'photo', 'label': f'Replace {slot}', 'slot_id': slot} for slot in changed)
                except ValueError as error:
                    plan['conflicts'].append(_conflict('invalid_photo', str(error)))
        plan['changes'].extend({'kind': 'facts', 'label': f"{item['old']} → {item['new']} ({item['occurrences']})"}
            for item in plan['facts'])
        if sha256(source.read_bytes()).hexdigest() != source_digest:
            plan['conflicts'].append(_conflict('source_changed', 'Report changed during preview; refresh.'))
        plan['ready'] = not plan['conflicts']
        return plan

    @staticmethod
    def _check_overlaps(root, prepared, fact_replacements, photos, plan):
        existing_appendices = {}
        for paragraph in root.findall('w:body/w:p', NS):
            match = re.match(r'Appendix\s+([A-Z]+|\d+)\b', text(paragraph).strip(), re.I)
            if match:
                existing_appendices.setdefault(match.group(1).upper(), []).append(paragraph)
        claimed_appendices = set()
        for item in prepared:
            if item['region_selected']:
                continue
            match = re.match(r'Appendix\s+([A-Z]+|\d+)\b', item['appendix_title'], re.I)
            if match is None:
                continue  # The existing renderer has already validated the title.
            label = match.group(1).upper()
            own_heading = item['appendix'][1] if item['appendix'] is not None else None
            if label in claimed_appendices or any(heading is not own_heading
                    for heading in existing_appendices.get(label, [])):
                plan['conflicts'].append(_conflict('appendix_identity_conflict',
                    f'Appendix {label} is already assigned to another result; choose an unused identifier.',
                    item['result']['result_id']))
            claimed_appendices.add(label)
        for index, first in enumerate(prepared):
            for second in prepared[index + 1:]:
                if any(_overlaps(left, right) for left in first['writes'] for right in second['writes']):
                    plan['conflicts'].append(_conflict('target_overlap',
                        'Two selected results rewrite the same report region or result cell.', second['result']['result_id']))
        writes = [write for item in prepared for write in item['writes']]
        occurrences = photo_occurrences(root)
        for photo in photos:
            occurrence = occurrences.get(photo['slot_id'])
            if occurrence is not None and any(_overlaps(occurrence, write) for write in writes):
                plan['conflicts'].append(_conflict('target_overlap',
                    f"{photo['slot_id']} is inside a result region being replaced; remove the competing photo assignment."))
        for replacement in fact_replacements:
            old, _, target = replacement_parts(replacement)
            paragraphs = [paragraph for index, paragraph in enumerate(root.xpath('//w:p', namespaces=NS))
                          if fact_target_matches('word/document.xml', index, paragraph, target) and old in _paragraph_text(paragraph)]
            if any(_overlaps(paragraph, write) for paragraph in paragraphs for write in writes):
                plan['conflicts'].append(_conflict('target_overlap',
                    f'Fact replacement "{old}" intersects result content being rebuilt.'))
            for item in prepared:
                result = item['result']
                generated = '\n'.join([summary(result), text(measurement_table(result)),
                    item['appendix_title'], *result_notes(result)])
                if target is None and old in generated:
                    plan['conflicts'].append(_conflict('target_overlap',
                        f'Fact replacement "{old}" would alter the newly generated measurement evidence.', result['result_id']))

    @staticmethod
    def _check_llcr_overlaps(root, prepared, fact_replacements, photos, plan):
        guards = []
        namespaces = {key: value for key, value in root.nsmap.items() if key is not None}
        namespaces.update(NS)
        for region in plan['llcr']['guard_regions']:
            nodes = root.xpath(region['xpath'], namespaces=namespaces)
            if len(nodes) != 1 or sha256(etree.tostring(nodes[0], method='c14n')).hexdigest() != region['sha256']:
                plan['conflicts'].append(_conflict('invalid_llcr_target', 'The LLCR target fingerprint changed during preview.'))
                return
            guards.append((region['role'], nodes[0]))
        for item in prepared:
            if (re.match(r'^Appendix\s+A\b', item['appendix_title'], re.I)
                    or any(_overlaps(write, guard) for write in item['writes']
                           for role, guard in guards if role != 'anchor')):
                plan['conflicts'].append(_conflict('target_overlap',
                    'This result conflicts with an LLCR target, matching field or reserved Appendix A.', item['result']['result_id']))
        occurrences = photo_occurrences(root)
        for photo in photos:
            occurrence = occurrences.get(photo['slot_id'])
            if occurrence is not None and any(_overlaps(occurrence, guard) for role, guard in guards if role != 'anchor'):
                plan['conflicts'].append(_conflict('target_overlap',
                    f"{photo['slot_id']} intersects an LLCR target or Appendix A; choose a separate photo slot."))
        for replacement in fact_replacements:
            old, _, target = replacement_parts(replacement)
            paragraphs = [paragraph for index, paragraph in enumerate(root.xpath('//w:p', namespaces=NS))
                          if fact_target_matches('word/document.xml', index, paragraph, target) and old in _paragraph_text(paragraph)]
            if any(_overlaps(paragraph, guard) for paragraph in paragraphs for _, guard in guards):
                plan['conflicts'].append(_conflict('target_overlap',
                    f'Fact replacement "{old}" changes an LLCR matching field, result or Appendix A anchor.'))

    def update(self, source: Path, output: Path, plan, *, fact_replacements, results, photos, llcr_dataset=None):
        source, output = Path(source), Path(output)
        if output.exists() or output.resolve() == source.resolve():
            raise ValueError('The output already exists; batch assembly never overwrites a report.')
        if not plan.get('ready'):
            raise ValueError('Resolve the batch target conflicts before creating a report copy.')
        current_plan = self.preview(source, fact_replacements=fact_replacements, results=results, photos=photos,
            llcr_dataset=llcr_dataset)
        if not current_plan['ready'] or _digest(current_plan) != _digest(plan):
            raise ValueError('The report, selections or target preview changed; refresh the batch preview.')
        with TemporaryDirectory(prefix='connlab-batch-') as directory:
            directory = Path(directory)
            current = directory / 'source.docx'
            protection = self.protected.stage_editable_copy(source, current)
            # Text updates do not change paragraph/table identity. Apply their frozen
            # locators before result appendices can add or remove paragraphs.
            if fact_replacements:
                updated = directory / 'facts.docx'
                self.facts_writer.apply_facts(current, updated, fact_replacements)
                current = updated
            if photos:
                photographed = directory / 'photos.docx'
                replace_photo_slots(current, photographed, [PhotoReplacement(**item) for item in photos],
                    expected_source_sha256=sha256(current.read_bytes()).hexdigest())
                current = photographed
            pagination_groups = []
            if results:
                updated = directory / 'results.docx'
                updates = [{'result': item['result'], 'target': resolved['target']}
                    for item, resolved in zip(results, current_plan['results'], strict=True)]
                evidence = self.results_writer.update_many(current, updated, updates)
                pagination_groups = evidence['pagination_groups']
                current = updated
            if llcr_dataset is not None:
                updated = directory / 'llcr.docx'
                self.llcr_writer.synchronize_llcr_results(source_path=current, output_path=updated, dataset=llcr_dataset)
                current = updated
            self.protected.restore_password_protection(current, protection)
            if sha256(source.read_bytes()).hexdigest() != plan['source_sha256']:
                raise ValueError('Report changed while assembling; refresh the batch preview.')
            with output.open('xb') as destination:
                destination.write(current.read_bytes())
        return {'changes': current_plan['changes'], 'pagination_groups': pagination_groups,
            'source_sha256': plan['source_sha256'], 'output_sha256': sha256(output.read_bytes()).hexdigest()}
