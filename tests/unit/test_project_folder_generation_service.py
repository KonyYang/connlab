from backend.application.project_folder_generation_service import (
    GENERATION_STEPS,
    ProjectFolderInUseError,
    ProjectFolderGenerationService,
    basic_information_generation_blocker,
)
from backend.infrastructure.files.generation_journal import GenerationJournal
import pytest


def test_basic_information_preflight_distinguishes_missing_unconfirmed_and_changed_data():
    assert basic_information_generation_blocker(
        status="unconfirmed",
        missing_required_labels=("Project Leader", "Lab Performing the Tests"),
    ) == (
        "Basic Information is incomplete. Complete these required fields before "
        "generating Project Folder outputs: Project Leader, Lab Performing the Tests."
    )
    assert basic_information_generation_blocker(
        status="unconfirmed", missing_required_labels=()
    ) == (
        "Basic Information is complete but not confirmed. Open Basic Information "
        "and click Confirm before generating Project Folder outputs."
    )
    assert basic_information_generation_blocker(
        status="needs_review", missing_required_labels=()
    ) == (
        "Basic Information source data changed after confirmation. Review and confirm "
        "the current Basic Information before generating Project Folder outputs."
    )
    assert basic_information_generation_blocker(
        status="confirmed", missing_required_labels=()
    ) is None


def test_backend_runs_chain_without_browser_and_resumes_at_failed_step(tmp_path):
    calls = []
    fail = [True]
    queued = []
    def step(state, name):
        calls.append(name)
        if name == "fee_form" and fail[0]:
            raise ValueError("Temporary failure")
    service = ProjectFolderGenerationService(GenerationJournal(tmp_path), lambda _: "same", step, queued.append)
    started = service.start("p", None, "same", "request-1")
    assert calls == []
    queued.pop()()
    assert service.read("p")["status"] == "blocked"
    assert service.read("p")["completed_steps"] == list(GENERATION_STEPS[:4])
    fail[0] = False
    service.resume("p", started["operation_id"])
    queued.pop()()
    assert service.read("p")["status"] == "completed"
    assert calls.count("workspace") == 1
    assert calls.count("fee_form") == 2
    service.start("p", None, "same", "request-1")
    assert queued == []


def test_completed_workspace_requires_explicit_in_place_intent_to_keep_custom_folder(tmp_path):
    queued = []
    seen_intents = []

    def preview(_project_id, intent):
        seen_intents.append(intent)
        return {
            "expected_context": f"context-{intent}",
            "workspace_preview": {"status": "completed"},
            "start_blockers": [], "review_conflicts": [],
        }

    service = ProjectFolderGenerationService(
        GenerationJournal(tmp_path), lambda _: "same", lambda _state, _name: None,
        queued.append, preview=preview,
    )
    with pytest.raises(ValueError, match="already exists"):
        service.start("p", None, "context-create", "without-consent")
    started = service.start("p", "update_in_place", "context-update_in_place", "explicit-consent")
    assert started["status"] == "queued"
    assert seen_intents[-1] == "update_in_place"
    assert len(queued) == 1


@pytest.mark.parametrize("failure", [PermissionError, OSError])
def test_failed_finalization_requires_resume_not_replacement(tmp_path, caplog, failure):
    import logging
    caplog.set_level(logging.INFO, logger="connlab.operations")
    queued, fail, steps, finalizations = [], [True], [], []
    def finalize(state):
        finalizations.append(state["operation_id"])
        if fail[0]:
            raise failure("cleanup interrupted")
    journal = GenerationJournal(tmp_path)
    service = ProjectFolderGenerationService(journal, lambda _: "same",
        lambda state, name: steps.append(name), queued.append, finalize=finalize)
    started = service.start("p", None, "same", "first")
    queued.pop()()
    blocked = service.read("p")
    assert blocked["status"] == "blocked"
    assert blocked["completed_steps"] == list(GENERATION_STEPS)
    assert blocked["can_restart"] is False
    assert journal.read("p")["finalization_pending"] is True
    assert "outputs are ready" in blocked["message"]
    assert "old-copy cleanup" in blocked["message"]
    assert "resume" in blocked["message"]
    assert "Stage: folder_finalization" in blocked["message"]
    assert "Diagnostic ID:" in blocked["message"]
    assert '"stage": "folder_finalization"' in caplog.text
    with pytest.raises(ValueError):
        service.start("p", "backup_and_recreate", "same", "second", started["operation_id"])
    fail[0] = False
    service.resume("p", started["operation_id"])
    queued.pop()()
    assert service.read("p")["status"] == "completed"
    assert journal.read("p")["finalization_pending"] is False
    assert steps == list(GENERATION_STEPS)
    assert finalizations == [started["operation_id"], started["operation_id"]]


def test_overwrite_cleanup_intent_prevents_replacement_before_finalize_checkpoint(tmp_path):
    journal, queued = GenerationJournal(tmp_path), []
    def step(state, name):
        if name == "workspace":
            state["effects"]["workspace"] = {
                "step": "workspace", "overwrite_cleanup": True, "prior": "old-files",
            }
            journal.save(state)
        else:
            raise ValueError("Later file needs repair")
    service = ProjectFolderGenerationService(journal, lambda _: "same", step, queued.append)
    state = journal.create("p", "overwrite_rebuild", "same")
    state.update(request_id="historical", owner=service.owner)
    journal.save(state)
    started = service._view(state)
    service.dispatch(lambda: service.run("p", state["operation_id"]))
    queued.pop()()
    assert service.read("p")["can_restart"] is False
    with pytest.raises(ValueError, match="safely checkpointed"):
        service.start("p", "backup_and_recreate", "same", "second", started["operation_id"])


