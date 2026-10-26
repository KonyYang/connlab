"""Prepare project-specific report evidence and decisions, without publishing reports."""
from dataclasses import replace, asdict
from datetime import datetime, timezone
from hashlib import sha256
from uuid import uuid4
import json
from backend.domain.report_authoring import (
    ReportAuthoringState, ReportSource, ReportMapping, ReportAuthoringConflict,
    SOURCE_ROLES, validate_mapping,
)


class ReportAuthoringService:
    def __init__(self, *, repository, assets, inspect_upload, project_context, drafts=None, writer=None, results=None, result_writer=None, photos=None, customer=None):
        self.repository = repository
        self.assets = assets
        self.inspect_upload = inspect_upload
        self.project_context = project_context
        self.drafts = drafts
        self.writer = writer
        self.results = results
        self.result_writer = result_writer
        self.photos = photos
        self.customer = customer

    def state(self, project_id):
        context = self.project_context(project_id)
        state = self.repository.get(project_id)
        # A Matrix change never silently re-confirms a previously mapped result.
        mappings = tuple(replace(item, status="pending") if item.matrix_id and item.matrix_id != context["matrix_id"] else item
                         for item in state.mappings)
        current = replace(state, mappings=mappings)
        fingerprint = self._review_context_sha256(current, context)
        outputs = []
        for output in current.customer_outputs:
            recorded = output.get('recorded_audit') or output.get('audit')
            if recorded and recorded.get('review_context_sha256') != fingerprint:
                issue = {'code': 'review_context_changed', 'location': 'review', 'message':
                    'The Matrix, report copy, source version or report decisions changed after this check. Review the current evidence and check again.', 'sha256': None}
                outputs.append({**output, 'status': 'needs_review', 'recorded_audit': recorded,
                    'audit': {**recorded, 'passed': False, 'issues': [*recorded['issues'], issue]}})
            else:
                outputs.append(output)
        return replace(current, customer_outputs=tuple(outputs)), context

    def _editable(self, project_id, expected_revision):
        state, context = self.state(project_id)
        if state.revision != expected_revision:
            raise ReportAuthoringConflict("Report sources changed. Reload before saving.")
        return state, context

    def add_source(self, project_id, *, role, file_name, content, expected_revision):
        state, context = self._editable(project_id, expected_revision)
        if role not in SOURCE_ROLES:
            raise ValueError("Choose a supported report source role.")
        report_dl = self.inspect_upload(file_name, content, role, context["dl_number"])
        digest = sha256(content).hexdigest()
        if any(item.sha256 == digest and item.role == role for item in state.sources):
            return state
        source = ReportSource(uuid4().hex, role, file_name, digest, len(content), self._now(), report_dl)
        self.assets.retain(project_id, source, content)
        previous = {item.source_id for item in state.sources if item.file_name.casefold() == file_name.casefold() and item.role == role}
        mappings = tuple(replace(item, status="pending", confirmed_by="", confirmed_at="")
                         if item.source_id in previous else item for item in state.mappings)
        return self.repository.save(replace(state, sources=(*state.sources, source), mappings=mappings), expected_revision)

    def save_mapping(self, project_id, *, expected_revision, mapping_id="", **values):
        state, context = self._editable(project_id, expected_revision)
        source = self._source(state, values["source_id"])
        self.assets.read(project_id, source)
        existing = next((item for item in state.mappings if item.mapping_id == mapping_id), None)
        if mapping_id and existing is None:
            raise LookupError("Report mapping not found in this project.")
        status = values.get("status", "pending")
        author = values.pop("confirmed_by", "Lab User").strip()
        if status == "confirmed" and not author:
            raise ValueError("A confirmed decision needs the confirming operator's name.")
        mapping = ReportMapping(mapping_id or uuid4().hex, **values,
            matrix_id=context["matrix_id"] if values.get("group_id") else "",
            confirmed_by=author if status == "confirmed" else "", confirmed_at=self._now() if status == "confirmed" else "")
        validate_mapping(mapping)
        if mapping.group_id or mapping.row_id or mapping.step_token:
            if not any(option["group_id"] == mapping.group_id and option["row_id"] == mapping.row_id and
                       option["step_token"] == mapping.step_token for option in context["steps"]):
                raise ValueError("Choose a Group and Step from the current confirmed Matrix.")
        mappings = tuple(item for item in state.mappings if item.mapping_id != mapping.mapping_id) + (mapping,)
        return self.repository.save(replace(state, mappings=mappings), expected_revision)

    def source_content(self, project_id, source_id):
        state, _ = self.state(project_id)
        source = self._source(state, source_id)
        return source, self.assets.read(project_id, source)

    def select_base(self, project_id, source_id, expected_revision):
        state, context = self._editable(project_id, expected_revision)
        source = self._source(state, source_id)
        if source.role not in {"original", "layout_reference"}:
            raise ValueError("Select an Internal Report original or an approved layout reference.")
        if not context["dl_number"]:
            raise ValueError("Confirm this project's DL number before preparing a report copy.")
        self.assets.read(project_id, source)
        if state.base_source_id == source_id and state.outputs:
            self.assets.read(project_id, ReportSource(**state.outputs[-1]['artifact']))
            return state
        issues = []
        def generate(input_path, output_path):
            issues.extend(self.writer.prepare(input_path, output_path, source_dl=source.report_dl,
                project_dl=context["dl_number"], reference=source.role == "layout_reference") or [])
        def revalidate():
            self.assets.read(project_id, source)
            current, now = self._editable(project_id, expected_revision)
            if now != context:
                raise ReportAuthoringConflict("Project authority changed while preparing the report copy.")
        result = self.drafts.update(project_id, context["dl_number"], self.assets.path(project_id, source),
            generate, revalidate, matrix_id=context["matrix_id"], make_current=False)
        content = result.file_path.read_bytes()
        artifact = ReportSource(result.report_revision_id, "working_copy", result.file_name,
            sha256(content).hexdigest(), len(content), self._now(), context["dl_number"])
        self.assets.retain(project_id, artifact, content)
        output = {"output_id": artifact.source_id, "artifact": asdict(artifact), "base_source_id": source_id,
            "status": "needs_review", "issues": issues, "operation": "prepare_base"}
        return self.repository.save(replace(state, base_source_id=source_id, outputs=(*state.outputs, output)), expected_revision)

    def output_content(self, project_id, output_id):
        state, _ = self.state(project_id)
        output = next((item for item in (*state.outputs, *state.customer_outputs) if item["output_id"] == output_id), None)
        if output is None:
            raise LookupError("Report copy not found in this project.")
        artifact = ReportSource(**output["artifact"])
        return artifact, self.assets.read(project_id, artifact)

    def source_table(self, project_id, source_id, sheet_name=None):
        source, content = self.source_content(project_id, source_id)
        return self.results.table(content, source.file_name, sheet_name)

    def preview_result(self, project_id, request):
        state, context = self._editable(project_id, request["expected_revision"])
        source = self._source(state, request["source_id"])
        if source.role != request["kind"]:
            raise ValueError("Choose a source retained with the matching measurement role.")
        target = next((step for step in context["steps"] if all(step[key] == request[key] for key in ("group_id", "row_id", "step_token"))), None)
        if target is None:
            raise ValueError("Choose the result's Group and Step from the current confirmed Matrix.")
        if request["outcome"] != "pending" and not request["acceptance_reason"].strip():
            raise ValueError("Record this project's acceptance evidence before confirming an outcome.")
        data = self.results.preview(self.assets.read(project_id, source), source.file_name, request)
        profile = {key: value for key, value in request.items() if key != "preview_sha256"}
        result = {"kind": request["kind"], "source_id": source.source_id, "source_sha256": source.sha256,
            "matrix_id": context["matrix_id"], "target": target, "profile": profile, "data": data,
            "outcome": request["outcome"], "acceptance_reason": request["acceptance_reason"]}
        result["preview_sha256"] = sha256(json.dumps(result, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()
        return result

    def confirm_result(self, project_id, request):
        preview = self.preview_result(project_id, request)
        if preview["preview_sha256"] != request.get("preview_sha256"):
            raise ReportAuthoringConflict("The reviewed result inputs changed. Preview and confirm again.")
        state, _ = self._editable(project_id, request["expected_revision"])
        result = {**preview, "result_id": uuid4().hex, "confirmed_at": self._now(), "confirmed_by": request["confirmed_by"]}
        return self.repository.save(replace(state, results=(*state.results, result)), request["expected_revision"])

    def preview_facts(self, project_id, request):
        state, _ = self._editable(project_id, request["expected_revision"])
        output = self._current_output(state, request["output_id"])
        artifact = ReportSource(**output["artifact"])
        self.assets.read(project_id, artifact)
        replacements = []
        mappings = []
        applied = {}
        for previous in reversed(state.outputs):
            if previous['operation'] == 'prepare_base':
                break
            for snapshot in previous.get('evidence', {}).get('mapping_snapshots', []):
                applied.setdefault(snapshot['mapping_id'], snapshot)
        for mapping_id in request["mapping_ids"]:
            mapping = next((item for item in state.mappings if item.mapping_id == mapping_id), None)
            if mapping is None or mapping.status != "confirmed" or mapping.kind not in {"identity", "specification"} or not mapping.report_text.strip():
                raise ValueError("Select confirmed project/specification mappings with the exact old report text.")
            self.assets.read(project_id, self._source(state, mapping.source_id))
            snapshot = applied.get(mapping_id)
            if snapshot and all(snapshot.get(key) == getattr(mapping, key) for key in ('source_id', 'report_text', 'value')):
                continue
            replacements.append((mapping.report_text, mapping.value))
            mappings.append(asdict(mapping))
        if not replacements:
            return {'output_sha256': artifact.sha256, 'changes': [], 'mapping_ids': [], 'mapping_snapshots': [],
                'preview_sha256': sha256((artifact.sha256 + ':no_changes').encode()).hexdigest()}
        if len({item[0] for item in replacements}) != len(replacements) or any(a[0] in b[0] or b[0] in a[0] for index, a in enumerate(replacements) for b in replacements[index+1:]):
            raise ValueError("Each old report text must have one replacement, not overlapping decisions.")
        changes = self.writer.preview_facts(self.assets.path(project_id, artifact), replacements)
        result = {"output_sha256": artifact.sha256, "changes": changes, "mapping_ids": [item['mapping_id'] for item in mappings],
                  'mapping_snapshots': mappings}
        result["preview_sha256"] = sha256(json.dumps(result, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        return result

    def apply_facts(self, project_id, request):
        preview = self.preview_facts(project_id, request)
        if request.get("preview_sha256") != preview["preview_sha256"]:
            raise ReportAuthoringConflict("Report text or confirmed facts changed. Review the replacement preview again.")
        state, context = self._editable(project_id, request["expected_revision"])
        output = self._current_output(state, request["output_id"])
        if not preview['changes']:
            return state
        replacements = [(item["old"], item["new"]) for item in preview["changes"]]
        return self._updated_copy(state, context, output, "confirmed_facts", request["expected_revision"],
            lambda source, target: self.writer.apply_facts(source, target, replacements),
            lambda: self.preview_facts(project_id, request), {"mapping_ids": preview['mapping_ids'], 'mapping_snapshots': preview['mapping_snapshots']})

    def result_targets(self, project_id, output_id, result_id, expected_revision):
        state, context = self._editable(project_id, expected_revision)
        output = self._current_output(state, output_id)
        result = self._confirmed_result(state, context, result_id)
        artifact = ReportSource(**output["artifact"])
        self.assets.read(project_id, artifact)
        return {**self.result_writer.inspect(self.assets.path(project_id, artifact), result),
                "output_sha256": artifact.sha256, "result_id": result_id}

    def apply_result(self, project_id, request):
        state, context = self._editable(project_id, request["expected_revision"])
        output = self._current_output(state, request["output_id"])
        result = self._confirmed_result(state, context, request["result_id"])
        if output['artifact']['sha256'] != request['output_sha256']:
            raise ReportAuthoringConflict('The report changed after selecting its result and appendix locations.')
        if (request.get('evidence_start') is not None or request.get('evidence_end') is not None) and not request.get('evidence_selection_confirmed'):
            raise ValueError('Review and explicitly confirm the selected old evidence blocks before replacement.')
        evidence = {key: request.get(key) for key in ('result_id', 'result_table', 'result_row', 'appendix_table', 'appendix_title', 'evidence_start', 'evidence_end')}
        if output['operation'] == 'result_update' and all(output.get('evidence', {}).get(key) == value for key, value in evidence.items()):
            return state
        def revalidate():
            current, current_context = self._editable(project_id, request['expected_revision'])
            if current_context != context:
                raise ReportAuthoringConflict('The project Matrix changed during the update.')
            self._confirmed_result(current, current_context, request['result_id'])
        return self._updated_copy(state, context, output, 'result_update', request['expected_revision'],
            lambda source, target: self.result_writer.update(source, target, result,
                result_table=request['result_table'], result_row=request['result_row'],
                appendix_table=request['appendix_table'], appendix_title=request['appendix_title'],
                evidence_start=request.get('evidence_start'), evidence_end=request.get('evidence_end')),
            revalidate, evidence)

    def _confirmed_result(self, state, context, result_id):
        result = next((item for item in state.results if item['result_id'] == result_id), None)
        if result is None:
            raise LookupError('Confirmed result not found in this project.')
        if result['matrix_id'] != context['matrix_id']:
            raise ReportAuthoringConflict('The result refers to an older Matrix. Review its Group and Step again.')
        source = self._source(state, result['source_id'])
        latest = next(item for item in reversed(state.sources) if item.role == source.role and item.file_name.casefold() == source.file_name.casefold())
        if latest.source_id != source.source_id:
            raise ReportAuthoringConflict('A newer source file was uploaded. Review and import its measurements again.')
        self.assets.read(state.project_id, source)
        return result

    def photo_slots(self, project_id, output_id, expected_revision):
        state, _ = self._editable(project_id, expected_revision)
        output = self._current_output(state, output_id)
        artifact = ReportSource(**output['artifact'])
        self.assets.read(project_id, artifact)
        return {'output_sha256': artifact.sha256, 'slots': self.photos.inspect(self.assets.path(project_id, artifact))}

    def photo_content(self, project_id, output_id, slot_id):
        state, _ = self.state(project_id)
        output = self._current_output(state, output_id)
        artifact = ReportSource(**output['artifact'])
        self.assets.read(project_id, artifact)
        return self.photos.read(self.assets.path(project_id, artifact), slot_id)

    def apply_photos(self, project_id, request):
        state, context = self._editable(project_id, request['expected_revision'])
        output = self._current_output(state, request['output_id'])
        if output['artifact']['sha256'] != request['output_sha256']:
            raise ReportAuthoringConflict('The report changed after selecting photo slots. Reload the slot preview.')
        replacements, evidence, selected = [], [], set()
        for assignment in request['assignments']:
            if assignment['slot_id'] in selected:
                raise ValueError('Assign each photo slot once.')
            selected.add(assignment['slot_id'])
            source = self._source(state, assignment['source_id'])
            if source.role != 'photo':
                raise ValueError('Choose a retained photo source for each slot.')
            replacements.append({'slot_id': assignment['slot_id'], 'content': self.assets.read(project_id, source),
                'crop_mode': assignment['crop_mode'], 'accept_slot_transform': assignment['accept_slot_transform']})
            evidence.append({**assignment, 'source_sha256': source.sha256})
        def revalidate():
            current, now = self._editable(project_id, request['expected_revision'])
            if now != context:
                raise ReportAuthoringConflict('Project authority changed during photo replacement.')
            for assignment in request['assignments']:
                self.assets.read(project_id, self._source(current, assignment['source_id']))
        return self._updated_copy(state, context, output, 'photo_replacement', request['expected_revision'],
            lambda source, target: self.photos.update(source, target, replacements), revalidate, {'assignments': evidence})

    def generate_customer(self, project_id, request):
        state, context = self._editable(project_id, request['expected_revision'])
        output = self._current_output(state, request['output_id'])
        artifact = ReportSource(**output['artifact'])
        if artifact.sha256 != request['output_sha256']:
            raise ReportAuthoringConflict('The reviewed Internal Report copy changed. Reload before customer conversion.')
        self.assets.read(project_id, artifact)
        temperatures = [self._confirmed_result(state, context, key) for key in request['temperature_result_ids']]
        if any(item['kind'] != 'temperature' for item in temperatures):
            raise ValueError('Choose temperature results for the complete customer measurement supplement.')
        applied = set(self.active_result_ids(state))
        if any(result['result_id'] not in applied for result in temperatures):
            raise ValueError('Apply each selected temperature result to the current Internal Report copy first.')
        if any(result['kind'] == 'temperature' and result['result_id'] in applied and result['result_id'] not in request['temperature_result_ids'] for result in state.results):
            raise ValueError('Include all temperature results applied to this Internal Report; a customer copy must not omit their measurement tables or curves.')
        for result in temperatures:
            if self.result_writer.inspect(self.assets.path(project_id, artifact), result)['unreconciled_temperature_evidence']:
                raise ValueError('Old temperature evidence remains in the result Group. Explicitly replace its complete table, curve and conclusion before customer conversion.')
        def revalidate():
            current, now = self._editable(project_id, request['expected_revision'])
            if now != context:
                raise ReportAuthoringConflict('Project authority changed during customer conversion.')
            self.assets.read(project_id, artifact)
            for result in temperatures:
                self._confirmed_result(current, now, result['result_id'])
        generated = self.drafts.update(project_id, context['dl_number'], self.assets.path(project_id, artifact),
            lambda source, target: self.customer.generate(source, target, temperatures), revalidate,
            matrix_id=context['matrix_id'], make_current=False)
        content = generated.file_path.read_bytes()
        customer = ReportSource(uuid4().hex, 'customer_copy', f"{context['dl_number']}-CR-review.docx",
            sha256(content).hexdigest(), len(content), self._now(), context['dl_number'])
        self.assets.retain(project_id, customer, content)
        record = {'output_id': customer.source_id, 'artifact': asdict(customer), 'base_source_id': state.base_source_id,
            'parent_output_id': output['output_id'], 'operation': 'customer_projection', 'status': 'needs_review',
            'issues': ['Customer review copy only. Not formally released.'], 'temperature_result_ids': request['temperature_result_ids']}
        return self.repository.save(replace(state, customer_outputs=(*state.customer_outputs, record)), request['expected_revision'])

    def customer_check(self, project_id, request):
        state, context = self._editable(project_id, request['expected_revision'])
        output = next((item for item in state.customer_outputs if item['output_id'] == request['output_id']), None)
        if output is None:
            raise LookupError('Customer review copy not found.')
        artifact = ReportSource(**output['artifact'])
        if artifact.sha256 != request['output_sha256']:
            raise ReportAuthoringConflict('Customer copy bytes changed. Inspect the current copy again.')
        self.assets.read(project_id, artifact)
        base = self._source(state, output['base_source_id'])
        forbidden = [base.report_dl] if base.report_dl and base.report_dl != context['dl_number'] else []
        forbidden += request['forbidden_project_ids']
        audit = self.customer.audit(self.assets.path(project_id, artifact), sensitive_terms=request['sensitive_terms'],
            forbidden_project_ids=forbidden, reviewed_parts=request['reviewed_parts'], expected_project_dl=context['dl_number'])
        issues = list(audit['issues'])
        if not request['disclosure_scope_confirmed']:
            issues.append({'code': 'disclosure_scope_unconfirmed', 'location': 'review', 'message':
                'Confirm the sensitive material/disclosure terms and check unclassified material before accepting the package check.', 'sha256': None})
        current = state.outputs[-1] if state.outputs else None
        if current is None or current['output_id'] != output['parent_output_id']:
            issues.append({'code': 'stale_customer_copy', 'location': 'review', 'message': 'A newer Internal Report copy exists. Regenerate the customer review copy.', 'sha256': None})
        if any(mapping.status == 'pending' for mapping in state.mappings):
            issues.append({'code': 'pending_decisions', 'location': 'review', 'message': 'Report source/mapping decisions remain pending or were invalidated. Resolve them before delivery.', 'sha256': None})
        if not current or request.get('content_review_sha256') != current['artifact']['sha256']:
            issues.append({'code': 'content_review_required', 'location': 'review', 'message': 'Review the exact Internal Report facts, specification, conclusions, photos and completeness; prior-project statements are not current evidence.', 'sha256': None})
        for key in self.active_result_ids(state):
            try:
                result = self._confirmed_result(state, context, key)
                if result['outcome'] == 'pending' or (result['kind'] == 'temperature' and not result['data'].get('sample_ids')):
                    issues.append({'code': 'pending_result_decision', 'location': key, 'message': 'Applied result acceptance or sample identities still need confirmation.', 'sha256': None})
                if result['kind'] == 'temperature' and current:
                    internal = ReportSource(**current['artifact'])
                    self.assets.read(project_id, internal)
                    if self.result_writer.inspect(self.assets.path(project_id, internal), result)['unreconciled_temperature_evidence']:
                        issues.append({'code': 'old_temperature_evidence', 'location': key, 'message': 'Old temperature table, curve or conclusion remains in this Group. Replace the explicit evidence region; content-review approval cannot bypass this check.', 'sha256': None})
            except (ValueError, LookupError):
                issues.append({'code': 'stale_result', 'location': key, 'message': 'An applied result no longer matches the retained source or current Matrix.', 'sha256': None})
        audit.update(passed=not issues, issues=issues, output_sha256=artifact.sha256,
            checked_at=self._now(), checked_by=request['reviewed_by'],
            sensitive_terms=request['sensitive_terms'], forbidden_project_ids=forbidden,
            reviewed_parts=request['reviewed_parts'], disclosure_scope_confirmed=request['disclosure_scope_confirmed'])
        audit['content_review_sha256'] = request.get('content_review_sha256')
        audit['review_context_sha256'] = self._review_context_sha256(state, context)
        record = {**output, 'audit': audit, 'status': 'package_checked' if audit['passed'] else 'needs_review'}
        record.pop('recorded_audit', None)
        return self.repository.save(replace(state, customer_outputs=tuple(record if item['output_id'] == output['output_id'] else item for item in state.customer_outputs)), request['expected_revision'])

    def customer_part(self, project_id, output_id, part_name):
        state, _ = self.state(project_id)
        output = next((item for item in state.customer_outputs if item['output_id'] == output_id), None)
        if output is None:
            raise LookupError('Customer review copy not found.')
        artifact = ReportSource(**output['artifact'])
        self.assets.read(project_id, artifact)
        return self.customer.part(self.assets.path(project_id, artifact), part_name)

    @staticmethod
    def active_result_ids(state):
        active, targets = [], set()
        results = {item['result_id']: item for item in state.results}
        for output in reversed(state.outputs):
            if output['operation'] == 'prepare_base':
                break
            if output['operation'] != 'result_update':
                continue
            result_id = output['evidence']['result_id']
            result = results[result_id]
            key = tuple(result['target'][field] for field in ('group_id', 'row_id', 'step_token'))
            if key not in targets:
                active.append(result_id)
                targets.add(key)
        return list(reversed(active))

    @classmethod
    def _review_context_sha256(cls, state, context):
        active_ids = set(cls.active_result_ids(state))
        results = [item for item in state.results if item['result_id'] in active_ids]
        used_sources = {item.source_id for item in state.mappings} | {item['source_id'] for item in results}
        if state.base_source_id:
            used_sources.add(state.base_source_id)
        latest = {}
        for source in state.sources:
            latest[(source.role, source.file_name.casefold())] = source.source_id
        dependencies = [{"source_id": source.source_id, 'latest_source_id': latest[(source.role, source.file_name.casefold())]}
            for source in state.sources if source.source_id in used_sources]
        facts = {'matrix_id': context['matrix_id'], 'base_source_id': state.base_source_id,
            'internal_sha256': state.outputs[-1]['artifact']['sha256'] if state.outputs else None,
            'mappings': [asdict(item) for item in state.mappings], 'result_ids': sorted(active_ids), 'sources': dependencies}
        return sha256(json.dumps(facts, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    def _updated_copy(self, state, context, output, operation, expected_revision, generate, revalidate, evidence):
        artifact = ReportSource(**output["artifact"])
        self.assets.read(state.project_id, artifact)
        changed = [None]
        def generate_copy(source, target):
            changed[0] = generate(source, target)
        def validate_retained_source():
            self.assets.read(state.project_id, artifact)
            current, now = self._editable(state.project_id, expected_revision)
            if now != context:
                raise ReportAuthoringConflict('Project authority changed while updating the report copy.')
            self._current_output(current, output['output_id'])
            revalidate()
        result = self.drafts.update(state.project_id, context["dl_number"], self.assets.path(state.project_id, artifact),
            generate_copy, validate_retained_source, matrix_id=context["matrix_id"], make_current=False)
        content = result.file_path.read_bytes()
        if changed[0] is False or sha256(content).hexdigest() == artifact.sha256:
            return state
        updated = ReportSource(result.report_revision_id, "working_copy", result.file_name,
            sha256(content).hexdigest(), len(content), self._now(), context["dl_number"])
        self.assets.retain(state.project_id, updated, content)
        record = {"output_id": updated.source_id, "artifact": asdict(updated), "base_source_id": state.base_source_id,
            "parent_output_id": output["output_id"], "status": "needs_review", "issues": output["issues"],
            "operation": operation, "evidence": evidence}
        if operation == 'result_update' and isinstance(changed[0], dict) and changed[0].get('pagination_groups'):
            record['evidence'] = {**evidence, **changed[0]}
            record['issues'] = [*output['issues'], 'Pagination protection keeps identified Group headings, result-table headers and first rows together; their pagination properties may change, not their text, font or images.']
        return self.repository.save(replace(state, outputs=(*state.outputs, record)), expected_revision)

    @staticmethod
    def _current_output(state, output_id):
        if not state.outputs or state.outputs[-1]["output_id"] != output_id:
            raise ReportAuthoringConflict("Choose the current working copy; a newer report edit may exist.")
        return state.outputs[-1]

    @staticmethod
    def _source(state, source_id):
        source = next((item for item in state.sources if item.source_id == source_id), None)
        if source is None:
            raise LookupError("Report source not found in this project.")
        return source

    @staticmethod
    def _now():
        return datetime.now(timezone.utc).isoformat()
