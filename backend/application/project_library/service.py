"""User-facing project intake and takeover orchestration through explicit adapters."""
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from backend.domain.project_library import ProjectLibraryConflict, ProjectLibraryError


def now():
    return datetime.now(timezone.utc).isoformat()


class ProjectLibraryService:
    def __init__(self, store, settings, *, files, portability=None, opener=None):
        self.store, self.settings, self.files = store, settings, files
        self.portability, self.opener = portability, opener

    def runtime(self):
        return self.files.runtime()

    def _require_configured(self):
        if not self.settings.library_root:
            raise ProjectLibraryError("Select a project library for this ConnLab instance before receiving projects.")

    def scan(self, roots):
        return self.files.scan(roots)

    def members(self, query="", batch_id=None):
        return {"items": [self._public(row, check_snapshot=False) for row in self.store.members(query, batch_id)]}

    def member(self, member_id):
        return self._public(self.store.member(member_id))

    def _public(self, row, *, check_snapshot=True):
        available, current = self.files.member_folder_available(row)
        warnings = []
        if not available:
            warnings.append("The folder is unavailable. Reconnect its location to browse files.")
        elif current != row["folder_path"]:
            warnings.append("This project was moved or renamed. Reconnect the verified location before continuing.")
        business_ready = True
        if available:
            try:
                business = self.files.workspace_business(row, self.store.workspace(row["project_id"]) if row["project_id"] else None, current)
                business_ready = business["ready"]
                if not business_ready:
                    warnings.append(business["warning"])
            except (OSError, ValueError):
                business_ready = False
                warnings.append("The registered project folder cannot be verified. Reconnect its location before continuing.")
        pending = self.files.pending_change(row["member_id"])
        if pending:
            warnings.append("A project location change needs recovery. Review its title or location to finish it.")
        portable = {"status": "not_checked", "created_at": None}
        if check_snapshot:
            portable = self.portability.status(row) if self.portability else {"status": "missing", "created_at": None}
        return {key: row[key] for key in ("member_id", "project_id", "ltr_number", "title", "folder_path", "revision", "batch_id")} | {
            "folder_path": current or row["folder_path"], "snapshot_status": portable["status"],
            "snapshot_created_at": portable.get("created_at"), "warnings": warnings,
            "is_history": row.get("is_history", False),
            "can_continue": bool(row["project_id"] and not row.get("is_history") and available and business_ready and current == row["folder_path"] and not pending)}

    def intake_plan(self, sources, assignments=()):
        self._require_configured()
        assignments = {item["source_path"]: item for item in assignments}
        members = self.store.members()
        numbers = self.store.project_numbers()
        rows = []
        for value in dict.fromkeys(sources):
            assignment = assignments.get(value, {})
            target_id = assignment.get("target_member_id")
            new_title = assignment.get("new_project_title")
            if target_id and new_title:
                raise ProjectLibraryError("Choose an existing project or a new project title, not both.")
            try:
                source = self.files.inspect_source(value)
                member = self.store.member(target_id) if target_id else None
                if member and member.get("is_history"):
                    raise ProjectLibraryConflict("Choose a working project for supplementary material; retained history is read-only.")
                target = self.files.suggested_target(source, new_title=new_title, target_member=member)
                status, warnings, separate = "ready", [], False
                workspace = self.store.workspace(source.get("project_id")) if source.get("project_id") else None
                reference_existing = bool(workspace and workspace["local_workspace_path"].casefold() == target.casefold()
                    and workspace["dl_number"] == source.get("ltr_number") and self.files.exists(target)
                    and self.files.same_content(source, target)
                    and not any(row["project_id"] == source.get("project_id") for row in members))
                if source["kind"] == "file" and not (target_id or new_title):
                    status = "conflict"
                    warnings.append("Assign this file to an existing project or explicitly name a new project to organize.")
                elif any(item["source_path"].casefold() == source["source_path"].casefold() for item in members) and not assignment:
                    received = next(item for item in members if item["source_path"].casefold() == source["source_path"].casefold())
                    if self.files.exists(received["folder_path"]) and self.files.same_content(source, received["folder_path"]):
                        status = "already_added"
                        warnings.append("The same project material is already received in the library.")
                    else:
                        status, separate = "conflict", True
                        warnings.append("This source or its working copy has changed since intake. Review and Keep Separate to preserve both versions.")
                elif reference_existing:
                    warnings.append("Register the existing working folder without copying its files or changing the official project location.")
                elif self.files.exists(target):
                    if self.files.same_content(source, target):
                        status = "already_added"
                        warnings.append("The same content is already at the destination.")
                    else:
                        status, separate = "conflict", True
                        warnings.append("The destination contains different content. Keep Separate preserves another version.")
                if source.get("ltr_number") and status != "already_added" and not target_id and not reference_existing and any(
                    str(item.get("ltr_number") or "").casefold() == source["ltr_number"].casefold()
                    for item in [*members, *numbers]
                ):
                    status, separate = "conflict", True
                    warnings.append("Another record shares this LTR. Review the source; no records will be merged.")
                if source.get("has_portable") and not reference_existing:
                    status, separate = "conflict", False
                    warnings.append("This project carries saved test data. Use Inspect and Restore Portable Project to preserve it; plain intake cannot create an empty replacement.")
                rows.append({**source, "target_path": target, "status": status, "warnings": warnings,
                             "can_keep_separate": separate, "target_member_id": target_id,
                             "new_project_title": new_title, "target_revision": member["revision"] if member else None, "reference_existing": reference_existing})
            except (OSError, ValueError, LookupError) as error:
                rows.append({"source_path": value, "target_path": "", "title": Path(value).name,
                             "ltr_number": None, "status": "unavailable", "warnings": [str(error)],
                             "can_keep_separate": False, "target_member_id": target_id, "new_project_title": new_title})
        for first in rows:
            for second in rows:
                if first is second or "entries" not in first or "entries" not in second:
                    continue
                a, b = Path(first["source_path"]), Path(second["source_path"])
                if a.is_relative_to(b):
                    first["status"], first["can_keep_separate"] = "conflict", False
                    first["warnings"].append("Selected project boundaries overlap. Choose one boundary before receiving.")
                elif first.get("ltr_number") and first["ltr_number"] == second.get("ltr_number") and not first.get("new_project_title") and not first.get("has_portable"):
                    first["status"], first["can_keep_separate"] = "conflict", True
                    first["warnings"].append("Another selected folder uses this LTR. Review and keep separate if appropriate.")
        plan = self.files.save_plan("intake", {"items": rows})
        keys = ("source_path", "target_path", "title", "ltr_number", "status", "warnings", "can_keep_separate", "target_member_id", "new_project_title")
        return {"plan_id": plan["plan_id"], "fingerprint": plan["fingerprint"],
                "items": [{key: row.get(key) for key in keys} for row in rows], "warnings": []}

    def create_batch(self, plan_id, fingerprint, selected, keep_separate=(), batch_id=None):
        self._require_configured()
        payload = self.files.plan(plan_id, fingerprint, "intake")
        lookup = {row["source_path"]: row for row in payload["items"]}
        if any(path not in lookup for path in selected):
            raise ProjectLibraryError("Select only sources from this review.")
        batch_id = batch_id or uuid4().hex
        intent = {"plan_id": plan_id, "fingerprint": fingerprint, "selected": sorted(set(selected)), "keep_separate": sorted(set(keep_separate))}
        try:
            previous = self.store.batch(batch_id)
        except LookupError:
            previous = None
        if previous is not None:
            if previous.get("intent") != intent:
                raise ProjectLibraryConflict("This batch identity belongs to a different confirmed request.")
            return self._run_batch(previous)
        batch = {"batch_id": batch_id, "status": "running", "groups": {}, "items": [], "counts": {}, "intent": intent}
        for path in dict.fromkeys(selected):
            source = lookup[path]
            separate = path in keep_separate
            member_id = source.get("target_member_id") or uuid4().hex
            group = source.get("new_project_title")
            if group:
                member_id = batch["groups"].setdefault(group, member_id)
            target = source["target_path"]
            if separate and self.files.exists(target):
                target = self.files.alternate(target, batch_id)
            batch["items"].append({"source_path": path, "status": "pending", "message": "", "member_id": None,
                                   "source": source, "target": target, "working_member_id": member_id,
                                   "keep_separate": separate, "phase": "planned"})
        batch = self.store.reserve_batch(batch)
        return self._run_batch(batch)

    def resume_batch(self, batch_id):
        return self._run_batch(self.store.batch(batch_id))

    def batch(self, batch_id):
        return self._batch_public(self.store.batch(batch_id))

    def _run_batch(self, batch):
        with self.files.lock():
            batch["status"] = "running"
            for index, item in enumerate(batch["items"]):
                if item["status"] in {"added", "already_added", "review"}:
                    continue
                source = item["source"]
                try:
                    if source["status"] == "already_added":
                        item.update(status="already_added", message="This source was already received.")
                    elif source["status"] == "unavailable":
                        item.update(status="failed", message=" ".join(source["warnings"]))
                    elif source["status"] == "conflict" and not (item["keep_separate"] and source["can_keep_separate"]):
                        item.update(status="review", message=" ".join(source["warnings"]))
                    else:
                        self._receive_item(batch, item, index)
                except (OSError, ValueError, LookupError) as error:
                    item.update(status="failed", message=str(error))
                self.store.save_batch(batch)
            batch["status"] = "interrupted" if any(row["status"] == "failed" for row in batch["items"]) else "completed"
            self.store.save_batch(batch)
        return self._batch_public(batch)

    def _receive_item(self, batch, item, index):
        source = item["source"]
        if source.get("has_portable") and not source.get("reference_existing"):
            raise ProjectLibraryConflict("Inspect and restore this project's carried test data instead of using plain intake.")
        if not self.files.source_unchanged(source):
            raise ProjectLibraryConflict("The source changed after review. Create a new intake review.")
        existing = source.get("target_member_id")
        if existing:
            member = self.store.member(existing)
            if member.get("is_history"):
                raise ProjectLibraryConflict("Retained history cannot receive supplementary material.")
            if member["revision"] != source["target_revision"]:
                raise ProjectLibraryConflict("The destination project changed. Review the intake again.")
        else:
            title = source.get("new_project_title") or source["title"]
            root = self.files.root_for_target(item["target"], source, bool(source.get("new_project_title")))
            project_id = source.get("project_id") if source.get("reference_existing") else None
            member = {"member_id": item["working_member_id"], "project_id": project_id,
                      "ltr_number": source.get("ltr_number"), "title": title, "folder_path": root,
                      "source_path": source["source_path"], "source_project_id": source.get("project_id"), "revision": 1, "batch_id": batch["batch_id"],
                      "created_at": now(), "snapshot_fingerprint": None}
            if source.get("new_project_title"):
                self.files.ensure_group(member)
        marker = self.files.marker(member["folder_path"]) if self.files.exists(member["folder_path"]) else None
        received = source.get("reference_existing") or self.files.exists(item["target"]) and marker and marker.get("member_id") == member["member_id"]
        if not received:
            item["phase"] = "copying"
            self.store.save_batch(batch)
            self.files.receive({**source, "member_marker": member if not existing else None},
                               item["target"], batch["batch_id"], str(index))
            item["phase"] = "copied"
            self.store.save_batch(batch)
        if not existing:
            try:
                member = self.store.member(member["member_id"])
            except LookupError:
                member = self.store.add_member(member)
                self.files.write_marker(member)
        item.update(status="added", message="Received and verified. Original source files remain unchanged.", member_id=member["member_id"])

    @staticmethod
    def _batch_public(batch):
        items = [{key: row[key] for key in ("source_path", "status", "message", "member_id")} for row in batch["items"]]
        return {"batch_id": batch["batch_id"], "status": batch["status"],
                "counts": {name: sum(row["status"] == status for row in items) for name, status in
                           (("added", "added"), ("already_added", "already_added"), ("review", "review"), ("failed", "failed"))},
                "items": items}

    def files_list(self, member_id, relative_path=""):
        row = self.store.member(member_id)
        available, folder = self.files.member_folder_available(row)
        if not available:
            return {"items": [], "warnings": ["The folder is unavailable. Reconnect its location."]}
        return self.files.listing(folder, relative_path)

    def open_folder(self, member_id):
        row = self.member(member_id)
        if not self.files.exists(row["folder_path"]):
            return {"status": "blocked", "message": "The folder is unavailable. Reconnect its location."}
        if self.opener:
            result = self.opener(row["folder_path"])
            if result is not None and hasattr(result, "status"):
                return {"status": result.status, "message": result.message}
        return {"status": "opened", "message": "Project folder opened."}

    def _pending_review(self, member_id, kind):
        state = self.files.pending_change(member_id)
        if not state:
            return None
        if state["strategy"] != kind:
            raise ProjectLibraryConflict("Finish the interrupted project location change before starting another.")
        effects = state["effects"]
        payload = effects["payload"]
        return {"plan_id": effects["plan_id"], "fingerprint": effects["fingerprint"],
                "source_path": payload["source_path"], "target_path": payload["target_path"],
                "warnings": ["An earlier location change was interrupted. Confirm to verify and finish it without moving another copy."]}

    def title_plan(self, member_id, title):
        pending = self._pending_review(member_id, "title")
        if pending:
            return pending
        row = self.store.member(member_id)
        if row.get("is_history"):
            raise ProjectLibraryConflict("Retained history does not allow changing its project title.")
        payload = self.files.title_context(row, title) | {"kind": "title"}
        if payload["source_path"] != payload["target_path"] and self.files.exists(payload["target_path"]):
            raise ProjectLibraryConflict("Another folder already uses the requested title.")
        plan = self.files.save_plan("title", payload)
        return {key: plan[key] for key in ("plan_id", "fingerprint")} | {key: payload[key] for key in ("source_path", "target_path")} | {"warnings": []}

    def location_plan(self, member_id, folder):
        pending = self._pending_review(member_id, "location")
        if pending:
            return pending
        member = self.store.member(member_id)
        payload = self.files.locate_context(member, folder, self.store.workspace(member["project_id"]) if member["project_id"] else None) | {"kind": "location"}
        for other in self.store.members():
            if other["member_id"] != member_id and self.files.overlap(other["folder_path"], payload["target_path"]):
                raise ProjectLibraryConflict("Another library entry already uses this location.")
        for workspace in self.store.workspaces():
            if workspace["project_id"] != member["project_id"] and self.files.overlap(workspace["local_workspace_path"], payload["target_path"]):
                raise ProjectLibraryConflict("This location overlaps another project's working folder.")
        plan = self.files.save_plan("location", payload)
        warnings = ["The identity marker is missing. Verify this folder belongs to the selected LTR and project before confirming; its marker will be rebuilt."] if payload["manual_identity_rebuild"] else []
        if payload.get("business_warning"):
            warnings.append(payload["business_warning"])
        return {key: plan[key] for key in ("plan_id", "fingerprint")} | {key: payload[key] for key in ("source_path", "target_path")} | {"warnings": warnings}

    def change(self, member_id, plan_id, fingerprint, kind):
        with self.files.lock():
            payload = self.files.plan(plan_id, fingerprint, kind)
            member = self.store.member(member_id)
            with self.files.project_lock(member["project_id"]):
                state = self.files.pending_change(member_id)
                if state:
                    effects = state["effects"]
                    if state["strategy"] != kind or effects["plan_id"] != plan_id or effects["fingerprint"] != fingerprint:
                        raise ProjectLibraryConflict("Finish the interrupted location change with its original review.")
                else:
                    if payload["member_id"] != member_id or not self.files.context_valid(member, payload):
                        raise ProjectLibraryConflict("The project changed. Review its location again.")
                    state = self.files.changes.create(member_id, kind, fingerprint)
                    state["status"] = "running"
                    state["effects"] = {"payload": payload, "plan_id": plan_id, "fingerprint": fingerprint, "phase": "reviewed"}
                    self.files.changes.save(state)
                old, target = payload["source_path"], payload["target_path"]
                phase = state["effects"]["phase"]
                if phase == "reviewed":
                    if kind == "title":
                        if self.files.exists(old):
                            self.files.move(old, target, payload["identity"])
                        elif not self.files.exists(target):
                            raise ProjectLibraryConflict("The interrupted folder move cannot be verified.")
                        elif self.files.path_identity(target) != payload["identity"]:
                            raise ProjectLibraryConflict("Another folder replaced the interrupted move.")
                    state["effects"]["phase"] = "moved"
                    self.files.changes.save(state)
                root = target if kind == "location" or member["folder_path"] == old else member["folder_path"]
                title = payload.get("title", member["title"])
                if state["effects"]["phase"] == "moved":
                    if member["revision"] == payload["revision"]:
                        business = Path(payload["business_target_path"]) if payload.get("business_target_path") else self.files.business_path({**member, "folder_path": root})
                        member = self.store.publish_move(member, old, target, root, title, str(business))
                    elif not (member["revision"] == payload["revision"] + 1 and member["folder_path"] == root and member["title"] == title):
                        raise ProjectLibraryConflict("The project changed during recovery. Review the retained copies.")
                    state["effects"]["phase"] = "indexed"
                    self.files.changes.save(state)
                workspace = self.store.workspace(member["project_id"]) if member["project_id"] else None
                if workspace:
                    self.files.publish_workspace_metadata(root, workspace)
                else:
                    self.files.rewrite_identity_metadata(root, old, target, member["project_id"])
                self.files.write_marker(member)
                state["status"] = "completed"
                state["effects"]["phase"] = "completed"
                self.files.changes.save(state)
                return self._public(self.store.member(member_id))

    def portable(self, member_id):
        return self.portability.status(self.store.member(member_id))

    def prepare(self, member_id, fingerprint):
        member = self.store.member(member_id)
        if member.get("is_history"):
            raise ProjectLibraryConflict("Retained history is a recovery reference, not the working project.")
        return self.portability.prepare(member, fingerprint)

    def restore_plan(self, folder, resolution=None):
        self._require_configured()
        return self.portability.restore_plan(folder, resolution)

    def restore(self, plan_id, fingerprint, resolution=None):
        self._require_configured()
        result = self.portability.restore(plan_id, fingerprint, resolution)
        return {**result, "member": self._public(result["member"])}

    def takeover_plan(self, member_id):
        member = self.store.member(member_id)
        warnings, blockers, missing = [], [], []
        if member.get("is_history"):
            blockers.append("This retained history is read-only. Resolve its project ownership before resuming tests.")
        if not member["project_id"] and self.files.has_portable(member["folder_path"]):
            blockers.append("This folder carries test-data metadata. Inspect and restore the portable project before continuing; an empty planning project would lose its history.")
        if not self.files.member_folder_available(member)[0]:
            blockers.append("Reconnect the project folder before taking it over.")
        existing_project = member.get("source_project_id") if self.store.project_exists(member.get("source_project_id")) else None
        if existing_project and any(row["member_id"] != member_id and row["project_id"] == existing_project for row in self.store.members()):
            blockers.append("Another library entry already manages this project. Reconnect that entry instead of creating a second working copy.")
        elif existing_project and not member["project_id"]:
            warnings.append("Confirming takeover switches the existing project to this received working copy. The original source is retained.")
        if not member["project_id"] and not existing_project:
            missing.extend(["Confirm Basic Information", "Review and confirm the test Matrix"])
            if member["ltr_number"]:
                warnings.append("The old LTR is retained as evidence; no public workbook is changed or number registered automatically.")
        existing_context = self.store.project_context(existing_project) if existing_project else None
        if existing_context and existing_context["registry_state"] != "active":
            blockers.append("The existing project is retained history or in Trash. Resolve its registry state before takeover.")
        payload = {"member_id": member_id, "revision": member["revision"], "project_id": member["project_id"], "existing_project_id": existing_project, "existing_context": self.files.digest(existing_context), "blockers": blockers}
        plan = self.files.save_plan("takeover", payload)
        return {"plan_id": plan["plan_id"], "fingerprint": plan["fingerprint"], "project_id": member["project_id"],
                "ltr_number": member["ltr_number"], "title": member["title"],
                "status": "conflict" if blockers else "already_managed" if member["project_id"] else "needs_information" if missing else "ready",
                "missing": missing, "warnings": warnings, "blockers": blockers}

    def takeover(self, member_id, plan_id, fingerprint):
        with self.files.lock():
            payload = self.files.plan(plan_id, fingerprint, "takeover")
            with self.files.project_lock(payload.get("existing_project_id") or payload.get("project_id")):
                member = self.store.member(member_id)
                if payload["member_id"] != member_id or payload["revision"] != member["revision"]:
                    raise ProjectLibraryConflict("The project changed. Review takeover again.")
                if not self.files.member_folder_available(member)[0]:
                    raise ProjectLibraryConflict("Reconnect the project folder before taking it over.")
                if payload.get("blockers"):
                    raise ProjectLibraryConflict(" ".join(payload["blockers"]))
                if not member["project_id"] and self.files.has_portable(member["folder_path"]):
                    raise ProjectLibraryConflict("Inspect and restore the carried test data before taking over this project.")
                if not member["project_id"]:
                    existing = payload.get("existing_project_id")
                    if existing and self.files.digest(self.store.project_context(existing)) != payload.get("existing_context"):
                        raise ProjectLibraryConflict("The existing project changed after review. Review takeover again.")
                    if existing:
                        self.files.locate_context(member, member["folder_path"], self.store.workspace(existing))
                        self.store.link_existing_project(member, existing)
                    else:
                        self.store.create_planning_project(member)
                    member = self.store.member(member_id)
                self.files.publish_workspace_metadata(member["folder_path"], self.store.workspace(member["project_id"]))
                self.files.write_marker(member)
                return {"member": self._public(member), "project_id": member["project_id"],
                        "warnings": ["Review missing project information before confirming test authority."] if not payload["project_id"] else []}