def test_changed_input_blocks_resume_before_any_more_writes(tmp_path):
    queued, context, calls = [], ["old"], []
    service = ProjectFolderGenerationService(GenerationJournal(tmp_path), lambda _: context[0],
                                           lambda state, name: calls.append(name), queued.append)
    started = service.start("p", None, "old", "req")
    context[0] = "changed"
    queued.pop()()
    assert service.read("p")["status"] == "blocked"
    assert calls == []


def test_corrected_inputs_start_a_new_explicit_operation_without_rebinding_or_replaying_choice(tmp_path):
    queued, context = [], ["old"]
    def step(state, name):
        if name == "materials":
            raise ValueError("Missing source")
    journal = GenerationJournal(tmp_path)
    service = ProjectFolderGenerationService(journal, lambda _: context[0], step, queued.append)
    original = service.start("p", "backup_and_recreate", "old", "first")
    queued.pop()()
    context[0] = "corrected"
    fresh = service.start("p", None, "corrected", "second", replaces_operation_id=original["operation_id"])
    assert fresh["operation_id"] != original["operation_id"]
    assert journal.read("p")["strategy"] is None
    assert journal.read("p")["context"] == "corrected"
    assert journal.read_archived("p", original["operation_id"])["context"] == "old"


def test_cannot_replace_an_operation_with_uncheckpointed_publication(tmp_path):
    journal, queued = GenerationJournal(tmp_path), []
    def step(state, name):
        state["effects"]["pending"] = {"step": name}
        journal.save(state)
        raise ValueError("Published before index commit")
    service = ProjectFolderGenerationService(journal, lambda _: "same", step, queued.append)
    original = service.start("p", None, "same", "one")
    queued.pop()()
    assert service.read("p")["can_restart"] is False
    with pytest.raises(ValueError, match="safely checkpointed"):
        service.start("p", None, "same", "two", replaces_operation_id=original["operation_id"])
    assert journal.read("p")["operation_id"] == original["operation_id"]


@pytest.mark.parametrize("strategy", ["continue_existing", "overwrite_rebuild"])
def test_new_generation_rejects_legacy_mutating_strategies(tmp_path, strategy):
    service = ProjectFolderGenerationService(
        GenerationJournal(tmp_path), lambda _: "same", lambda *_: None, lambda *_: None
    )

    with pytest.raises(ValueError, match="not available for new project folder operations"):
        service.start("p", strategy, "same", "request")


@pytest.mark.parametrize("strategy", ["continue_existing", "overwrite_rebuild"])
def test_pre_upgrade_journal_resumes_with_legacy_token_and_rebuild_intent(
    tmp_path, strategy
):
    journal, queued, preview_intents, steps = GenerationJournal(tmp_path), [], [], []

    def preview(_project_id, intent):
        preview_intents.append(intent)
        return {
            "expected_context": "version-2-token",
            "legacy_expected_context": "pre-upgrade-token",
        }

    service = ProjectFolderGenerationService(
        journal,
        lambda _: "same",
        lambda _state, name: steps.append(name),
        queued.append,
        preview=preview,
    )
    historical = journal.create("p", strategy, "same")
    historical.update(
        request_id="historical-request",
        owner="pre-upgrade-backend",
        preview_context="pre-upgrade-token",
    )
    journal.save(historical)

    service.resume("p", historical["operation_id"])
    queued.pop()()

    assert preview_intents == ["backup_rebuild"]
    assert service.read("p")["status"] == "completed"
    assert steps == list(GENERATION_STEPS)


def test_locked_existing_folder_explains_resume_and_safe_continue_choices(tmp_path):
    queued = []

    def locked_step(_state, _name):
        raise ProjectFolderInUseError("official-folder")

    service = ProjectFolderGenerationService(
        GenerationJournal(tmp_path), lambda _: "same", locked_step, queued.append
    )
    service.start("p", "backup_and_recreate", "same", "one")
    queued.pop()()

    result = service.read("p")
    assert result["status"] == "blocked"
    assert result["can_restart"] is True
    assert "Windows denied access" in result["message"]
    assert "rebuild option" in result["message"]
    assert "Diagnostic ID:" in result["message"]


def test_unrelated_permission_error_keeps_generic_storage_guidance(tmp_path):
    queued = []
    service = ProjectFolderGenerationService(
        GenerationJournal(tmp_path),
        lambda _: "same",
        lambda _state, _name: (_ for _ in ()).throw(
            PermissionError(5, "Access is denied", "generated-form")
        ),
        queued.append,
    )
    service.start("p", None, "same", "one")
    queued.pop()()

    assert service.read("p")["message"].startswith(
        "Folder storage is unavailable or changed. Review the configured folder before resuming."
    )

def test_blocked_folder_reports_access_denial_with_diagnostic_id(tmp_path, caplog):
    import logging
    from backend.application.project_folder_generation_service import ProjectFolderInUseError
    from backend.infrastructure.files.generation_journal import GenerationJournal
    caplog.set_level(logging.INFO, logger="connlab.operations")
    journal = GenerationJournal(tmp_path / "diagnostic-journal")
    def denied(state, name):
        original = PermissionError(13, "Access denied")
        original.winerror = 5
        raise ProjectFolderInUseError("private-path") from original
    service = ProjectFolderGenerationService(journal, lambda _: "context", denied, lambda callback: callback())
    service.start("p", "backup_and_recreate", "context", "request")
    result = service.read("p")
    assert result["status"] == "blocked"
    assert "Diagnostic ID:" in result["message"]
    assert "folder_workspace" in result["message"]
    assert "denied access" in result["message"]
    assert result["operation_id"] in caplog.text
    assert '"winerror": 5' in caplog.text
