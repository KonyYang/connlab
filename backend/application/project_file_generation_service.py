"""Independent file generation in a trusted, already-created project workspace."""

from contextlib import contextmanager, nullcontext
from pathlib import Path
import logging
from hashlib import sha256
import json
from uuid import uuid4
from threading import Lock

from backend.application.project_file_generation_types import FILE_DEFINITIONS, ProjectFileTargetLockedError


logger = logging.getLogger(__name__)
_ACTIONS = {"skip", "generate_missing", "replace_with_backup"}


def fingerprint(value):
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


class ProjectFileGenerationService:
    def __init__(self, *, journal, shared, components, submit, check_other_writes, files):
        self.journal, self.shared = journal, shared
        self.components, self.submit = components, submit
        self.check_other_writes = check_other_writes
        self.files, self.owner = files, uuid4().hex
        self._inflight, self._inflight_lock = {}, Lock()

    @contextmanager
    def _components(self):
        value = self.components()
        with value if hasattr(value, "__enter__") else nullcontext(value) as component:
            yield component

    def _preview(self, project_id, component):
        blockers, workspace, items = [], None, []
        try:
            workspace = component.workspace(project_id)
            self.check_other_writes(project_id)
        except (ValueError, OSError, LookupError) as exc:
            blockers.append(str(exc))
        for key, label, _kind in FILE_DEFINITIONS:
            item = {"key": key, "label": label, "target_path": None, "status": "blocked",
                    "default_action": "skip", "source_token": None, "message": "Create or review the project folder first.", "warnings": []}
            if workspace:
                try:
                    source = component.source(project_id, key)
                    item["target_path"] = self._display_path(source.target, workspace)
                    facts = self.files.facts(source.target)
                    item.update(target_path=self._display_path(source.target, workspace),
                        status="exists" if facts else source.status,
                        default_action="skip" if facts else "generate_missing",
                        source_token=self._review_token(source, facts), message=source.message,
                        warnings=list(source.warnings))
                except (ValueError, OSError, LookupError) as exc:
                    item["message"] = str(exc)
            items.append(item)
        state = self.journal.read(project_id)
        return {"project_id": project_id, "workspace_token": workspace["token"] if workspace else None,
                "status": "blocked" if blockers else "ready", "items": items,
                "blockers": blockers, "warnings": [], "operation": self._view(state) if state else None}

    def preview(self, project_id):
        with self._components() as component:
            return self._preview(project_id, component)

    def start(self, project_id, request):
        request_id = request.get("request_id")
        if not isinstance(request_id, str) or not request_id.strip() or len(request_id) > 100:
            raise ValueError("A bounded request identity is required.")
        choices = request.get("items", [])
        keys = [item.get("key") for item in choices]
        if not choices or len(keys) != len(set(keys)) or not set(keys) <= {key for key, _, _ in FILE_DEFINITIONS}:
            raise ValueError("Choose each supported file at most once.")
        if any(item.get("action") not in _ACTIONS for item in choices):
            raise ValueError("Unsupported file generation action.")
        signature = fingerprint({"workspace_token": request.get("workspace_token"),
                                 "items": sorted(choices, key=lambda item: item["key"])})
        with self.shared.lock(project_id):
            prior = self.journal.find_request(project_id, request_id)
            if prior:
                if prior["request_signature"] != signature:
                    raise ValueError("This request identity was already used for different file choices.")
                return self._response(prior)
            self.check_other_writes(project_id)
            current = self.journal.read(project_id)
            if current and current["status"] != "completed":
                raise ValueError("Resume the unfinished file operation first.")
            with self._components() as component:
                workspace = component.workspace(project_id)
                if workspace["token"] != request.get("workspace_token"):
                    raise ValueError("Project folder identity changed. Refresh the file preview.")
                items = []
                for choice in choices:
                    source = component.source(project_id, choice["key"])
                    facts = None if choice["action"] == "skip" else self.files.facts(source.target)
                    if choice["action"] != "skip" and choice.get("source_token") != self._review_token(source, facts):
                        raise ValueError(f"{source.label} sources or target changed. Refresh the preview.")
                    if choice["action"] == "generate_missing" and facts:
                        raise ValueError("An existing target requires explicit replacement with backup.")
                    if choice["action"] == "replace_with_backup" and not facts:
                        raise ValueError("The reviewed replacement target disappeared. Refresh the preview.")
                    items.append({"key": source.key, "label": source.label, "target": str(source.target) if source.target else None,
                        "output_kind": source.output_kind, "source_token": source.source_token,
                        "review_token": choice.get("source_token"), "prior": facts,
                        "action": choice["action"], "status": "pending", "message": source.message,
                        "warnings": list(source.warnings), "outcome": None, "output_record_id": None})
                targets = [item["target"].casefold() for item in items if item["target"] and item["action"] != "skip"]
                if len(targets) != len(set(targets)):
                    raise ValueError("Two selected files share a publication target. Review their selected sources before generating.")
            state = self.journal.create(project_id, request_id, signature, workspace["token"], items,
                                        workspace=workspace, owner=self.owner)
        self._enqueue(project_id, state["operation_id"])
        return self.read(project_id, state["operation_id"])

    def read(self, project_id, operation_id):
        current = self.journal.read(project_id)
        state = current if current and current["operation_id"] == operation_id else self.journal.read_archived(project_id, operation_id)
        if state is None:
            raise LookupError("File generation operation not found.")
        return self._view(state)

    def resume(self, project_id, operation_id):
        with self.shared.lock(project_id):
            state = self.journal.read(project_id)
            if not state or state["operation_id"] != operation_id:
                raise ValueError("Only the current file operation may be resumed.")
            if state["status"] == "completed":
                return self._response(state)
            self.check_other_writes(project_id)
            state.update(status="queued", message=None, owner=self.owner)
            self.journal.save(state)
        self._enqueue(project_id, operation_id)
        return self.read(project_id, operation_id)

    def run(self, project_id, operation_id):
        try:
            with self.shared.lock(project_id):
                state = self.journal.read(project_id)
                if not state or state["operation_id"] != operation_id or state["status"] == "completed":
                    return
                self.check_other_writes(project_id)
                state["status"] = "running"
                self.journal.save(state)
                try:
                    # Resolve every frozen filesystem/registration effect before any
                    # current document source is consulted after process loss.
                    for item in state["items"]:
                        if item["key"] in state["effects"] and item["status"] != "completed":
                            try:
                                self._recover(state, item)
                            except ProjectFileTargetLockedError as exc:
                                item["message"] = str(exc)
                                self.journal.save(state)
                    for item in state["items"]:
                        if item["status"] in {"completed", "skipped", "failed", "needs_input"}:
                            continue
                        if item["key"] in state["effects"]:
                            continue
                        if item["action"] == "skip":
                            item.update(status="skipped", message="File generation skipped.")
                            self.journal.save(state)
                            continue
                        if item.get("stage"):
                            self._recover_incomplete_stage(state, item)
                            continue
                        self._generate(state, item)
                    pending = any(item["status"] not in {"completed", "skipped", "failed", "needs_input"} for item in state["items"])
                    state.update(status="interrupted" if pending else "completed", outcome=None if pending else
                        "partial" if any(item["status"] in {"failed", "needs_input"} for item in state["items"]) else "complete",
                        message="Some files need recovery; other independent files completed." if pending else None)
                    self.journal.save(state)
                except Exception as exc:
                    logger.exception("Project file generation interrupted project=%s operation=%s", project_id, operation_id)
                    state.update(status="interrupted", message=str(exc))
                    self.journal.save(state)
        except Exception:
            logger.exception("Could not acquire/read file generation operation project=%s operation=%s", project_id, operation_id)

    def _verify_workspace(self, state):
        with self._components() as component:
            workspace = component.workspace(state["project_id"])
        if workspace["token"] != state["workspace_token"]:
            raise ValueError("Project folder identity changed; retain generation files for recovery.")

    def _generate(self, state, item):
        project_id, key = state["project_id"], item["key"]
        self._verify_workspace(state)
        try:
            with self._components() as component:
                source = component.source(project_id, key)
                if source.status != "ready" or not source.source_token:
                    item.update(status="needs_input", message=source.message)
                    self.journal.save(state)
                    return
                if source.source_token != item["source_token"]:
                    raise ValueError("File sources changed. Preview a new operation after this batch completes.")
                if self.files.facts(source.target) != item["prior"]:
                    raise ValueError("The reviewed target changed before generation.")
                item["registration"] = component.registration(project_id, key)
                if item["registration"]["adapter_token"] != source.source_token:
                    raise ValueError("File sources changed while freezing output registration.")
        except (ValueError, LookupError, OSError) as exc:
            item.update(status="failed", message=str(exc))
            self.journal.save(state)
            return
        target = Path(item["target"])
        stage = self.files.prepare_stage(self.journal, state, item)
        try:
            with self._components() as component:
                generated = Path(component.generate(project_id, key, stage, target.name))
        except Exception as exc:
            self.files.verify_stage(item)
            item.update(status="failed", message=str(exc))
            self.journal.save(state)
            return
        item["unverified_generated_path"] = str(generated)
        self.journal.save(state)
        self.files.verify_generated(item, generated)
        item.pop("unverified_generated_path")
        with self._components() as component:
            current_source = component.source(project_id, key)
        if current_source.source_token != item["source_token"]:
            item.update(status="failed", message="File sources changed during generation; staged output retained.")
            self.journal.save(state)
            return
        self._verify_workspace(state)
        try:
            effect = self.files.prepare(self.journal, state, item, generated)
        except (ValueError, OSError) as exc:
            item.update(status="failed", message=str(exc))
            self.journal.save(state)
            return
        state["effects"][key] = effect
        self.journal.save(state)
        try:
            self._recover(state, item)
        except ProjectFileTargetLockedError as exc:
            # A locked individual target must not starve independent files.
            # Its frozen receipt remains pending and continues fencing writers.
            item.update(status="published" if effect["phase"] == "published" else "generating", message=str(exc))
            self.journal.save(state)

    def _recover(self, state, item):
        effect = state["effects"][item["key"]]
        self.files.publish(self.journal, state, effect, lambda: self._verify_workspace(state))
        item["status"] = "published"
        self.journal.save(state)
        with self._components() as component:
            record_id = component.register(state, item, effect)
        item.update(status="completed", output_record_id=record_id,
                    outcome="replaced" if effect["backup"] else "generated", message="File generated and registered.")
        self.journal.save(state)

    def _recover_incomplete_stage(self, state, item):
        if item.get("unverified_generated_path"):
            raise ValueError("An unverified generator output needs manual review; retain all files.")
        self.files.verify_incomplete_stage(item)
        item.update(status="failed", message="Generation was interrupted before publication; retained staging was not regenerated.")
        self.journal.save(state)

    @staticmethod
    def _review_token(source, facts):
        return fingerprint({"source": source.source_token, "target": str(source.target), "existing": facts}) if source.source_token else None

    @staticmethod
    def _display_path(target, workspace):
        if target is None:
            return None
        path = Path(target)
        try:
            return path.relative_to(workspace["official"]).as_posix()
        except ValueError:
            return path.name

    def _response(self, state):
        workspace = state.get("workspace", {})
        items = []
        for item in state["items"]:
            effect = state["effects"].get(item["key"], {})
            backup = effect.get("backup")
            items.append({key: item.get(key) for key in ("key", "label", "status", "action", "message", "warnings", "outcome", "output_record_id")})
            items[-1].update(target_path=self._display_path(item.get("target"), workspace),
                backup_path=Path(backup).relative_to(workspace["local"]).as_posix() if backup else None)
        summary = {name: 0 for name in ("generated", "replaced", "skipped", "needs_input", "failed")}
        for item in items:
            bucket = item.get("outcome") or item["status"]
            if bucket in summary:
                summary[bucket] += 1
        return {"project_id": state["project_id"], "operation_id": state["operation_id"],
                "status": state["status"], "outcome": state["outcome"], "items": items,
                "message": state["message"], "warnings": state.get("warnings", []),
                "can_resume": state["status"] in {"queued", "running", "interrupted"}, "summary": summary}

    def _view(self, state):
        response = self._response(state)
        with self._inflight_lock:
            locally_dispatched = self._inflight.get(state["operation_id"], 0) > 0
        if state["status"] == "running" or (state["status"] == "queued" and
                (state.get("owner") != self.owner or not locally_dispatched)):
            try:
                with self.shared.lock(state["project_id"]):
                    response.update(status="interrupted", can_resume=True,
                        message="Generation was interrupted. Resume to verify retained files.")
            except ValueError:
                pass
        return response

    def _enqueue(self, project_id, operation_id):
        with self._inflight_lock:
            self._inflight[operation_id] = self._inflight.get(operation_id, 0) + 1
        def execute():
            try:
                self.run(project_id, operation_id)
            finally:
                self._release_dispatch(operation_id)
        try:
            self.submit(execute)
        except Exception:
            self._release_dispatch(operation_id)
            logger.exception("File generation dispatch failed project=%s operation=%s", project_id, operation_id)

    def _release_dispatch(self, operation_id):
        with self._inflight_lock:
            count = self._inflight[operation_id] - 1
            if count:
                self._inflight[operation_id] = count
            else:
                self._inflight.pop(operation_id)
