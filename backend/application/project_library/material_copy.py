"""Explicit selected-file copying into an existing project, without adoption or recovery."""
from datetime import datetime, timezone
from uuid import uuid4
from backend.domain.project_library import ProjectLibraryConflict


class MaterialCopyService:
    def __init__(self, store, files, catalog, contexts):
        self.store, self.files, self.catalog, self.contexts = store, files, catalog, contexts

    def _entry(self, key, native=False):
        self.store.refresh()
        entries = self.catalog.catalog()
        entry = next((row for row in entries if row["key"] == key), None)
        if entry is None:
            raise LookupError("Material entry not found. Refresh the library.")
        if native and (not entry.get("project_id") or entry["source"] == "linked"):
            raise ValueError("Choose an existing ConnLab project as the copy destination.")
        if native and not self.catalog.copy_target_eligible(entry["project_id"]):
            raise ValueError("Open an active Project Workbench; retained temporary work cannot be a copy target.")
        if not entry["folder_path"] or not self.files.available(entry["folder_path"]):
            raise ValueError("Associate or locate the material folder before copying.")
        return {**entry, "available": True}

    def update_context(self, session_id, intent, project_id):
        def target():
            if project_id is None:
                return None
            entry = self._entry("project:" + project_id, native=True)
            return {**entry, "root_identity": self.files.root_identity(entry["folder_path"])}
        return self.contexts.update(session_id, intent, target)

    def _context_target(self, active):
        expected = active["target"]
        current = self._entry(expected["key"], native=True)
        if {**current, "root_identity": self.files.root_identity(current["folder_path"])} != expected:
            raise ProjectLibraryConflict("The Workbench target or its registered folder changed. Open that Workbench again.")
        return current

    def preview(self, source_key, relative_path, context, target_relative_directory="Reference materials"):
        with self.contexts.guard(context) as active, self.files.lock():
            source, target = self._entry(source_key), self._context_target(active)
            with self.files.project_lock(target["project_id"]):
                selected = self.files.selected_file(source["folder_path"], relative_path)
                batch_id = uuid4().hex
                prior = [item for batch in self.store.batches_for_target(target["folder_path"], target["key"])
                         for item in batch["items"] if item.get("status") in {"copied", "supplemented", "skipped"}]
                target_state, item = self.files.plan_selected_copy(source["folder_path"], selected,
                    target["folder_path"], target_relative_directory, batch_id, prior)
                payload = {"context": context, "context_intent": active["intent"], "batch_id": batch_id, "source": source, "target": target,
                    "selected": selected, "target_state": target_state, "items": [item],
                    "created_at": datetime.now(timezone.utc).isoformat()}
                plan = self.files.control.save_plan("material_copy", payload)
                return {"status": "ready", "plan_id": plan["plan_id"], "fingerprint": plan["fingerprint"],
                    "batch_id": batch_id, "source_key": source_key, "target_key": target["key"],
                    "source_path": source["folder_path"], "target_path": target["folder_path"],
                    "number": target.get("number") or "", "product_name": target["title"],
                    "supplement": True, "candidates": [], "items": [item]}

    def confirm(self, plan_id, fingerprint, context):
        with self.contexts.guard(context) as active, self.files.lock():
            plan = self.files.control.plan(plan_id, fingerprint, "material_copy")
            if plan.get("context") != context or self._context_target(active) != plan["target"]:
                raise ProjectLibraryConflict("The copy context changed. Preview the copy again from the target Workbench.")
            with self.files.project_lock(plan["target"]["project_id"]):
                return self._confirm(plan_id, fingerprint, plan)

    def _confirm(self, plan_id, fingerprint, plan):
        batch = self.store.batch(plan["batch_id"])
        if batch and batch["status"] == "completed":
            return batch
        source, target = self._entry(plan["source"]["key"]), self._entry(plan["target"]["key"], native=True)
        if source != plan["source"] or target != plan["target"]:
            raise ProjectLibraryConflict("The source or target registration changed. Preview the copy again.")
        if self.files.selected_file(source["folder_path"], plan["selected"]["relative_path"]) != plan["selected"]:
            raise ProjectLibraryConflict("The selected source changed. Preview the copy again.")
        self.files.check_root(target["folder_path"], plan["target_state"]["identity"])
        if batch is None:
            if self.files.snapshot(target["folder_path"]) != plan["target_state"]:
                raise ProjectLibraryConflict("The target changed after preview. Preview the copy again.")
            batch = {"copy_context": {"session_id": plan["context"]["session_id"], "intent": plan["context_intent"]}, "operation": "copy_file", "batch_id": plan["batch_id"], "plan_id": plan_id,
                "fingerprint": fingerprint, "status": "running", "target_key": target["key"],
                "target_path": target["folder_path"], "source_path": source["folder_path"],
                "created_at": plan["created_at"], "receipt_id": None, "counts": {}, "directory_counts": {}, "message": "",
                "items": [{**row, "status": "pending", "message": ""} for row in plan["items"]]}
            self.store.save_batch(batch)
        item = batch["items"][0]
        if item["status"] in {"copied", "supplemented", "skipped", "retained_changed"}:
            if not self.files.matches(target["folder_path"], item, plan["target_state"]["identity"]):
                item["status"], item["message"] = "retained_changed", "The copied file was edited or removed. It was retained as-is; preview again."
        else:
            try:
                item["status"] = self.files.publish(source["folder_path"], target["folder_path"], item, plan["target_state"]["identity"])
                item["message"] = ""
            except (OSError, ValueError) as error:
                item["status"], item["message"] = "failed", str(error)
        try:
            source_changed = self.files.selected_file(source["folder_path"], plan["selected"]["relative_path"]) != plan["selected"]
        except (OSError, ValueError):
            source_changed = True
        batch["message"] = "The source changed during copying. Preview again." if source_changed else ""
        batch["status"] = "incomplete" if source_changed or item["status"] in {"failed", "retained_changed"} else "completed"
        batch["counts"] = {status: int(item["status"] == status)
                           for status in ("copied", "supplemented", "skipped", "failed", "retained_changed")}
        self.store.save_batch(batch)
        return batch
