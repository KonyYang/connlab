"""Move independent project records between normal, trash and retained history."""

from contextlib import ExitStack
from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Protocol
from uuid import uuid4

from backend.application.project_identity import resolve_project_identity, display_identity_override_from_values
from backend.application.project_lifecycle_state_service import project_close_reason_label
from backend.application.project_registry_models import (
    ProjectRegistryEntry, ProjectRegistryPreview, ProjectRegistryConflict, ProjectRegistryNotFound,
)


class RegistryStore(Protocol):
    def get(self, project_id): ...
    def list(self, *, registry_state="active"): ...
    def atomic(self): ...
    def move(self, project_id, destination, **audit): ...
    def commit(self): ...
    def retained_inventory(self, project_id): ...


class ProjectRegistryManagementService:
    """Conflict decisions and complete audited transitions behind one public seam."""

    def __init__(self, registry: RegistryStore, ltrs, generation_journal, *, basic_information=None,
                 temporary_context=None, clock=None):
        self._registry, self._ltrs, self._generation = registry, ltrs, generation_journal
        self._basic, self._temporary = basic_information, temporary_context
        self._clock = clock or (lambda: datetime.now(timezone.utc).isoformat())

    def list_entries(self, location):
        if location not in {"trash", "history"}:
            raise ValueError("Management lists require trash or history.")
        return [self._entry(project) for project in self._registry.list(registry_state=location)]

    def preview(self, project_id, action):
        if action not in {"trash", "restore"}:
            raise ValueError("Unknown management action.")
        project = self._registry.get(project_id)
        if project is None:
            raise ProjectRegistryNotFound(f"Project not found: {project_id}")
        entry = self._entry(project)
        conflicts = tuple(sorted((self._entry(other) for other in self._registry.list()
            if other.project_id != project_id and self._identity_key(other) == self._identity_key(project)),
            key=lambda other: other.project_id)) if action == "restore" else ()
        blockers = []
        if action == "trash" and entry.registry_state == "trash":
            blockers.append("Project is already in the recycle bin.")
        if action == "restore" and entry.registry_state == "active":
            blockers.append("Project is already in the normal registry.")
        try:
            state = self._generation.read(project_id)
            if state and state["status"] in {"queued", "running"}:
                blockers.append("Project folder generation is queued or running. Wait for it to finish before moving the project.")
        except (ValueError, OSError):
            blockers.append("Generation state is unavailable. Review the generation journal before moving the project.")
        inventory = self._registry.retained_inventory(project_id)
        retained = (
            *(f"{label} retained: {count}" for label, count in inventory.items()),
            "Matrix, schedules, fees, reports and traceability records stay with this project.",
            "Public-drive folders, original materials and LTR workbook records are not changed or deleted.",
            "LTR ownership remains unchanged; restoring this record does not transfer its registration.",
        )
        payload = {"action": action, "project": asdict(entry), "conflicts": [asdict(item) for item in conflicts],
                   "inventory": inventory}
        token = sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        return ProjectRegistryPreview(entry, action, token, conflicts, tuple(blockers), retained,
            ("Existing external files and LTR associations are retained.",))

    def trash(self, project_id, *, token, reason, actor=None):
        reason = (reason or "").strip()
        if not reason:
            raise ValueError("A deletion reason is required.")
        return self._transition(project_id, "trash", token, "trash", False, reason, actor)

    def restore(self, project_id, *, token, destination="active", replace_conflicts=False, actor=None):
        if destination not in {"active", "history"}:
            raise ValueError("Restore destination must be active or history.")
        if destination == "history" and replace_conflicts:
            raise ValueError("Restoring only to history cannot replace active conflicts.")
        return self._transition(project_id, "restore", token, destination, replace_conflicts, "Restored by operator.", actor)

    def _transition(self, project_id, action, token, destination, replace_conflicts, reason, actor):
        with self._registry.atomic():
            preview = self.preview(project_id, action)
            if token != preview.token:
                raise ProjectRegistryConflict("Project or conflicts changed. Refresh the preview before confirming.",
                                              "project_registry_preview_stale")
            if preview.blockers:
                raise ProjectRegistryConflict(preview.blockers[0], "project_registry_move_blocked")
            replacements = preview.conflicts if destination == "active" else ()
            if replacements and not replace_conflicts:
                raise ProjectRegistryConflict("An active project with the same identifier exists; choose how to resolve the conflict.")
            entries = (preview.project, *replacements)
            # Lock every affected record, including the project displaced into history.
            # BEGIN IMMEDIATE prevents a new conflict appearing between review and commit.
            with ExitStack() as locks:
                for entry in sorted(entries, key=lambda item: item.project_id):
                    try:
                        locks.enter_context(self._generation.lock(entry.project_id))
                        generation = self._generation.read(entry.project_id)
                        if generation and generation["status"] in {"queued", "running"}:
                            raise ProjectRegistryConflict("Project generation is queued or running. Wait before moving it.")
                    except (ValueError, OSError) as exc:
                        raise ProjectRegistryConflict(str(exc), "project_registry_move_blocked") from exc
                now, operation_id = self._clock(), uuid4().hex
                for entry in replacements:
                    self._registry.move(entry.project_id, "history", expected_revision=entry.registry_revision,
                        reason=f"Retained while restoring project {project_id}.", actor=actor, changed_at=now,
                        operation_id=operation_id)
                self._registry.move(project_id, destination, expected_revision=preview.project.registry_revision,
                    reason=reason, actor=actor, changed_at=now, operation_id=operation_id)
                self._registry.commit()
                return self._entry(self._registry.get(project_id))

    def _identity_key(self, project):
        identity = resolve_project_identity(project, self._ltrs.list_by_project(project.project_id))
        return identity.display_project_id.strip().casefold()

    def _entry(self, project):
        basic = self._basic.get_latest_confirmed(project.project_id) if self._basic else None
        identity = resolve_project_identity(project, self._ltrs.list_by_project(project.project_id),
            identity_override=display_identity_override_from_values(basic.values if basic else None))
        temporary = self._temporary.get_by_project(project.project_id) if self._temporary else None
        return ProjectRegistryEntry(
            project_id=project.project_id, display_project_id=identity.display_project_id,
            sample_description=identity.sample_description or (temporary.sample_description if temporary else None),
            test_item=identity.test_item or (temporary.test_item if temporary else None),
            requestor=project.requestor, created_on=project.created_on.isoformat() if project.created_on else None,
            lifecycle_state=project.lifecycle_state.value,
            close_reason_label=(project_close_reason_label(project.close_reason_category)
                                if project.close_reason_category else None),
            registry_state=project.registry_state, registry_revision=project.registry_revision,
            changed_at=project.registry_changed_at, reason=project.registry_reason,
        )
