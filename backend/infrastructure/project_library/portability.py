"""Versioned project snapshots with explicit graph and asset restore.

Snapshots contain one project aggregate, not an executable SQL script or a copy
of the machine database. Source paths are provenance; only bound portable paths
can become target file locations.
"""
from contextlib import nullcontext
from datetime import date, datetime
from hashlib import sha256
import json
from pathlib import Path
import re
from uuid import uuid4
from sqlalchemy import select, inspect
from sqlalchemy.exc import IntegrityError

from backend.domain.project_library import ProjectLibraryError, ProjectLibraryConflict
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.project_library.files import (
    PORTABLE_FILE, SOFTWARE_MARKER, atomic_json, read_json, fingerprint, now,
    checked_path, inventory, file_hash,
)
from backend.infrastructure.project_library.assets import PortableAssets, project_inventory, decode_rows, decode_path
from backend.infrastructure.project_library.ownership import capture, table, TABLES, validate_relations, typed_record
from backend.infrastructure.storage.models_project_library import ProjectLibraryMemberModel
from backend.infrastructure.storage.database import Base


class ProjectPortability:
    def __init__(self, store, files, settings):
        self.store, self.files, self.settings = store, files, settings

    def _capture(self, member):
        if not member["project_id"]:
            raise ProjectLibraryError("Take over this project before preparing test-data portability.")
        root = checked_path(member["folder_path"])
        journal_history = []
        for name in ("project_folder_generation", "official_folder_relocation", "llcr_cr_record_publication", "ir_dwv_record_publication"):
            journal = GenerationJournal(self.settings.data_dir / name)
            state = journal.read(member["project_id"])
            if state and state.get("status") != "completed":
                raise ProjectLibraryConflict("Finish the interrupted project operation before preparing a portable snapshot.")
            if state:
                journal_history.append({"kind": name, "operation_id": state["operation_id"], "status": "completed",
                                        "completed_steps": state.get("completed_steps", []), "source_provenance_only": True})
        rows = capture(self.store.session, member["project_id"])
        pending = [row for row in rows["project_public_folder_workflow_operations"] if row.get("status") not in {"completed", "cancelled"}]
        if pending:
            raise ProjectLibraryConflict("Resolve the unfinished public-folder operation before preparing this project.")
        journal_history.extend(self._operation_evidence(member))
        inherited = Path(member["folder_path"]) / PORTABLE_FILE
        if inherited.is_file():
            previous = read_json(inherited)
            if isinstance(previous, dict) and isinstance(previous.get("body"), dict) and previous.get("checksum") == fingerprint(previous["body"]):
                journal_history.extend(previous["body"].get("operation_history", []))
        permission_history = [item for item in journal_history if item.get("kind") == "public_permission"]
        for state in rows["project_public_folder_workflow_states"]:
            if not permission_history:
                journal_history.append({"kind": "public_permission", "project_id": member["project_id"], "source_auto_sync_enabled": bool(state.get("auto_sync_enabled")), "target_permission": False})
            state["auto_sync_enabled"] = False
            state["sync_locked"] = False
        journal_history = sorted({fingerprint(item): item for item in journal_history}.values(), key=fingerprint)
        assets = PortableAssets(self.settings, member)
        encoded_rows = assets.encode(rows)
        encoded_rows = {name: sorted(records, key=lambda row: json.dumps(row, sort_keys=True, ensure_ascii=False)) for name, records in encoded_rows.items()}
        content = {"project_id": member["project_id"], "ltr_number": member["ltr_number"], "title": member["title"],
                   "rows": encoded_rows, "files": project_inventory(root), "assets": assets.descriptors(),
                   "operation_history": journal_history}
        return content, assets

    def _operation_evidence(self, member):
        session = self.store.session
        project_id = member["project_id"]
        result = []
        token_table = Base.metadata.tables["ltr_duplicate_resolution_tokens"]
        for row in session.execute(select(token_table).where((token_table.c.current_project_id == project_id) | (token_table.c.existing_project_id == project_id))).mappings():
            record = dict(row)
            token_id = record.pop("token_id")
            record["token_reference"] = sha256(token_id.encode()).hexdigest()
            result.append({"kind": "ltr_decision_evidence", "source_record": record, "replayable": False})
        request_table = Base.metadata.tables["frozen_field_revision_requests"]
        for row in session.execute(select(request_table).where(request_table.c.project_id == project_id)).mappings():
            record = dict(row)
            if record["status"] not in {"completed", "applied", "rejected", "cancelled"}:
                raise ProjectLibraryConflict("Finish the pending business-field decision before preparing this project.")
            result.append({"kind": "frozen_field_decision_evidence", "source_record": record, "replayable": False})
        session.rollback()
        return result

    def status(self, member):
        result = {"status": "missing", "fingerprint": "", "created_at": None, "format_version": 1,
                  "record_counts": {}, "file_count": 0, "warnings": [], "blockers": []}
        try:
            if member.get("disposition") == "recovery":
                body = self._read_snapshot(member["folder_path"])
                self._verify_files(member["folder_path"], body)
                return {**result, "status": "current", "fingerprint": body["source_signature"], "created_at": body["created_at"],
                        "record_counts": {key: len(value) for key, value in body["rows"].items()},
                        "file_count": sum(not item["directory"] for item in body["files"]),
                        "warnings": ["This retained recovery packet is not the active working project."]}
            current, assets = self._capture(member)
            signature = fingerprint(current)
            result.update(fingerprint=signature, record_counts={key: len(value) for key, value in current["rows"].items()},
                          file_count=sum(not item["directory"] for item in current["files"]), warnings=sorted(set(assets.warnings)))
            path = Path(member["folder_path"]) / PORTABLE_FILE
            if path.is_file():
                body = self._read_snapshot(member["folder_path"])
                result["created_at"] = body["created_at"]
                result["status"] = "current" if signature == body["source_signature"] else "stale"
                result["record_counts"] = {key: len(value) for key, value in body["rows"].items()}
                result["file_count"] = sum(not item["directory"] for item in body["files"])
                if result["status"] == "stale":
                    result["warnings"].append("The saved snapshot does not include the latest project changes. Prepare it again before taking this project away.")
        except (OSError, ValueError, LookupError) as error:
            result.update(status="unavailable", blockers=[str(error)])
        return result

    def prepare(self, member, expected, *, locked=False, persist_member=True):
        with nullcontext() if locked else self.files.lock():
            current, assets = self._capture(member)
            signature = fingerprint(current)
            if signature != expected:
                raise ProjectLibraryConflict("Project data or files changed. Refresh the preparation review.")
            root = checked_path(member["folder_path"])
            body = {"format_version": 1, "created_at": now(), "member_id": member["member_id"],
                    "source_signature": signature, **current, "warnings": sorted(set(assets.warnings))}
            assets.copy_to(root / ".connlab" / "portable")
            after, _ = self._capture(member)
            if fingerprint(after) != signature:
                raise ProjectLibraryConflict("Project data or source files changed while preparing the snapshot.")
            envelope = {"body": body, "checksum": fingerprint(body)}
            revisions = root / ".connlab" / "portable" / "revisions" / (uuid4().hex + ".json")
            atomic_json(revisions, envelope)
            atomic_json(root / PORTABLE_FILE, envelope)
            if persist_member:
                self.store.update_member(member["member_id"], {"snapshot_fingerprint": signature})
            return self.status(self.store.member(member["member_id"]))

    def _read_snapshot(self, folder):
        envelope = read_json(checked_path(folder) / PORTABLE_FILE)
        if not isinstance(envelope, dict) or not isinstance(envelope.get("body"), dict):
            raise ProjectLibraryError("The portable snapshot is damaged.")
        body = envelope["body"]
        if type(body.get("format_version")) is not int or body["format_version"] != 1:
            raise ProjectLibraryError("This portable snapshot version is not supported by this ConnLab.")
        if fingerprint(body) != envelope.get("checksum"):
            raise ProjectLibraryConflict("The portable snapshot checksum does not match.")
        required = {"member_id", "project_id", "ltr_number", "title", "rows", "files", "assets", "source_signature", "created_at", "operation_history"}
        if not required.issubset(body) or not isinstance(body["rows"], dict) or set(body["rows"]) != TABLES:
            raise ProjectLibraryError("The portable snapshot does not include the supported project data contract.")
        if len(body["rows"].get("projects", [])) != 1 or body["rows"]["projects"][0].get("project_id") != body["project_id"]:
            raise ProjectLibraryError("The portable project identity is inconsistent.")
        if not all(isinstance(body.get(key), str) and body[key] for key in ("member_id", "project_id", "title", "source_signature", "created_at")):
            raise ProjectLibraryError("The portable project identity or revision is invalid.")
        if not isinstance(body["files"], list) or not isinstance(body["assets"], list) or not isinstance(body["operation_history"], list):
            raise ProjectLibraryError("The portable file and provenance collections are invalid.")
        for entry in body["files"]:
            if not isinstance(entry, dict) or not isinstance(entry.get("relative_path"), str) or not isinstance(entry.get("directory"), bool):
                raise ProjectLibraryError("A portable project file description is invalid.")
        for entry in body["assets"]:
            if not isinstance(entry, dict) or not all(isinstance(entry.get(key), str) for key in ("token", "blob", "sha256")) or type(entry.get("size_bytes")) is not int or entry["size_bytes"] < 0:
                raise ProjectLibraryError("A portable asset description is invalid.")
        if not all(isinstance(entry, dict) for entry in body["operation_history"]):
            raise ProjectLibraryError("The portable provenance history is invalid.")
        for name, records in body["rows"].items():
            if not isinstance(records, list) or len(records) > 250000:
                raise ProjectLibraryError("The portable record collection is invalid or too large.")
            identities = set()
            for row in records:
                if not isinstance(row, dict):
                    raise ProjectLibraryError("The portable record shape is invalid.")
                if "project_id" in table(name).c and row.get("project_id") != body["project_id"]:
                    raise ProjectLibraryError("The snapshot contains records owned by another project.")
                typed_record(name, row)
                keys = [column.name for column in table(name).primary_key] if name != "report_authoring_revisions" else ["project_id", "revision"]
                if any(row.get(key) is None for key in keys):
                    raise ProjectLibraryError("A portable record identity is missing: " + name)
                key = tuple(row[key] for key in keys)
                if key in identities:
                    raise ProjectLibraryError("A portable record identity is duplicated: " + name)
                identities.add(key)
        descriptor_tokens = {record["token"] for record in body["assets"]}
        from backend.infrastructure.project_library.ownership import transform_paths
        def validate_bound_token(value):
            if value.startswith(("@asset/", "@data/")) and value not in descriptor_tokens:
                raise ProjectLibraryError("A portable path has no carried asset description.")
            return value
        transform_paths(body["rows"], validate_bound_token)
        decode_rows(body["rows"], self.settings, self.settings.projects_dir)
        if any(row.get("status") not in {"completed", "cancelled"} for row in body["rows"]["project_public_folder_workflow_operations"]):
            raise ProjectLibraryError("The snapshot contains an unfinished source-machine operation.")
        issues = validate_relations(body["rows"])
        if issues:
            raise ProjectLibraryError("The snapshot has unresolved project references: " + "; ".join(issues[:5]))
        content = {key: body[key] for key in ("project_id", "ltr_number", "title", "rows", "files", "assets", "operation_history")}
        if fingerprint(content) != body["source_signature"]:
            raise ProjectLibraryError("The portable source revision is inconsistent.")
        return body

    def _verify_files(self, folder, body):
        if project_inventory(folder) != body["files"]:
            raise ProjectLibraryConflict("Project files changed after this snapshot. Prepare an updated snapshot on the working computer.")
        if len(body["assets"]) > 100000:
            raise ProjectLibraryError("The portable asset count exceeds the supported size.")
        for record in body["assets"]:
            blob = record["blob"]
            if not record["token"].startswith(("@asset/", "@data/")) or record["token"].startswith("@asset/") and record["token"] != "@asset/" + blob:
                raise ProjectLibraryError("The portable asset token is not a supported project asset.")
            if not isinstance(blob, str) or Path(blob).name != blob or not re.fullmatch(r"[a-f0-9]{64}(?:\.[a-z0-9]+)?", blob):
                raise ProjectLibraryError("A portable asset name is invalid.")
            path = checked_path(Path(folder) / ".connlab" / "portable" / "assets" / blob)
            if path.stat().st_size != record["size_bytes"] or file_hash(path) != record["sha256"]:
                raise ProjectLibraryConflict("A portable asset is missing or changed.")
            decoded = decode_path(record["token"], self.settings, self.settings.projects_dir, body["project_id"])
            if decoded is None or not decoded.is_relative_to(self.settings.data_dir.resolve()):
                raise ProjectLibraryError("A portable asset location is not supported.")

    def pending_receive(self, body):
        """Find a verified software-owned receive after its browser review was lost."""
        directory = checked_path(self.files.root / "restores", must_exist=False)
        if not directory.is_dir():
            return None
        matches = []
        for path in directory.glob("*.json"):
            try:
                journal = read_json(checked_path(path))
                if journal.get("phase") not in {"copying", "files_received"}:
                    continue
                previous = read_json(self.files.plans / (path.stem + ".json"))
                payload = self.files.plan(path.stem, previous["fingerprint"], "restore")
                if payload.get("resolution") or payload.get("project_id") != body["project_id"] or payload.get("source_signature") != body["source_signature"]:
                    continue
                target = checked_path(payload["target_path"])
                if not target.is_relative_to(self.settings.projects_dir.resolve()):
                    continue
                marker = self.files.marker(target)
                if not marker or marker.get("project_id") != body["project_id"] or marker.get("member_id") != body["member_id"]:
                    continue
                self._verify_files(target, body)
                matches.append({"plan_id": path.stem, "target_path": str(target)})
            except (OSError, ValueError, KeyError, LookupError):
                continue
        if len(matches) > 1:
            raise ProjectLibraryConflict("Multiple interrupted receives match this source. Review their destinations before continuing.")
        return matches[0] if matches else None

    def restore_plan(self, folder, resolution=None):
        from backend.infrastructure.project_library.restore_conflicts import RestoreConflicts
        return RestoreConflicts(self).plan(folder, resolution)

    def _check_existing_keys(self, rows):
        session = self.store.session
        for name, records in rows.items():
            model = table(name)
            if name == "report_authoring_revisions":
                continue
            key_columns = list(model.primary_key)
            for record in records:
                condition = None
                for column in key_columns:
                    term = column == record[column.name]
                    condition = term if condition is None else condition & term
                existing = session.execute(select(model).where(condition)).mappings().first()
                if existing is not None and name not in {"intake_packages", "intake_assets", "intake_cases", "intake_drafts"}:
                    # Existing project is handled as a whole, never row-by-row overwritten.
                    project = rows["projects"][0]["project_id"]
                    if not self.store.project_exists(project):
                        raise ProjectLibraryConflict(f"An unrelated target record collides with {name}; review source identity.")
        session.rollback()

    def restore(self, plan_id, expected, resolution=None):
        with self.files.lock():
            payload = self.files.plan(plan_id, expected, "restore")
            if payload.get("resolution") != resolution:
                raise ProjectLibraryConflict("The selected conflict resolution changed. Review the restore again.")
            if resolution:
                from backend.infrastructure.project_library.restore_conflicts import RestoreConflicts
                return RestoreConflicts(self).restore(payload, plan_id)
            if payload["status"] in {"conflict", "unavailable"}:
                raise ProjectLibraryConflict(" ".join(payload["blockers"]))
            body = self._read_snapshot(payload["source_path"])
            self._verify_files(payload["source_path"], body)
            if body["source_signature"] != payload["source_signature"]:
                raise ProjectLibraryConflict("The portable snapshot changed after review.")
            existing = [row for row in self.store.members() if row["project_id"] == body["project_id"]]
            if existing:
                current = self.status(existing[0])
                if current["status"] == "current" and current["fingerprint"] == body["source_signature"]:
                    self.files.publish_workspace_metadata(existing[0]["folder_path"], self.store.workspace(body["project_id"]))
                    self.files.write_marker(existing[0])
                    return {"status": "already_added", "member": existing[0], "warnings": body.get("warnings", [])}
                raise ProjectLibraryConflict("The target project changed after review. Compare the working copies.")
            if self.store.project_exists(body["project_id"]):
                raise ProjectLibraryConflict("The project appeared in the target database after review.")
            if payload.get("owner_state") != fingerprint(self.store.project_numbers()):
                raise ProjectLibraryConflict("LTR ownership changed. Review the restore again.")
            self._check_existing_keys(body["rows"])
            target = payload["target_path"]
            receive_id = payload.get("recovery_plan_id") or plan_id
            journal_path = self.files.root / "restores" / (receive_id + ".json")
            journal = read_json(journal_path) if journal_path.is_file() else None
            if not journal:
                if self.files.exists(target):
                    raise ProjectLibraryConflict("The target appeared after review.")
                journal = {"plan_id": plan_id, "source_signature": body["source_signature"], "phase": "copying"}
                atomic_json(journal_path, journal)
            if not self.files.exists(target):
                source = self.files.inspect_source(payload["source_path"])
                source["member_marker"] = {"member_id": body["member_id"], "project_id": body["project_id"], "ltr_number": body["ltr_number"]}
                self.files.receive(source, target, receive_id, "restore")
            marker = self.files.marker(target)
            if not marker or marker.get("project_id") != body["project_id"] or marker.get("member_id") != body["member_id"]:
                raise ProjectLibraryConflict("The recovered target identity differs from the reviewed project.")
            self._verify_files(target, body)
            journal["phase"] = "files_received"
            atomic_json(journal_path, journal)
            PortableAssets.restore_assets(Path(target), body["assets"], self.settings, body["project_id"])
            rows = decode_rows(body["rows"], self.settings, Path(target))
            for public_state in rows.get("project_public_folder_workflow_states", []):
                public_state["auto_sync_enabled"] = False
                public_state["sync_locked"] = False
            member = {"member_id": body["member_id"], "project_id": body["project_id"], "ltr_number": body["ltr_number"],
                      "title": body["title"], "folder_path": target, "source_path": payload["source_path"],
                      "source_project_id": body["project_id"], "revision": 1, "batch_id": None,
                      "created_at": now(), "snapshot_fingerprint": body["source_signature"]}
            self._insert(rows, member)
            self.files.publish_workspace_metadata(target, self.store.workspace(body["project_id"]))
            self.files.write_marker(member)
            journal["phase"] = "completed"
            atomic_json(journal_path, journal)
            return {"status": "restored", "member": self.store.member(member["member_id"]), "warnings": body.get("warnings", [])}

    def _insert(self, rows, member, *, replace_rows=None, recovery_member=None, operation_id=None):
        session = self.store.session
        session.rollback()
        connection = session.connection()
        previous_foreign_keys = connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one()
        try:
            connection.exec_driver_sql("PRAGMA foreign_keys=ON")
            connection.exec_driver_sql("BEGIN IMMEDIATE")
            connection.exec_driver_sql("PRAGMA defer_foreign_keys=ON")
            before = {tuple(row) for row in connection.exec_driver_sql("PRAGMA foreign_key_check")}
            if replace_rows is not None:
                from backend.infrastructure.project_library.restore_conflicts import delete_owned
                delete_owned(connection, replace_rows, member["project_id"])
                connection.execute(ProjectLibraryMemberModel.__table__.delete().where(ProjectLibraryMemberModel.member_id == member["member_id"]))
            for name, records in rows.items():
                model = table(name)
                for row in records:
                    current = typed_record(name, row)
                    if name == "report_authoring_revisions":
                        current.pop("id", None)
                    keys = list(model.primary_key)
                    condition = None
                    for column in keys:
                        if column.name not in current:
                            condition = None
                            break
                        term = column == current[column.name]
                        condition = term if condition is None else condition & term
                    old = connection.execute(select(model).where(condition)).mappings().first() if condition is not None else None
                    if old is not None:
                        from backend.infrastructure.project_library.ownership import plain
                        if plain(dict(old)) != row:
                            raise ProjectLibraryConflict(f"Existing {name} has different data. The snapshot was not restored.")
                        continue
                    connection.execute(model.insert().values(**current))
            session.add(ProjectLibraryMemberModel(**member))
            if recovery_member:
                old_recovery = session.get(ProjectLibraryMemberModel, recovery_member["member_id"])
                if old_recovery is None:
                    session.add(ProjectLibraryMemberModel(**recovery_member))
                elif old_recovery.folder_path != recovery_member["folder_path"] or old_recovery.disposition != "recovery":
                    raise ProjectLibraryConflict("The verified recovery point registration changed.")
            if operation_id:
                from backend.infrastructure.storage.models_project_library import ProjectLibraryBatchModel
                session.add(ProjectLibraryBatchModel(batch_id="restore_" + operation_id, payload_json=json.dumps({"committed": True})))
            session.flush()
            after = {tuple(row) for row in connection.exec_driver_sql("PRAGMA foreign_key_check")}
            if after - before:
                raise ProjectLibraryError("Restored records contain unresolved references. No project records were committed.")
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise ProjectLibraryConflict("Target records changed or their identities conflict. Review this restore again; no project records were committed.") from error
        except Exception:
            session.rollback()
            raise
        finally:
            # Foreign-key enforcement belongs to the restore transaction. Do not
            # change the connection-pool contract of unrelated existing writers.
            session.connection().exec_driver_sql("PRAGMA foreign_keys=" + str(int(previous_foreign_keys)))
            session.rollback()
