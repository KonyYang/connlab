import json
from pathlib import Path
import runpy
from types import SimpleNamespace
import pytest

from backend.api import dependencies as deps
from backend.infrastructure.files.public_folder_workflow_gateway import PublicFolderWorkflowGateway


fixture = runpy.run_path(str(Path(__file__).with_name("test_basic_project_workspace_api.py")))


def test_binding_is_committed_before_partial_sync_and_description_change_does_not_duplicate(tmp_path, monkeypatch):
    with fixture["prepared"](tmp_path) as (client, sessions, _, public):
        result = fixture["create"](client)
        folder = Path(result["official_project_folder_path"])
        (folder / "a.txt").write_bytes(b"a")
        (folder / "b.txt").write_bytes(b"b")
        prefix = "/api/projects/P1/public-folder-workflow"
        preview = client.get(prefix + "/binding/preview").json()
        assert preview["can_create"] and preview["candidates"] == []
        confirmation = client.post(prefix + "/binding/confirm", json={"expected_context": preview["expected_context"], "candidate_id": "create"})
        assert confirmation.status_code == 200, confirmation.text
        assert confirmation.json()["status"] == "bound"
        destination = Path(confirmation.json()["current_path"])
        assert list(destination.iterdir()) == []
        original = PublicFolderWorkflowGateway.copy_new_file
        observed = []
        def copy(self, source, target, **kwargs):
            with sessions() as other:
                saved = deps.PublicFolderWorkflowRepository(other).get_state("P1")
                assert json.loads(saved.binding_json)["path"] == str(destination)
                observed.append(target.name)
            if source.name == "a.txt":
                raise PermissionError("injected individual file failure")
            return original(self, source, target, **kwargs)
        monkeypatch.setattr(PublicFolderWorkflowGateway, "copy_new_file", copy)
        sync = client.post(prefix + "/sync/preview").json()
        copied = client.post(prefix + "/sync/execute", json={"preview_hash": sync["preview_hash"], "confirmed": True, "confirm_directory_creation": True})
        assert copied.status_code == 200, copied.text
        assert copied.json()["status"] == "partial"
        assert (destination / "b.txt").read_bytes() == b"b"
        assert not (destination / "a.txt").exists()
        assert observed
        assert client.get(prefix + "/binding/preview").json()["current_path"] == str(destination)


def test_binding_confirmation_cannot_approve_raw_or_stale_path(tmp_path):
    with fixture["prepared"](tmp_path) as (client, sessions, _, public):
        fixture["create"](client)
        prefix = "/api/projects/P1/public-folder-workflow/binding"
        preview = client.get(prefix + "/preview").json()
        outside = tmp_path / "outside"
        denied = client.post(prefix + "/confirm", json={"expected_context": preview["expected_context"], "candidate_id": str(outside)})
        assert denied.status_code == 409 and not outside.exists()
        candidate = public / "Open projects" / "2026" / "DL-2026-09-002A Old description"
        candidate.mkdir()
        stale = client.post(prefix + "/confirm", json={"expected_context": preview["expected_context"], "candidate_id": "create"})
        assert stale.status_code == 409
        with sessions() as session:
            assert deps.PublicFolderWorkflowRepository(session).get_state("P1").binding_json is None


def test_submit_restart_recovers_only_proven_closed_directory_metadata(tmp_path, monkeypatch):
    from backend.infrastructure.storage.repositories.public_folder_workflow import PublicFolderWorkflowRepository
    with fixture["prepared"](tmp_path) as (client, sessions, _, public):
        local = Path(fixture["create"](client)["official_project_folder_path"])
        (local / "record.txt").write_bytes(b"retained result")
        (public / "Closed projects" / "2026").mkdir(parents=True)
        monkeypatch.setattr(deps, "get_official_project_folder_check_service", lambda *_: SimpleNamespace(
            preview=lambda _: SimpleNamespace(status="complete", blockers=())))
        prefix = "/api/projects/P1/public-folder-workflow"
        sync = client.post(prefix + "/sync/preview").json()
        synced = client.post(prefix + "/sync/execute", json={"preview_hash": sync["preview_hash"], "confirmed": True, "confirm_directory_creation": True})
        assert synced.status_code == 200, synced.text
        original = PublicFolderWorkflowRepository.save_state
        def fail_after_move(self, state):
            if state.sync_locked:
                raise RuntimeError("injected DB interruption after public move")
            return original(self, state)
        monkeypatch.setattr(PublicFolderWorkflowRepository, "save_state", fail_after_move)
        submit = client.post(prefix + "/submit/preview").json()
        assert not submit["blockers"], submit
        with pytest.raises(RuntimeError, match="after public move"):
            client.post(prefix + "/submit/execute", json={"preview_hash": submit["preview_hash"], "confirmed": True})
        closed = public / "Closed projects" / "2026" / local.name
        assert (closed / "record.txt").read_bytes() == b"retained result"
        with sessions() as fresh:
            retained = json.loads(deps.PublicFolderWorkflowRepository(fresh).get_state("P1").binding_json)
            assert retained["pending_submit"]["target"] == str(closed)
        monkeypatch.setattr(PublicFolderWorkflowRepository, "save_state", original)
        assert client.post(prefix + "/sync/preview").json()["blockers"]
        restarted = client.post(prefix + "/submit/preview").json()
        assert restarted["status"] == "ready", restarted
        completed = client.post(prefix + "/submit/execute", json={"preview_hash": restarted["preview_hash"], "confirmed": True})
        assert completed.status_code == 200, completed.text
        assert completed.json()["status"] == "completed"
        with sessions() as fresh:
            saved = deps.PublicFolderWorkflowRepository(fresh).get_state("P1")
            assert saved.sync_locked
            assert json.loads(saved.binding_json)["path"] == str(closed)
            assert "pending_submit" not in json.loads(saved.binding_json)
        assert not (public / "Open projects" / "2026" / local.name).exists()


def test_invalid_saved_association_keeps_rebinding_reachable_without_open_authority(tmp_path):
    with fixture["prepared"](tmp_path) as (client, sessions, _, public):
        local = Path(fixture["create"](client)["official_project_folder_path"])
        (local / "managed.txt").write_bytes(b"managed")
        prefix = "/api/projects/P1/public-folder-workflow"
        preview = client.post(prefix + "/sync/preview").json()
        result = client.post(prefix + "/sync/execute", json={"preview_hash": preview["preview_hash"], "confirmed": True, "confirm_directory_creation": True})
        assert result.status_code == 200, result.text
        original = public / "Open projects" / "2026" / local.name
        changed = original.with_name("DL-2026-09-002A Manual new description")
        original.rename(changed)
        context = client.get(prefix + "/context").json()
        assert context["local_official_folder_available"]
        assert context["blockers"] == []
        assert context["warnings"]
        assert not context["public_open_folder_available"]
        sync = client.post(prefix + "/sync/preview").json()
        assert sync["status"] == "blocked"
        choices = client.get(prefix + "/binding/preview").json()
        assert choices["status"] == "review_required" and len(choices["candidates"]) == 1
        confirmed = client.post(prefix + "/binding/confirm", json={"expected_context": choices["expected_context"], "candidate_id": choices["candidates"][0]["candidate_id"]})
        assert confirmed.status_code == 200, confirmed.text
        with sessions() as session:
            record = deps.PublicFolderWorkflowRepository(session).get_file("P1", Path("managed.txt"))
            assert record.public_path == changed / "managed.txt"
        assert not original.exists()
