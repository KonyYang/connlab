from pathlib import Path

import pytest

from backend.application.project_file_generation_service import ProjectFileGenerationService
from backend.application.project_file_generation_types import ProjectFileSource, FILE_DEFINITIONS, ProjectFileTargetLockedError
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.files.project_file_generation_journal import ProjectFileGenerationJournal
from backend.infrastructure.files.recoverable_project_file_publisher import ProjectFilePublicationGateway


class Components:
    def __init__(self, root):
        self.root = root
        self.calls = []
        self.records = []
        (root / "official").mkdir()

    def workspace(self, project_id):
        return {"token": "trusted", "official": str(self.root / "official"),
                "local": str(self.root), "stage_parent": str(self.root / "stage")}

    def source(self, project_id, key):
        label, kind = next((label, kind) for value, label, kind in FILE_DEFINITIONS if value == key)
        ready = key != "fee_form"
        return ProjectFileSource(key, label, self.root / "official" / (key + ".xlsx"),
                                 key + "-v1" if ready else None, kind,
                                 "ready" if ready else "blocked", "Ready" if ready else "Confirm Fee")

    def generate(self, project_id, key, stage_dir, target_name):
        self.calls.append(key)
        result = stage_dir / target_name
        result.write_bytes(key.encode())
        return result

    def register(self, state, item, effect):
        self.records.append(item["key"])
        return "record-" + item["key"]

    def registration(self, project_id, key):
        return {"output_kind": key, "adapter_token": self.source(project_id, key).source_token}


def build(tmp_path):
    components = Components(tmp_path)
    journal = ProjectFileGenerationJournal(tmp_path / "journal")
    queue = []
    service = ProjectFileGenerationService(journal=journal,
        shared=GenerationJournal(tmp_path / "shared"), components=lambda: components,
        submit=lambda fn, *args: queue.append((fn, args)), check_other_writes=lambda _: None,
        files=ProjectFilePublicationGateway())
    return service, components, queue


def test_independent_readiness_partial_failure_and_idempotent_replay(tmp_path):
    service, components, queue = build(tmp_path)
    preview = service.preview("p1")
    request = {"request_id": "request-1", "workspace_token": preview["workspace_token"],
               "items": [{"key": item["key"], "source_token": item["source_token"], "action": item["default_action"]}
                         for item in preview["items"]]}
    first = service.start("p1", request)
    assert first["status"] == "queued"
    fn, args = queue.pop()
    fn(*args)
    result = service.read("p1", first["operation_id"])
    assert result["status"] == "completed"
    assert result["outcome"] == "partial"
    assert len(components.calls) == 7
    assert next(item for item in result["items"] if item["key"] == "fee_form")["status"] == "needs_input"
    assert service.start("p1", request)["operation_id"] == first["operation_id"]
    assert queue == []
    assert len(components.records) == 7
    changed = {**request, "items": request["items"][:-1]}
    with pytest.raises(ValueError, match="request"):
        service.start("p1", changed)


def test_existing_targets_default_skip_even_when_source_unavailable(tmp_path):
    service, components, queue = build(tmp_path)
    existing = tmp_path / "official" / "fee_form.xlsx"
    existing.write_bytes(b"manual")
    preview = service.preview("p1")
    item = next(item for item in preview["items"] if item["key"] == "fee_form")
    assert item["default_action"] == "skip"
    service.start("p1", {"request_id": "r", "workspace_token": preview["workspace_token"],
        "items": [{"key": "fee_form", "source_token": None, "action": "skip"}]})
    fn, args = queue.pop()
    fn(*args)
    assert existing.read_bytes() == b"manual"
    assert components.calls == []


def test_published_but_unregistered_recovery_does_not_read_sources_or_regenerate(tmp_path):
    service, components, queue = build(tmp_path)
    preview = service.preview("p1")
    choice = next(item for item in preview["items"] if item["key"] == "test_status")
    operation = service.start("p1", {"request_id": "r", "workspace_token": "trusted", "items": [
        {"key": "test_status", "source_token": choice["source_token"], "action": "generate_missing"}]})
    original_register = components.register
    components.register = lambda *args: (_ for _ in ()).throw(RuntimeError("database unavailable"))
    fn, args = queue.pop()
    fn(*args)
    interrupted = service.read("p1", operation["operation_id"])
    assert interrupted["status"] == "interrupted"
    assert (tmp_path / "official" / "test_status.xlsx").read_bytes() == b"test_status"
    components.register = original_register
    components.source = lambda *args: (_ for _ in ()).throw(AssertionError("Recovery reread changing source"))
    service.resume("p1", operation["operation_id"])
    fn, args = queue.pop()
    fn(*args)
    result = service.read("p1", operation["operation_id"])
    assert result["status"] == "completed"
    assert components.calls == ["test_status"]
    assert components.records == ["test_status"]


