"""Reviewed whole-project conflict choices and a recoverable working-copy switch.

Neither choice merges individual fields. A replacement keeps a verified portable
copy of the complete previous aggregate before switching its files and SQL graph.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import os
import shutil
from uuid import uuid4
from sqlalchemy import select, or_

from backend.domain.project_library import ProjectLibraryConflict, ProjectLibraryError
from backend.infrastructure.project_library.files import checked_path, read_json, atomic_json, fingerprint, now, inventory, copy_verified
from backend.infrastructure.project_library.assets import PortableAssets, SPECIAL_DATA_ROOTS, decode_rows
from backend.infrastructure.project_library.ownership import capture, table, TABLES, plain
from backend.infrastructure.storage.database import Base


def row_condition(model, row):
    keys = list(model.primary_key)
    if model.name == "report_authoring_revisions":
        keys = [model.c.project_id, model.c.revision]
    condition = None
    for column in keys:
        term = column == row[column.name]
        condition = term if condition is None else condition & term
    return condition


def validate_replace(connection, rows):
    """Reject inbound references from records outside the captured aggregate."""
    owned = {name: {tuple(record.get(column.name) for column in table(name).primary_key) for record in records}
             for name, records in rows.items()}
    for model in Base.metadata.tables.values():
        if model.name in {"project_library_members", "ltr_duplicate_resolution_tokens", "frozen_field_revision_requests"}:
            continue
        for constraint in model.foreign_key_constraints:
            elements = list(constraint.elements)
            parent_name = elements[0].column.table.name
            if parent_name not in rows:
                continue
            for parent in rows[parent_name]:
                condition = None
                for element in elements:
                    value = parent.get(element.column.name)
                    if value is None:
                        condition = None
                        break
                    term = element.parent == value
                    condition = term if condition is None else condition & term
                if condition is None:
                    continue
                for child in connection.execute(select(model).where(condition)).mappings():
                    key = tuple(child[column.name] for column in model.primary_key)
                    if model.name == "report_authoring_revisions":
                        belongs = any(child["project_id"] == row["project_id"] and child["revision"] == row["revision"] for row in rows.get(model.name, []))
                    else:
                        belongs = key in owned.get(model.name, set())
                    if not belongs:
                        raise ProjectLibraryConflict("Another project's records refer to this working revision (" + model.name + "). Resolve that relationship before replacing it.")

    semantic_links = {
        "confirmed_matrix_id": ("confirmed_matrix_versions", "confirmed_matrix_id"),
        "base_confirmed_matrix_id": ("confirmed_matrix_versions", "confirmed_matrix_id"),
        "base_report_revision_id": ("report_draft_revisions", "report_revision_id"),
        "source_package_id": ("intake_packages", "package_id"),
        "source_case_id": ("intake_cases", "case_id"),
        "source_draft_id": ("intake_drafts", "draft_id"),
        "source_intake_asset_id": ("intake_assets", "asset_id"),
        "pricing_draft_edit_id": ("fee_evaluation_pricing_draft_edits", "draft_edit_id"),
    }
    for model in Base.metadata.tables.values():
        for field, (parent, key) in semantic_links.items():
            ids = {row[key] for row in rows[parent]}
            if field not in model.c or not ids:
                continue
            for child in connection.execute(select(model).where(model.c[field].in_(ids))).mappings():
                identity = tuple(child[column.name] for column in model.primary_key)
                if identity not in owned.get(model.name, set()):
                    raise ProjectLibraryConflict("Another project's semantic references depend on this working revision (" + model.name + "). Resolve that relationship before replacement.")
    project_id = rows["projects"][0]["project_id"]
    source_ids = {row["asset_id"] for row in rows["file_assets"] + rows["intake_assets"]}
    model = table("project_temporary_contexts")
    for row in connection.execute(select(model).where(model.c.project_id != project_id)).mappings():
        if source_ids.intersection(json.loads(row["source_asset_ids_json"] or "[]")):
            raise ProjectLibraryConflict("Another project's source evidence depends on this revision.")
    model = table("report_authoring_revisions")
    matrix_ids = {row["confirmed_matrix_id"] for row in rows["confirmed_matrix_versions"]}
    for row in connection.execute(select(model).where(model.c.project_id != project_id)).mappings():
        payload = json.loads(row["payload_json"])
        if any(item.get("matrix_id") in matrix_ids for section in ("mappings", "results", "photos") for item in payload.get(section, [])):
            raise ProjectLibraryConflict("Another project's report evidence depends on this Matrix revision.")


def delete_owned(connection, rows, project_id):
    validate_replace(connection, rows)
    # Completed machine-local decisions are carried as non-replayable evidence in
    # the recovery packet. They must not remain effective after changing revision.
    for name in ("ltr_duplicate_resolution_tokens", "frozen_field_revision_requests"):
        model = Base.metadata.tables[name]
        condition = model.c.project_id == project_id if "project_id" in model.c else or_(model.c.current_project_id == project_id, model.c.existing_project_id == project_id)
        connection.execute(model.delete().where(condition))
    for name in reversed(list(rows)):
        model = table(name)
        for row in rows[name]:
            connection.execute(model.delete().where(row_condition(model, row)))


class RestoreConflicts:
    def __init__(self, portability):
        self.p = portability
        self.store, self.files, self.settings = portability.store, portability.files, portability.settings

    def _pending(self, project_id):
        directory = checked_path(self.files.root / "restores", must_exist=False)
        gate = self.files.pending_replacement_gate(project_id)
        gate_id = gate["effects"].get("library_restore", {}).get("plan_id") if gate else None
        matches = []
        for path in directory.glob("*.json") if directory.is_dir() else ():
            journal = read_json(checked_path(path))
            if journal.get("resolution") != "replace_working_copy" or journal.get("member", {}).get("project_id") != project_id:
                continue
            if journal.get("phase") in {"rolled_back", "completed"} and path.stem != gate_id:
                continue
            saved = read_json(self.files.plans / (path.stem + ".json"))
            payload = self.files.plan(path.stem, saved["fingerprint"], "restore")
            self._validate_journal(journal, payload, path.stem)
            matches.append({"plan_id": path.stem, "fingerprint": saved["fingerprint"], "journal": journal, "payload": payload})
        if gate_id and not any(item["plan_id"] == gate_id for item in matches):
            raise ProjectLibraryConflict("The interrupted replacement journal cannot be verified. The project writer remains blocked.")
        if len(matches) > 1:
            raise ProjectLibraryConflict("Multiple interrupted replacements require review before this project can continue.")
        return matches[0] if matches else None

    def _validate_journal(self, journal, payload, plan_id):
        backup = Path(payload["backup_path"])
        member, recovery = journal["member"], journal["backup_member"]
        if (payload.get("resolution") != "replace_working_copy" or member["project_id"] != payload["project_id"]
                or member["member_id"] != payload["target_member_id"] or journal["target_path"] != payload["target_path"]
                or recovery["folder_path"] != str(backup) or Path(journal["old_folder"]) != backup.parent / "previous-working-folder"
                or Path(journal["staging"]) != self.settings.projects_dir / (".connlab-restore-" + plan_id)):
            raise ProjectLibraryConflict("The interrupted replacement ownership or locations do not match its immutable review.")
        if not checked_path(backup).is_relative_to(self.files.recovery_root()):
            raise ProjectLibraryConflict("The recovery packet is outside this library's recovery storage.")
        for entry in journal.get("asset_moves", []):
            if not any(Path(entry["source"]) == self.settings.data_dir / name / sha256(member["project_id"].encode()).hexdigest()
                       and Path(entry["backup"]) == backup.parent / "runtime-assets" / name for name in SPECIAL_DATA_ROOTS):
                raise ProjectLibraryConflict("The interrupted asset move is outside its project partition.")
        packet = self.p._read_snapshot(backup)
        self.p._verify_files(backup, packet)
        if packet["source_signature"] != payload["target_signature"] or packet["member_id"] != recovery["member_id"]:
            raise ProjectLibraryConflict("The original complete recovery packet does not match the interrupted replacement.")
        return packet

    def _validate_uncommitted_site(self, journal, payload, body):
        original = self._validate_journal(journal, payload, Path(journal.get("staging", "")).name.removeprefix(".connlab-restore-"))
        current_rows = capture(self.store.session, payload["project_id"])
        original_rows = decode_rows(original["rows"], self.settings, Path(payload["target_path"]))
        def comparable(rows):
            rows = deepcopy(rows)
            for row in rows.get("project_official_workspace_records", []):
                row.pop("template_source_path", None)
            self._disable_permissions(rows)
            for records in rows.values():
                for row in records:
                    for key, value in list(row.items()):
                        if key.endswith("_json") and value:
                            row[key] = json.loads(value)
            return {name: sorted(records, key=fingerprint) for name, records in rows.items()}
        if comparable(current_rows) != comparable(original_rows):
            raise ProjectLibraryConflict("Project data changed after the interrupted replacement. The original complete recovery packet and both file locations were preserved; review the conflict before continuing.")
        target = Path(journal["target_path"])
        old = Path(journal["old_folder"])
        if not old.exists() and journal.get("phase") in {"old_moved", "swapped"}:
            try:
                self.p._verify_files(target, original)
            except (OSError, ValueError) as error:
                raise ProjectLibraryConflict("The original working folder is unavailable and the current scene is not a verified rollback. The registered complete recovery packet and current files were preserved.") from error
        if old.exists() and target.exists():
            marker = self.files.marker(target)
            if not marker or marker.get("member_id") != journal["member"]["member_id"] or marker.get("project_id") != payload["project_id"]:
                raise ProjectLibraryConflict("The interrupted destination now has a foreign project identity. All locations were preserved.")
            try:
                self.p._verify_files(target, body)
            except (OSError, ValueError) as error:
                raise ProjectLibraryConflict("Files changed after the interrupted replacement. Preserve the new material before recovery; the original complete recovery packet remains available.") from error

    def _review_pending(self, folder, body, resolution, pending):
        old, journal = pending["payload"], pending["journal"]
        if body["source_signature"] != old["source_signature"]:
            raise ProjectLibraryConflict("A replacement from a different source revision is unfinished. Review the original portable revision; its complete target recovery packet was preserved.")
        try:
            committed = self.store.batch("restore_" + pending["plan_id"]).get("committed")
        except LookupError:
            committed = False
        if not committed:
            self._validate_uncommitted_site(journal, old, body)
        if resolution not in (None, "replace_working_copy"):
            raise ProjectLibraryConflict("Finish the interrupted working-copy replacement before choosing another conflict resolution.")
        status = "ready" if resolution else "conflict"
        blockers = []
        warnings = ["This review resumes the original replacement and keeps its already verified complete recovery point."]
        if not resolution:
            warnings.append("A working-copy replacement is unfinished. Review and confirm its existing recovery operation.")
        extras = {"resolution_options": ["replace_working_copy"], "resolution": resolution, "target_revision": old["target_revision"],
                  "backup_path": old["backup_path"], "source_signature": old["source_signature"]}
        payload = {**old, **extras, "source_path": folder, "status": status, "blockers": blockers,
                   "pending_replacement_id": pending["plan_id"], "pending_fingerprint": pending["fingerprint"]}
        saved = self.files.save_plan("restore", payload)
        return {"plan_id": saved["plan_id"], "fingerprint": saved["fingerprint"], "project_id": body["project_id"], "ltr_number": body["ltr_number"], "title": body["title"],
                "source_path": folder, "target_path": old["target_path"], "status": status, "created_at": body["created_at"],
                "record_counts": {name: len(rows) for name, rows in body["rows"].items()}, "file_count": sum(not row["directory"] for row in body["files"]),
                "warnings": warnings, "blockers": blockers, **extras}

    def plan(self, folder, resolution):
        folder = str(checked_path(folder))
        extra = {"resolution_options": [], "resolution": resolution, "target_revision": None, "backup_path": None, "source_signature": None}
        try:
            body = self.p._read_snapshot(folder)
            self.p._verify_files(folder, body)
            pending = self._pending(body["project_id"])
            if pending:
                extra["backup_path"] = pending["payload"]["backup_path"]
                return self._review_pending(folder, body, resolution, pending)
            target = str(self.settings.projects_dir / Path(folder).name)
            blockers, warnings, options = [], list(body.get("warnings", [])), []
            existing = next((row for row in self.store.members() if row["project_id"] == body["project_id"]), None)
            target_signature = None
            recovery = None if existing else self.p.pending_receive(body)
            if recovery:
                target = recovery["target_path"]
            if existing:
                current, _ = self.p._capture(existing)
                target_signature = fingerprint(current)
                if self.p._matches_snapshot(current, body):
                    status, target = "already_added", existing["folder_path"]
                else:
                    status, target, options = "conflict", existing["folder_path"], ["replace_working_copy", "keep_as_history"]
                    warnings.append("This project has a different working revision. Select how to retain the two copies.")
            elif self.store.project_exists(body["project_id"]):
                status = "conflict"
                blockers.append("Register the existing project's current working folder before reviewing replacement; its recovery point must be complete.")
            else:
                status = "ready"
                numbers = [row for row in self.store.project_numbers() if row["is_current_owner"] and row["status"] == "registered" and body["ltr_number"] and row["ltr_number"].casefold() == body["ltr_number"].casefold() and row["project_id"] != body["project_id"]]
                if numbers:
                    status, options = "conflict", ["keep_as_history"]
                    warnings.append("Another project owns this LTR. Retain the source as history without changing the current owner.")
                elif recovery:
                    warnings.append("A verified earlier receive was interrupted. Confirm this fresh review to finish its working-project restoration without copying or discarding it.")
                elif self.files.exists(target):
                    status, options = "conflict", ["keep_as_history"]
                    warnings.append("The destination is occupied. A retained history copy uses a separate destination.")
            self.p._check_existing_keys(body["rows"])
            extra.update(resolution_options=options, source_signature=body["source_signature"], target_revision=existing["revision"] if existing else None)
            backup = None
            if resolution:
                if resolution not in options:
                    raise ProjectLibraryConflict("This resolution is not available for the reviewed conflict.")
                if resolution == "replace_working_copy":
                    rows = capture(self.store.session, body["project_id"])
                    validate_replace(self.store.session.connection(), rows)
                    self.store.session.rollback()
                    backup = self.files.recovery_root() / uuid4().hex / Path(target).name
                    warnings.append("The complete current project and its saved test data will be retained at the recovery point before switching this working copy.")
                else:
                    target = str(self.settings.projects_dir / (Path(folder).name + " [history " + uuid4().hex[:8] + "]"))
                    warnings.append("This source will be retained as read-only history. The target's current project and LTR owner remain unchanged.")
                status, blockers = "ready", []
            extra["backup_path"] = str(backup) if backup else None
            payload = {"source_path": folder, "target_path": target, "source_signature": body["source_signature"], "project_id": body["project_id"], "status": status, "blockers": blockers, **extra,
                       "target_member_id": existing["member_id"] if existing else None, "target_signature": target_signature,
                       "owner_state": self.p.owner_state(body), "recovery_plan_id": recovery["plan_id"] if recovery else None}
            saved = self.files.save_plan("restore", payload)
            return {"plan_id": saved["plan_id"], "fingerprint": saved["fingerprint"], "project_id": body["project_id"], "ltr_number": body["ltr_number"], "title": body["title"], "source_path": folder, "target_path": target, "status": status, "created_at": body["created_at"], "record_counts": {name: len(records) for name, records in body["rows"].items()}, "file_count": sum(not row["directory"] for row in body["files"]), "warnings": warnings, "blockers": blockers, **extra}
        except (OSError, ValueError, LookupError) as error:
            saved = self.files.save_plan("restore", {"source_path": folder, "target_path": "", "status": "unavailable", "blockers": [str(error)], "resolution": resolution})
            return {"plan_id": saved["plan_id"], "fingerprint": saved["fingerprint"], "project_id": None, "ltr_number": None, "title": Path(folder).name, "source_path": folder, "target_path": "", "status": "unavailable", "created_at": None, "record_counts": {}, "file_count": 0, "warnings": [], "blockers": [str(error)], **extra}

    def restore(self, payload, plan_id):
        recovery_id = payload.get("pending_replacement_id") or plan_id
        with self.files.project_lock(payload["project_id"], restore_id=recovery_id):
            if payload.get("pending_replacement_id"):
                original = self.files.plan(recovery_id, payload["pending_fingerprint"], "restore")
                if original["project_id"] != payload["project_id"] or original["source_signature"] != payload["source_signature"]:
                    raise ProjectLibraryConflict("The interrupted replacement differs from this review.")
                payload = {**original, "source_path": payload["source_path"]}
            return self._restore_locked(payload, recovery_id)

    def _restore_locked(self, payload, plan_id):
        if payload["status"] != "ready":
            raise ProjectLibraryConflict(" ".join(payload["blockers"]))
        body = self.p._read_snapshot(payload["source_path"])
        self.p._verify_files(payload["source_path"], body)
        if body["source_signature"] != payload["source_signature"]:
            raise ProjectLibraryConflict("The source changed after review.")
        journal_path = self.files.root / "restores" / (plan_id + ".json")
        journal = read_json(journal_path) if journal_path.is_file() else None
        if journal:
            try:
                committed = self.store.batch("restore_" + plan_id).get("committed")
            except LookupError:
                committed = False
            if committed:
                return self._finish(journal, journal_path, body)
            if journal.get("resolution") == "replace_working_copy":
                self._validate_uncommitted_site(journal, payload, body)
            source_is_current = Path(payload["source_path"]) == Path(journal["target_path"])
            self._rollback_files(journal)
            if source_is_current and journal.get("incoming_retained_path"):
                payload = {**payload, "source_path": journal["incoming_retained_path"]}
            journal["phase"] = "rolled_back"
            atomic_json(journal_path, journal)
            self.files.release_replacement_fence(payload["project_id"], plan_id)
        if self.p.owner_state(body) != payload["owner_state"]:
            raise ProjectLibraryConflict("LTR ownership changed. Review this restore again.")
        if payload["resolution"] == "replace_working_copy":
            return self._replace(payload, plan_id, body, journal_path, journal)
        return self._history(payload, plan_id, body, journal_path, journal)

    def _member(self, body, folder, member_id=None, *, recovery=False):
        return {"member_id": member_id or uuid4().hex, "project_id": None if recovery else body["project_id"], "ltr_number": body["ltr_number"], "title": body["title"], "folder_path": str(folder), "source_path": str(folder), "source_project_id": body["project_id"], "revision": 1, "batch_id": None, "created_at": now(), "disposition": "recovery" if recovery else "working", "snapshot_fingerprint": body["source_signature"]}

    def _receive(self, source, target, member, plan_id):
        if self.files.exists(target):
            raise ProjectLibraryConflict("The reviewed restore destination is now occupied.")
        descriptor = self.files.inspect_source(source)
        descriptor["member_marker"] = {key: member[key] for key in ("member_id", "project_id", "ltr_number")}
        self.files.receive(descriptor, str(target), plan_id, "conflict-copy")

    def _history(self, payload, plan_id, body, journal_path, old_journal):
        same_identity = self.store.project_exists(body["project_id"])
        member = self._member(body, payload["target_path"], recovery=same_identity)
        journal = {"phase": "copying", "target_path": member["folder_path"], "member": member, "backup_member": None, "resolution": "keep_as_history"}
        atomic_json(journal_path, journal)
        self._receive(payload["source_path"], member["folder_path"], member, plan_id)
        self.p._verify_files(member["folder_path"], body)
        if same_identity:
            # Same UUID history is an immutable complete packet, not a second
            # SQL working owner. Its original graph can be restored elsewhere.
            self.p._insert({}, member, operation_id=plan_id)
        else:
            PortableAssets.restore_assets(Path(member["folder_path"]), body["assets"], self.settings, body["project_id"])
            rows = decode_rows(body["rows"], self.settings, Path(member["folder_path"]))
            rows["projects"][0]["registry_state"] = "history"
            for row in rows["ltr_records"]:
                row["is_current_owner"] = False
            self._disable_permissions(rows)
            self.p._insert(rows, member, operation_id=plan_id)
        return self._finish(journal, journal_path, body)

    def _replace(self, payload, plan_id, body, journal_path, previous):
        member = self.store.member(payload["target_member_id"])
        current, _ = self.p._capture(member)
        if member["revision"] != payload["target_revision"] or fingerprint(current) != payload["target_signature"]:
            raise ProjectLibraryConflict("The target working revision changed. Review replacement again.")
        old_rows = capture(self.store.session, member["project_id"])
        validate_replace(self.store.session.connection(), old_rows)
        self.store.session.rollback()
        backup_path = checked_path(payload["backup_path"], must_exist=False)
        recovery_id = previous["backup_member"]["member_id"] if previous else uuid4().hex
        recovery = self._member({**current, "source_signature": fingerprint(current)}, backup_path, recovery_id, recovery=True)
        # Prepare a complete immutable recovery packet without changing the target
        # member revision; final SQL publication remains one transaction below.
        if not backup_path.exists():
            self.p.prepare(member, fingerprint(current), locked=True, persist_member=False)
            member = self.store.member(member["member_id"])
            copy_verified(Path(member["folder_path"]), backup_path, inventory(member["folder_path"]))
            packet = read_json(backup_path / ".connlab/portable/snapshot.json")
            packet["body"]["member_id"] = recovery_id
            atomic_json(backup_path / ".connlab/portable/snapshot.json", {"body": packet["body"], "checksum": fingerprint(packet["body"])})
            self.files.write_marker(recovery)
        backup_body = self.p._read_snapshot(backup_path)
        self.p._verify_files(backup_path, backup_body)
        if backup_body["source_signature"] != payload["target_signature"]:
            raise ProjectLibraryConflict("The target recovery copy does not match the reviewed revision.")
        self._register_recovery(recovery)
        replacement = self._member(body, member["folder_path"], member["member_id"])
        replacement["revision"] = member["revision"] + 1
        staging = self.settings.projects_dir / (".connlab-restore-" + plan_id)
        old_folder = backup_path.parent / "previous-working-folder"
        journal = {"phase": "copying", "target_path": member["folder_path"], "staging": str(staging), "old_folder": str(old_folder), "member": replacement, "backup_member": recovery, "resolution": "replace_working_copy", "asset_moves": []}
        atomic_json(journal_path, journal)
        try:
            self._receive(payload["source_path"], staging, replacement, plan_id)
            self.p._verify_files(staging, body)
            before_switch, _ = self.p._capture(member)
            if fingerprint(before_switch) != payload["target_signature"]:
                raise ProjectLibraryConflict("The target files changed while preparing the recovery point. Review replacement again.")
            self.files.fence_replacement(body["project_id"], plan_id)
            for name in SPECIAL_DATA_ROOTS:
                original = self.settings.data_dir / name / sha256(body["project_id"].encode()).hexdigest()
                saved = backup_path.parent / "runtime-assets" / name
                if original.exists():
                    checked_path(original)
                    saved.parent.mkdir(parents=True, exist_ok=True)
                    journal["asset_moves"].append({"source": str(original), "backup": str(saved)})
                    atomic_json(journal_path, journal)
                    os.rename(original, saved)
            os.rename(member["folder_path"], old_folder)
            journal["phase"] = "old_moved"
            atomic_json(journal_path, journal)
            os.rename(staging, member["folder_path"])
            journal["phase"] = "swapped"
            atomic_json(journal_path, journal)
            PortableAssets.restore_assets(Path(member["folder_path"]), body["assets"], self.settings, body["project_id"])
            rows = decode_rows(body["rows"], self.settings, Path(member["folder_path"]))
            self._disable_permissions(rows)
            self.p._insert(rows, replacement, replace_rows=old_rows, recovery_member=recovery, operation_id=plan_id)
        except Exception:
            try:
                committed = self.store.batch("restore_" + plan_id).get("committed")
            except LookupError:
                committed = False
            if committed:
                raise
            self._rollback_files(journal)
            journal["phase"] = "rolled_back"
            atomic_json(journal_path, journal)
            self.files.release_replacement_fence(body["project_id"], plan_id)
            raise
        return self._finish(journal, journal_path, body)

    def _register_recovery(self, recovery):
        try:
            current = self.store.member(recovery["member_id"])
        except LookupError:
            self.store.add_member(recovery)
            return
        if current["folder_path"] != recovery["folder_path"] or current["source_project_id"] != recovery["source_project_id"] or current.get("disposition") != "recovery":
            raise ProjectLibraryConflict("The original recovery point registration changed. It was not overwritten.")

    @staticmethod
    def _disable_permissions(rows):
        for row in rows.get("project_public_folder_workflow_states", []):
            row["auto_sync_enabled"], row["sync_locked"] = False, False

    def _rollback_files(self, journal):
        target = checked_path(journal["target_path"], must_exist=False)
        old = Path(journal["old_folder"]) if journal.get("old_folder") else None
        if old and old.exists():
            if target.exists():
                marker = self.files.marker(target)
                if not marker or marker.get("member_id") != journal["member"]["member_id"]:
                    raise ProjectLibraryConflict("The interrupted restore destination has another identity. Its recovery point was retained.")
                checked_path(target)
                inventory(target)
                evidence = old.parent / ("interrupted-incoming-" + uuid4().hex)
                os.rename(target, evidence)
                journal["incoming_retained_path"] = str(evidence)
                journal.setdefault("retained_locations", []).append(str(evidence))
            os.rename(old, target)
        if not old and target.exists():
            marker = self.files.marker(target)
            if not marker or marker.get("member_id") != journal["member"]["member_id"]:
                raise ProjectLibraryConflict("The interrupted history destination now has another identity.")
            inventory(target)
            shutil.rmtree(target)
        staging = Path(journal["staging"]) if journal.get("staging") else None
        if staging and staging.exists():
            checked_path(staging)
            inventory(staging)
            if old:
                evidence = old.parent / ("interrupted-staging-" + uuid4().hex)
                os.rename(staging, evidence)
                journal.setdefault("retained_locations", []).append(str(evidence))
            else:
                shutil.rmtree(staging)
        for entry in reversed(journal.get("asset_moves", [])):
            original, saved = Path(entry["source"]), Path(entry["backup"])
            if saved.exists():
                checked_path(saved)
                if original.exists():
                    checked_path(original)
                    inventory(original)
                    shutil.rmtree(original)
                original.parent.mkdir(parents=True, exist_ok=True)
                os.rename(saved, original)

    def _finish(self, journal, journal_path, body):
        member = self.store.member(journal["member"]["member_id"])
        self.files.write_marker(member)
        if member["project_id"]:
            # Official metadata is path-only and is derived from the restored rows.
            workspace = self.store.workspace(member["project_id"])
            if workspace:
                self.files.publish_workspace_metadata(member["folder_path"], workspace)
        journal["phase"] = "completed"
        atomic_json(journal_path, journal)
        self.files.release_replacement_fence(journal["member"].get("project_id"), journal_path.stem)
        return {"status": "history_kept" if journal["resolution"] == "keep_as_history" else "restored", "member": member,
                "backup_member_id": journal["backup_member"]["member_id"] if journal.get("backup_member") else None,
                "warnings": ["The complete previous working revision is retained as a recovery point."] if journal.get("backup_member") else body.get("warnings", [])}
