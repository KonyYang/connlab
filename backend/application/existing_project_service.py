"""Reviewed in-place intake; source files and external authorities stay unchanged."""
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from uuid import uuid4

from backend.domain import Project
from backend.application.project_registry_models import ProjectRegistryConflict, ProjectRegistryNotFound
from backend.application.project_identity import resolve_project_identity


def _fingerprint(value):
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


class ExistingProjectService:
    def __init__(self, locations, registry, files, generation):
        self.locations, self.registry, self.gateway, self.generation = locations, registry, files, generation

    def _project(self, project_id, *, writable=False):
        project = self.registry.get(project_id)
        if not project:
            raise ProjectRegistryNotFound("Project record no longer exists.")
        if writable and project.registry_state != "active":
            raise ProjectRegistryConflict("Restore the retained project before linking or relocating its folders.")
        return project

    def _state(self):
        return {"projects": [{"project_id": p.project_id, "number": p.project_no, "name": p.product_name,
                              "display_project_id": resolve_project_identity(p, self.registry.ltr_records(p.project_id)).display_project_id,
                              "state": p.registry_state, "revision": p.registry_revision}
                             for p in self.registry.list(registry_state="all")],
                "numbers": sorted(self.locations.numbers()),
                "locations": [{"id": row.location_id, "project_id": row.project_id, "path": row.root_path,
                               "number": row.management_number, "source_number": row.source_number,
                               "source_project_id": row.source_project_id, "revision": row.revision}
                              for row in self.locations.list()]}

    def preview(self, path):
        source = self.gateway.inspect(path)
        state = self._state()
        existing = self.locations.by_path(source["path"])
        number = (source["source_number"] or "").casefold()
        conflicts = [p for p in state["projects"] if p["project_id"] == source["source_project_id"]
                     or (number and (p["number"] or "").casefold() == number)]
        aliases = {row["project_id"] for row in state["locations"]
                   if (source["source_project_id"] and row["source_project_id"] == source["source_project_id"])
                   or (number and (row["source_number"] or "").casefold() == number)}
        for project in state["projects"]:
            if project["project_id"] in aliases and not any(p["project_id"] == project["project_id"] for p in conflicts):
                conflicts.append(project)
        # Registered LTR may differ from legacy project_no: consult the real identity too.
        for project in self.registry.list(registry_state="all"):
            if self.registry.identity_numbers(project.project_id) & {number} and not any(p["project_id"] == project.project_id for p in conflicts):
                conflicts.append(next(p for p in state["projects"] if p["project_id"] == project.project_id))
        return {**source, "token": _fingerprint([source, state]), "conflicts": conflicts,
                "targets": state["projects"], "existing": self._view(existing) if existing else None,
                "suggested_number": source["source_number"] or f"LEG-{_fingerprint(source['path'])[:8].upper()}",
                "notice": "Files only: Matrix, fees, results and LTR registration are not restored or confirmed."}

    def scan(self, roots, depth=1):
        return self.gateway.scan(roots, depth=depth)

    def register(self, *, path, token, action, management_number="", target_project_id=None, ignore_manifest=False):
        if action == "skip":
            return {"skipped": True}
        if action not in {"register", "independent", "link"}:
            raise ValueError("Choose register, independent, link or skip.")
        number = management_number.strip()
        if action != "link" and (not number or len(number) > 128 or any(ord(c) < 32 for c in number)):
            raise ValueError("Enter a local management number (1–128 characters).")
        decision = _fingerprint([action, number, target_project_id, bool(ignore_manifest)])
        with self.registry.atomic():
            current = self.preview(path)
            existing = self.locations.by_path(current["path"])
            if existing:
                self._project(existing.project_id, writable=True)
                if (existing.approval_token == token and existing.decision_fingerprint == decision
                        and existing.source_fingerprint == current["source_fingerprint"]):
                    return self._view(existing)
                raise ProjectRegistryConflict("This directory is already managed. Open its project or review relocation; it will not be imported twice.")
            if token != current["token"]:
                raise ProjectRegistryConflict("Source or local records changed. Refresh the preview and review again.")
            if current["manifest_error"] and not (action == "independent" and ignore_manifest):
                raise ProjectRegistryConflict("Review the manifest error; explicitly import independently as files only to continue.")
            source_id = current["source_project_id"]
            source_claims = {row.project_id for row in self.locations.list() if source_id and row.source_project_id == source_id}
            if source_id and self.registry.get(source_id):
                source_claims.add(source_id)
            if any(self.registry.get(pid).registry_state != "active" for pid in source_claims):
                raise ProjectRegistryConflict("A retained project matches this source ID. Restore it before intake.")
            if action == "link":
                project = self._project(target_project_id, writable=True)
                number = project.project_no or f"LOCAL-{project.project_id[:8].upper()}"
                linked = next((row for row in self.locations.list() if row.project_id == project.project_id), None)
                if linked:
                    number = linked.management_number
                project_id = project.project_id
            else:
                if current["conflicts"] and action != "independent":
                    raise ProjectRegistryConflict("A matching source identity or number already exists locally. Explicitly link the same project or import as an independent project.")
                used = {(p.project_no or "").strip().casefold() for p in self.registry.list(registry_state="all")}
                used.update(n.strip().casefold() for n in self.locations.numbers())
                used.update(row.management_number.casefold() for row in self.locations.list())
                if number.casefold() in used:
                    raise ProjectRegistryConflict("That management number already exists, including retained records. Choose a different number or explicitly link the existing project.")
                project_id = source_id if source_id and action == "register" else uuid4().hex
                project = Project(project_id=project_id, project_no=number, product_name=current["name"],
                                  requestor="", created_on=date.today())
            with self.generation.lock(project_id):
                self._check_idle(project_id)
                fresh = self.gateway.inspect(path)
                if fresh != {key: current[key] for key in fresh}:
                    raise ProjectRegistryConflict("Source changed. Refresh the preview.")
                if action != "link":
                    self.registry.create(project)
                row = self.locations.add(location_id=uuid4().hex, project_id=project_id, root_path=current["path"],
                    management_number=number, source_number=current["source_number"], source_project_id=source_id,
                    source_kind=current["source_kind"], source_fingerprint=current["source_fingerprint"],
                    root_identity=current["root_identity"], relocation_history="[]",
                    decision_fingerprint=decision, approval_token=token, revision=0,
                    registered_at=datetime.now(timezone.utc).isoformat())
                self.registry.commit()
                return self._view(row)

    def _check_idle(self, project_id):
        state = self.generation.read(project_id)
        if state and state["status"] in {"queued", "running"}:
            raise ProjectRegistryConflict("Project generation is queued or running. Wait before changing folder associations.")

    def _view(self, row):
        project = self._project(row.project_id)
        return {"location_id": row.location_id, "project_id": row.project_id, "path": row.root_path,
                "management_number": row.management_number, "source_number": row.source_number,
                "source_project_id": row.source_project_id, "source_kind": row.source_kind,
                "registry_state": project.registry_state, "revision": row.revision,
                "product_name": project.product_name, "registered_at": row.registered_at}

    def list_locations(self, project_id=None):
        return [self._view(row) for row in self.locations.list() if project_id is None or row.project_id == project_id]

    def _location(self, location_id, *, writable=False):
        row = self.locations.get(location_id)
        if not row:
            raise ProjectRegistryNotFound("Registered folder was not found.")
        self._project(row.project_id, writable=writable)
        return row

    def files(self, location_id, relative=""):
        row = self._location(location_id)
        return self.gateway.files(row.root_path, relative, identity=row.root_identity)

    def file(self, location_id, relative):
        row = self._location(location_id)
        self.gateway.verify_root(row.root_path, row.root_identity)
        return self.gateway.file(row.root_path, relative)

    def open_file(self, location_id, relative):
        row = self._location(location_id)
        return self.gateway.open_file(row.root_path, row.root_identity, relative)

    def preview_relocation(self, location_id, path):
        row = self._location(location_id, writable=True)
        source = self.gateway.inspect(path)
        claimed = self.locations.by_path(source["path"])
        blockers = []
        if claimed and claimed.location_id != location_id:
            blockers.append("This folder is already linked. Keep its existing association.")
        if source["manifest_error"]:
            blockers.append(source["manifest_error"])
        if source["source_project_id"] and source["source_project_id"] not in {row.source_project_id, row.project_id}:
            blockers.append("The selected folder identifies a different project.")
        current = self._view(row)
        return {"location": current, "source": source, "blockers": blockers,
                "token": _fingerprint([current, source, self._state()])}

    def relocate(self, location_id, *, path, token):
        with self.registry.atomic():
            preview = self.preview_relocation(location_id, path)
            if token != preview["token"]:
                raise ProjectRegistryConflict("Folder or records changed. Refresh the relocation preview.")
            if preview["blockers"]:
                raise ProjectRegistryConflict(preview["blockers"][0])
            row = self._location(location_id, writable=True)
            with self.generation.lock(row.project_id):
                self._check_idle(row.project_id)
                if self.gateway.inspect(path) != preview["source"]:
                    raise ProjectRegistryConflict("Folder changed. Refresh the relocation preview.")
                history = json.loads(row.relocation_history)
                history.append({"path": row.root_path, "root_identity": row.root_identity,
                                "changed_at": datetime.now(timezone.utc).isoformat()})
                row.relocation_history = json.dumps(history, ensure_ascii=False)
                row.root_path = preview["source"]["path"]
                row.root_identity = preview["source"]["root_identity"]
                row.source_fingerprint = preview["source"]["source_fingerprint"]
                row.revision += 1
                self.locations.flush()
                self.registry.commit()
                return self._view(row)