def test_unknown_stage_after_process_loss_retains_fence(tmp_path):
    service, components, queue = build(tmp_path)
    preview = service.preview("p1")
    choice = next(item for item in preview["items"] if item["key"] == "test_status")
    operation = service.start("p1", {"request_id": "r", "workspace_token": "trusted", "items": [
        {"key": "test_status", "source_token": choice["source_token"], "action": "generate_missing"}]})
    state = service.journal.read("p1")
    stage = tmp_path / "unknown-stage"
    stage.mkdir()
    (stage / "unproven.xlsx").write_bytes(b"preserve")
    state["items"][0].update(stage=str(stage), stage_identity=None, status="generating")
    service.journal.save(state)
    fn, args = queue.pop()
    fn(*args)
    assert service.read("p1", operation["operation_id"])["status"] == "interrupted"
    assert (stage / "unproven.xlsx").read_bytes() == b"preserve"
    assert components.calls == []


def test_lost_worker_status_projects_interrupted_without_mutating_receipt(tmp_path):
    service, components, queue = build(tmp_path)
    preview = service.preview("p1")
    operation = service.start("p1", {"request_id": "r", "workspace_token": "trusted", "items": [
        {"key": "fee_form", "source_token": None, "action": "skip"}]})
    path = service.journal.project_path("p1") / "operation.json"
    before = path.read_bytes()
    service.owner = "new-process-owner"
    result = service.read("p1", operation["operation_id"])
    assert result["status"] == "interrupted"
    assert result["can_resume"]
    assert path.read_bytes() == before


def test_completed_request_replay_after_next_batch_returns_its_own_history(tmp_path):
    service, components, queue = build(tmp_path)
    request = {"request_id": "first", "workspace_token": "trusted", "items": [
        {"key": "test_status", "source_token": None, "action": "skip"}]}
    first = service.start("p1", request)
    fn, args = queue.pop()
    fn(*args)
    second = service.start("p1", {**request, "request_id": "second"})
    assert second["operation_id"] != first["operation_id"]
    replay = service.start("p1", request)
    assert replay["operation_id"] == first["operation_id"]
    assert replay["status"] == "completed"
    assert len(queue) == 1


def test_generator_failure_does_not_block_independent_selected_file(tmp_path):
    service, components, queue = build(tmp_path)
    original = components.generate
    def generate(project_id, key, stage, name):
        if key == "test_record":
            raise OSError("Template unavailable")
        return original(project_id, key, stage, name)
    components.generate = generate
    preview = service.preview("p1")
    choices = [{"key": item["key"], "source_token": item["source_token"], "action": "generate_missing"}
               for item in preview["items"] if item["key"] in {"test_record", "test_status"}]
    operation = service.start("p1", {"request_id": "r", "workspace_token": "trusted", "items": choices})
    fn, args = queue.pop()
    fn(*args)
    result = service.read("p1", operation["operation_id"])
    assert result["status"] == "completed"
    assert result["summary"] == {"generated": 1, "replaced": 0, "skipped": 0, "needs_input": 0, "failed": 1}
    assert components.calls == ["test_status"]


def test_locked_target_effect_stays_pending_while_independent_file_completes(tmp_path):
    from backend.application.project_file_generation_guard import require_project_file_generation_clear
    service, components, queue = build(tmp_path)
    original = service.files.publish
    def publish(journal, state, effect, verify):
        if effect["target"].endswith("test_record.xlsx"):
            raise ProjectFileTargetLockedError("Target is open in Word")
        return original(journal, state, effect, verify)
    service.files.publish = publish
    preview = service.preview("p1")
    choices = [{"key": item["key"], "source_token": item["source_token"], "action": "generate_missing"}
               for item in preview["items"] if item["key"] in {"test_record", "test_status"}]
    operation = service.start("p1", {"request_id": "r", "workspace_token": "trusted", "items": choices})
    fn, args = queue.pop()
    fn(*args)
    result = service.read("p1", operation["operation_id"])
    assert result["status"] == "interrupted"
    assert result["summary"]["generated"] == 1
    assert components.records == ["test_status"]
    with pytest.raises(ValueError, match="unfinished"):
        require_project_file_generation_clear(service.journal, "p1")


def test_generator_returning_unowned_file_retains_unsafe_operation(tmp_path):
    service, components, queue = build(tmp_path)
    outside = tmp_path / "unexpected.xlsx"
    def generate(*args):
        outside.write_bytes(b"unproven output")
        return outside
    components.generate = generate
    preview = service.preview("p1")
    item = next(item for item in preview["items"] if item["key"] == "test_status")
    operation = service.start("p1", {"request_id": "r", "workspace_token": "trusted", "items": [
        {"key": "test_status", "source_token": item["source_token"], "action": "generate_missing"}]})
    fn, args = queue.pop()
    fn(*args)
    assert service.read("p1", operation["operation_id"])["status"] == "interrupted"
    assert service.journal.read("p1")["items"][0]["unverified_generated_path"] == str(outside)
    assert outside.read_bytes() == b"unproven output"


