"""Explicit receipt of reference files, independent of project adoption and recovery."""
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from backend.domain.project_library import ProjectLibraryConflict


class MaterialReceiptService:
    def __init__(self, store, files, catalog, contexts=None):
        self.store, self.files, self.catalog = store, files, catalog
        from backend.application.project_library.copy_context import copy_contexts
        self.contexts = contexts if contexts is not None else copy_contexts

    def create_copy_context(self):
        return self.contexts.create()

    def update_copy_context(self, session_id, intent, project_id):
        from backend.application.project_library.material_copy import MaterialCopyService
        return MaterialCopyService(self.store, self.files, self.catalog, self.contexts).update_context(session_id, intent, project_id)

    def copy_preview(self, source_key, relative_path, context, target_relative_directory="Reference materials"):
        from backend.application.project_library.material_copy import MaterialCopyService
        return MaterialCopyService(self.store, self.files, self.catalog, self.contexts).preview(
            source_key, relative_path, context, target_relative_directory)

    def copy_confirm(self, plan_id, fingerprint, context):
        from backend.application.project_library.material_copy import MaterialCopyService
        return MaterialCopyService(self.store, self.files, self.catalog, self.contexts).confirm(plan_id, fingerprint, context)

    def _ensure_library_settings(self):
        config = self.store.settings()
        if config["root_path"]:
            return config
        with self.files.lock():
            self.store.refresh()
            config = self.store.settings()
            if not config["root_path"]:
                root = self.files.default_root()
                self._check_receive_ownership(str(root))
                root = self.files.root(root, create=True)
                config = self.store.configure(str(root))
            return config

    def runtime(self, ensure_default=False):
        config = self._ensure_library_settings() if ensure_default else self.store.settings()
        if not config["root_path"]:
            return {**config, "root_path": str(self.files.default_root()), "configured": False, "available": False}
        return {**config, "configured": bool(config["root_path"]),
                "available": bool(config["root_path"] and self.files.available(config["root_path"]))}

    def configure_root(self, path):
        with self.files.lock():
            current = self.store.settings()
            is_new = not current["root_path"] or str(Path(current["root_path"])) != str(Path(path))
            self._check_receive_ownership(str(Path(path).resolve()))
            root = str(self.files.root(path, create=is_new))
            self.store.configure(root)
        return self.runtime()

    def _check_receive_ownership(self, root, target=None, excluding_receipt=None):
        self.store.refresh()
        protected = [*self.store.protected_roots(excluding_receipt),
                     *[row["folder_path"] for row in self.catalog.catalog()
                       if row["folder_path"] and (excluding_receipt is None
                                                  or row.get("receipt_id") != excluding_receipt)]]
        # A top-level receive container may hold separate entries. It cannot itself
        # be inside an entry; each new destination must also be disjoint from them.
        if any(self.files.contains(path, root) or target and self.files.overlaps(target, path)
               for path in protected):
            raise ProjectLibraryConflict("Choose a Materials library folder separate from folders owned by existing entries or original sources.")

    def _candidates(self, number, target_key=""):
        self.store.refresh()
        candidates = []
        for entry in self.catalog.catalog():
            entry_number = entry.get("number") or ""
            same_number = bool(number and entry_number.casefold() == number.casefold())
            explicitly_unnumbered = not number and not entry_number and entry["key"] == target_key
            if not same_number and not explicitly_unnumbered:
                continue
            associated = bool(entry["folder_path"].strip())
            available = associated and self.files.available(entry["folder_path"])
            state = "unassociated" if not associated else "available" if available else "unavailable"
            reason = ("A material folder is not linked to this project yet." if not associated
                      else "The registered material location is unavailable. Locate it before supplementing."
                      if not available else "")
            if entry["source"] == "linked":
                reason = "Receive a managed copy first; linked original folders are read-only here."
            candidates.append({**entry, "available": available, "location_state": state,
                "can_supplement": entry["source"] != "linked" and available, "reason": reason})
        return candidates

    def preview(self, source, number="", product_name="", test_keywords="", target_key="", separate_description="", material_state=None):
        number = number.strip()
        if len(number) > 128:
            raise ValueError("The project number is too long.")
        if material_state not in {None, "completed", "ongoing"}:
            raise ValueError("Choose Completed or On-going for this materials entry.")
        product_name = product_name.strip() or Path(source).name
        if not product_name:
            raise ValueError("Enter a product name or description.")
        self._ensure_library_settings()
        with self.files.lock():
            binding = self.files.binding(self.store.settings())
            candidates = self._candidates(number, target_key)
            if candidates and not target_key:
                return {"status": "choose_target", "candidates": candidates, "number": number}
            candidate = next((row for row in candidates if row["key"] == target_key), None)
            if target_key not in {"", "new"} and candidate is None:
                raise ProjectLibraryConflict("The selected same-number entry changed. Check again.")
            if candidate and not candidate["can_supplement"]:
                raise ProjectLibraryConflict(candidate["reason"] or "Locate the managed target folder before supplementing it.")
            if candidates and target_key == "new" and not separate_description.strip():
                raise ValueError("Enter a distinguishing description for this independent same-number entry.")
            batch_id, receipt_id = uuid4().hex, uuid4().hex
            target = candidate["folder_path"] if candidate else self.files.proposed_target(
                binding["root_path"], number, source, separate_description)
            if not candidate:
                self._check_receive_ownership(binding["root_path"], target)
            prior = [entry for batch in self.store.batches_for_target(target, (candidate or {}).get("key"))
                     for entry in batch["items"] if entry.get("status") in {"copied", "supplemented", "skipped"}]
            source_state, target_state, entries = self.files.preview(source, target, batch_id,
                native=bool(candidate and candidate.get("project_id")), prior=prior)
            has_control_data = any(row["relative_path"].split("/")[0].casefold() == ".connlab" for row in entries)
            if has_control_data and material_state is None and not candidate:
                return {"status": "choose_state", "candidates": candidates,
                        "message": "This folder contains ConnLab files. Choose the materials state explicitly; stored data will only be copied, never restored."}
            payload = {"material_state": material_state or "completed", "batch_id": batch_id, "receipt_id": receipt_id, "binding": binding,
                "source_path": str(Path(source).resolve()), "target_path": target,
                "source_state": source_state, "target_state": target_state, "candidate": candidate,
                "number": number or None, "product_name": product_name,
                "test_keywords": test_keywords.strip(), "separate_description": separate_description.strip(),
                "items": entries, "created_at": datetime.now(timezone.utc).isoformat()}
            plan = self.files.save_plan(payload)
            return {"status": "ready", "batch_id": batch_id, "plan_id": plan["plan_id"], "fingerprint": plan["fingerprint"],
                "target_path": target, "source_path": payload["source_path"], "number": number,
                "product_name": candidate["title"] if candidate else product_name,
                "supplement": bool(candidate), "material_state": (candidate or {}).get("material_state") or payload["material_state"],
                "items": entries, "candidates": candidates}

    def _check_binding(self, plan, batch):
        if self.files.binding(self.store.settings()) != plan["binding"]:
            raise ProjectLibraryConflict("The Materials library folder changed. Preview again.")
        candidate = plan["candidate"]
        if not candidate:
            receipt_id = (batch or {}).get("receipt_id")
            if receipt_id:
                current = self.store.entry(receipt_id)
                expected = batch.get("receipt_binding")
                if (expected is not None and current != expected or expected is None and
                        (current["folder_path"] != plan["target_path"] or current["revision"] != 1)):
                    raise ProjectLibraryConflict("The received entry changed. Preview again before receiving more files.")
            self._check_receive_ownership(plan["binding"]["root_path"], plan["target_path"], receipt_id)
        if candidate:
            current = next((row for row in self._candidates(plan["number"], candidate["key"]) if row["key"] == candidate["key"]), None)
            if current != candidate:
                raise ProjectLibraryConflict("The selected entry changed or is unavailable. Preview again.")

    def confirm(self, plan_id, fingerprint):
        with self.files.lock():
            plan = self.files.plan(plan_id, fingerprint)
            with self.files.project_lock((plan["candidate"] or {}).get("project_id")):
                return self._confirm(plan_id, fingerprint, plan)

    def _confirm(self, plan_id, fingerprint, plan):
        batch = self.store.batch(plan["batch_id"])
        if batch and batch["status"] == "completed":
            return batch
        self._check_binding(plan, batch)
        if self.files.snapshot(plan["source_path"]) != plan["source_state"]:
            raise ProjectLibraryConflict("The source folder changed after preview. Preview again.")
        if batch is None:
            if self.files.snapshot(plan["target_path"]) != plan["target_state"]:
                raise ProjectLibraryConflict("The destination changed after preview. Preview again.")
            batch = {"batch_id": plan["batch_id"], "plan_id": plan_id, "fingerprint": fingerprint,
                "status": "running", "target_path": plan["target_path"], "source_path": plan["source_path"],
                "counts": {}, "directory_counts": {}, "message": "", "created_at": plan["created_at"],
                "receipt_id": (plan["candidate"] or {}).get("receipt_id"),
                "target_key": (plan["candidate"] or {}).get("key") or f"receipt:{plan['receipt_id']}",
                "root_identity": (plan["target_state"] or {}).get("identity"),
                "items": [{**entry, "status": "pending", "message": ""} for entry in plan["items"]]}
            self.store.save_batch(batch)
        if batch["root_identity"] is None:
            # An interrupted empty-directory creation is not permission to use an occupied path.
            try:
                batch["root_identity"] = self.files.create_root(plan["target_path"])
            except (OSError, ValueError) as error:
                batch["status"], batch["message"] = "incomplete", str(error)
                self.store.save_batch(batch)
                return batch
            self.store.save_batch(batch)
        self.files.check_root(batch["target_path"], batch["root_identity"])
        if not plan["candidate"]:
            entry_binding = self.store.add_entry({"receipt_id": plan["receipt_id"], "number": plan["number"],
                "product_name": plan["product_name"], "test_keywords": plan["test_keywords"],
                "folder_path": plan["target_path"], "source_path": plan["source_path"],
                "batch_id": batch["batch_id"], "created_at": plan["created_at"], "revision": 1,
                "description": plan["separate_description"], "material_state": plan["material_state"]})
            batch["receipt_id"] = plan["receipt_id"]
            batch["receipt_binding"] = entry_binding
            self.store.save_batch(batch)
        for entry in batch["items"]:
            if entry["status"] in {"copied", "supplemented", "skipped", "retained_changed"}:
                if not self.files.matches(plan["target_path"], entry, batch["root_identity"]):
                    entry["status"] = "retained_changed"
                    entry["message"] = "A previously received item was edited or removed. It was retained as-is; preview again to decide how to continue."
                elif entry["status"] == "retained_changed":
                    entry["status"], entry["message"] = "skipped", ""
                self.store.save_batch(batch)
                continue
            try:
                entry["status"] = self.files.publish(plan["source_path"], plan["target_path"], entry, batch["root_identity"])
                entry["message"] = ""
            except (OSError, ValueError) as error:
                entry["status"], entry["message"] = "failed", str(error)
            self.store.save_batch(batch)
        try:
            source_changed = self.files.snapshot(plan["source_path"]) != plan["source_state"]
        except (OSError, ValueError):
            source_changed = True
        batch["message"] = "The source changed during receipt. Preview again to include its latest contents." if source_changed else ""
        batch["status"] = "incomplete" if source_changed or any(row["status"] in {"failed", "retained_changed"} for row in batch["items"]) else "completed"
        batch["counts"] = {status: sum(row["status"] == status and not row["directory"] for row in batch["items"])
                           for status in ("copied", "supplemented", "skipped", "failed", "retained_changed")}
        batch["directory_counts"] = {status: sum(row["status"] == status and row["directory"] for row in batch["items"])
                                     for status in ("copied", "supplemented", "skipped", "failed", "retained_changed")}
        self.store.save_batch(batch)
        return batch

    def batch(self, batch_id):
        value = self.store.batch(batch_id)
        if value is None:
            raise LookupError("Receipt result not found.")
        return value

    def retry(self, batch_id, context=None):
        batch = self.batch(batch_id)
        if batch.get("operation") == "copy_file":
            return self.copy_confirm(batch["plan_id"], batch["fingerprint"], context)
        return self.confirm(batch["plan_id"], batch["fingerprint"])

    def catalog_history(self, key):
        self.store.refresh()
        catalog = self.catalog.catalog()
        entry = next((row for row in catalog if row["key"] == key), None)
        if entry is None and key.startswith("member:"):
            entry = next((row for row in catalog if row.get("member_id") == key.removeprefix("member:")), None)
        if entry is None:
            raise LookupError("Material entry not found. Refresh the library.")
        batches = self.store.batches_for_target(entry["folder_path"], entry["key"])
        return {"items": [{field: batch.get(field) for field in
                          ("batch_id", "status", "source_path", "created_at", "counts", "directory_counts")}
                          for batch in sorted(batches, key=lambda row: row["created_at"], reverse=True)]}

    def detail(self, receipt_id):
        entry = self.store.entry(receipt_id)
        history = self.store.batches_for_target(entry["folder_path"], f"receipt:{receipt_id}")
        return {**entry, "available": self.files.available(entry["folder_path"]),
                "batch": self.batch(entry["batch_id"]),
                "history": [{key: batch.get(key) for key in ("batch_id", "status", "source_path", "created_at", "counts", "directory_counts")}
                            for batch in history]}

    def edit(self, receipt_id, revision, product_name, test_keywords, material_state=None):
        if not product_name.strip():
            raise ValueError("Enter a product name or description.")
        if material_state not in {None, "completed", "ongoing"}:
            raise ValueError("Choose Completed or On-going.")
        with self.files.lock():
            changes = {"product_name": product_name.strip(), "test_keywords": test_keywords.strip()}
            if material_state is not None:
                changes["material_state"] = material_state
            self.store.edit_entry(receipt_id, revision, **changes)
            return self.detail(receipt_id)

    def locate_preview(self, receipt_id, folder):
        with self.files.lock():
            entry = self.store.entry(receipt_id)
            target = self.files.root(folder)
            self._check_location(entry, str(target))
            payload = {"entry": entry, "folder_path": str(target), "state": self.files.snapshot(target)}
            plan = self.files.control.save_plan("material_receipt_location", payload)
            return {"plan_id": plan["plan_id"], "fingerprint": plan["fingerprint"], "folder_path": str(target)}

    def locate(self, receipt_id, plan_id, fingerprint):
        with self.files.lock():
            payload = self.files.control.plan(plan_id, fingerprint, "material_receipt_location")
            if payload["entry"]["receipt_id"] != receipt_id or self.store.entry(receipt_id) != payload["entry"]:
                raise ProjectLibraryConflict("The entry changed. Locate it again.")
            self._check_location(payload["entry"], payload["folder_path"])
            if self.files.snapshot(payload["folder_path"]) != payload["state"]:
                raise ProjectLibraryConflict("The selected folder changed. Locate it again.")
            self.store.edit_entry(receipt_id, payload["entry"]["revision"], folder_path=payload["folder_path"])
            return self.detail(receipt_id)

    def _check_location(self, entry, target):
        self.store.refresh()
        protected = [entry["source_path"], *self.store.protected_roots(entry["receipt_id"]), *[row["folder_path"] for row in self.catalog.catalog()
            if row["key"] != f"receipt:{entry['receipt_id']}" and row["folder_path"]]]
        if any(self.files.overlaps(target, path) for path in protected):
            raise ProjectLibraryConflict("Choose the moved managed copy, not an original source or a folder owned by another entry.")

    def catalog_location_preview(self, key, folder):
        with self.files.lock():
            entry = self._unbound_entry(key)
            target = str(self.files.root(folder))
            self._check_member_location(entry, target)
            payload = {"entry": entry, "folder_path": target, "state": self.files.snapshot(target)}
            plan = self.files.control.save_plan("material_member_location", payload)
            return {"plan_id": plan["plan_id"], "fingerprint": plan["fingerprint"], "folder_path": target}

    def catalog_location(self, key, plan_id, fingerprint):
        with self.files.lock():
            payload = self.files.control.plan(plan_id, fingerprint, "material_member_location")
            entry = self._unbound_entry(key)
            if entry != payload["entry"]:
                raise ProjectLibraryConflict("The entry changed. Locate its folder again.")
            self._check_member_location(entry, payload["folder_path"])
            if self.files.snapshot(payload["folder_path"]) != payload["state"]:
                raise ProjectLibraryConflict("The folder changed. Locate it again.")
            return self.store.locate_unbound_member(key.removeprefix("member:"), entry, payload["folder_path"])

    def _unbound_entry(self, key):
        if not key.startswith("member:"):
            raise ValueError("Choose a received-only library entry.")
        return self.store.unbound_member(key.removeprefix("member:"))

    def _check_member_location(self, entry, target):
        self.store.refresh()
        protected = [entry["source_path"], *self.store.protected_roots(excluding_member=entry["key"].removeprefix("member:")),
                     *[row["folder_path"] for row in self.catalog.catalog()
                       if row["key"] != entry["key"] and row["folder_path"]]]
        if any(self.files.overlaps(target, path) for path in protected):
            raise ProjectLibraryConflict("Choose the moved managed copy, not an original source or another entry's folder.")