def test_two_selected_kinds_cannot_share_the_same_publication_target(tmp_path):
    from dataclasses import replace
    service, components, queue = build(tmp_path)
    original_source = components.source
    components.source = lambda project_id, key: replace(original_source(project_id, key), target=tmp_path / "official" / "shared.docx")
    preview = service.preview("p1")
    choices = [{"key": item["key"], "source_token": item["source_token"], "action": "generate_missing"}
               for item in preview["items"] if item["key"] in {"test_record", "application_form"}]
    with pytest.raises(ValueError, match="share.*target"):
        service.start("p1", {"request_id": "r", "workspace_token": "trusted", "items": choices})
    assert queue == []
    assert components.calls == []


def test_resume_locked_frozen_effect_still_generates_later_unstarted_file(tmp_path):
    service, components, queue = build(tmp_path)
    original = service.files.publish
    service.files.publish = lambda *args: (_ for _ in ()).throw(SystemExit("process loss"))
    preview = service.preview("p1")
    choices = [{"key": item["key"], "source_token": item["source_token"], "action": "generate_missing"}
               for item in preview["items"] if item["key"] in {"test_record", "test_status"}]
    operation = service.start("p1", {"request_id": "r", "workspace_token": "trusted", "items": choices})
    fn, args = queue.pop()
    with pytest.raises(SystemExit):
        fn(*args)
    assert components.calls == ["test_record"]
    def publish(journal, state, effect, verify):
        if effect["target"].endswith("test_record.xlsx"):
            raise ProjectFileTargetLockedError("Target is open in Word")
        return original(journal, state, effect, verify)
    service.files.publish = publish
    service.resume("p1", operation["operation_id"])
    fn, args = queue.pop()
    fn(*args)
    result = service.read("p1", operation["operation_id"])
    assert result["status"] == "interrupted"
    assert components.records == ["test_status"]
    assert components.calls == ["test_record", "test_status"]


def test_process_loss_after_output_bytes_before_identity_keeps_stage_unresolved(tmp_path):
    from backend.infrastructure.files.recoverable_output_publisher import file_identity
    service, components, queue = build(tmp_path)
    operation = service.start("p1", {"request_id": "r", "workspace_token": "trusted", "items": [
        {"key": "test_status", "source_token": None, "action": "skip"}]})
    state = service.journal.read("p1")
    stage = tmp_path / "owned-directory"
    stage.mkdir()
    (stage / "not-yet-journaled.xlsx").write_bytes(b"possibly partial")
    state["items"][0].update(stage=str(stage), stage_identity=file_identity(stage), status="generating", action="generate_missing")
    service.journal.save(state)
    fn, args = queue.pop()
    fn(*args)
    assert service.read("p1", operation["operation_id"])["status"] == "interrupted"
    assert (stage / "not-yet-journaled.xlsx").read_bytes() == b"possibly partial"


def test_explicit_skip_of_unreadable_target_does_not_block_other_selected_file(tmp_path):
    service, components, queue = build(tmp_path)
    original_facts = service.files.facts
    def facts(path):
        if path and str(path).endswith("test_record.xlsx"):
            raise PermissionError("Word has locked this file")
        return original_facts(path)
    service.files.facts = facts
    preview = service.preview("p1")
    selected = next(item for item in preview["items"] if item["key"] == "test_status")
    operation = service.start("p1", {"request_id": "r", "workspace_token": "trusted", "items": [
        {"key": "test_record", "source_token": None, "action": "skip"},
        {"key": "test_status", "source_token": selected["source_token"], "action": "generate_missing"}]})
    fn, args = queue.pop()
    fn(*args)
    assert service.read("p1", operation["operation_id"])["status"] == "completed"
    assert components.calls == ["test_status"]


def test_queued_worker_that_failed_to_acquire_lock_becomes_explicitly_resumable(tmp_path):
    service, components, queue = build(tmp_path)
    operation = service.start("p1", {"request_id": "r", "workspace_token": "trusted", "items": [
        {"key": "fee_form", "source_token": None, "action": "skip"}]})
    assert operation["status"] == "queued"
    fn, args = queue.pop()
    with service.shared.lock("p1"):
        fn(*args)
    before = (service.journal.project_path("p1") / "operation.json").read_bytes()
    result = service.read("p1", operation["operation_id"])
    assert result["status"] == "interrupted"
    assert result["can_resume"]
    assert (service.journal.project_path("p1") / "operation.json").read_bytes() == before
    assert components.calls == []
