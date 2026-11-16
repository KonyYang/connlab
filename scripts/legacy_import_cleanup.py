"""Bounded operator tool for the explicitly approved legacy-copy cleanup.

No application startup, migrations, generic cascade deletion or permanent-delete fallback.
The durable run directory contains the backup, exact SQL undo rows and progress receipts.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack, contextmanager
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.files.project_file_generation_journal import ProjectFileGenerationJournal
from backend.infrastructure.project_library.files import checked_path, inventory, copy_verified, atomic_json

AUTHORIZATION = {
    "DL-2026-04-003": ("f47238f5218a44e48ddb5e7b5a70d0b5", "158f10b125a147f2bfcdf664289697d5"),
    "DL-2026-04-009": ("217075a719314b2eb32a72e905b393a1", "9ef4d9ff38bd4f22994937f7b6f92c65"),
    "DL-2026-04-011": ("4227fba4bd16406283063b58ed2ce8d5", "0e2faeec41624c2da14ce08d51e64b9a"),
    "DL-2026-04-012": ("64ea449c9fac46d8a0cc92dcd7a8d8af", "87820d2a52e1486aaf81ca38ca440c90"),
    "DL-2026-04-013": ("1b7ce8bc75cd479a817764917d5df85e", "986d58e76ed947b88ad1fe99992d5760"),
    "DL-2026-04-018": ("b62d9b9cf37b4ab28fc312c2ebf8cee5", "26002737f59f41f1aa52a777c269a67b"),
    "DL-2026-04-031": ("70c94cb17d324ba89deb4c0acfb2dda2", None),
    "DL-2026-04-033": ("7051e90924964a8d8b4379ef1ce4ade0", None),
    "DL-2026-05-001": ("899e8619b0164b858693e16b2e092972", None),
    "DL-2026-05-001 Coolpower HD3.5MM CTC qulificaition test": ("6a5b464c2dac404592040834f42a75fd", None),
}
DELETE_ORDER = ("library_report_shortcuts", "material_archive_files", "material_archive_folders",
                "project_lifecycle_events", "project_official_workspace_records", "project_library_members", "projects")
AUDIT_AUTHORIZATION = "User explicitly authorized only nine approved duplicate folders and one database-only remainder; verified backups before unlink and Windows Recycle Bin. Preserve originals, all excluded units, root and configuration. Local only; no push, publication or packaging."


class CleanupError(ValueError):
    """A safety check failed; retain backups and stop without guessing."""


def digest(path):
    with Path(path).open("rb") as stream:
        from hashlib import file_digest
        return file_digest(stream, "sha256").hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def norm(value):
    return os.path.normcase(os.path.abspath(value)).replace("\\", "/").casefold()


def inside(path, root):
    value, parent = norm(path), norm(root)
    return value == parent or value.startswith(parent + "/")


def sqlname(value):
    return '"' + value.replace('"', '""') + '"'


def connect(path, *, writable=False):
    path = checked_path(path)
    conn = sqlite3.connect(path.as_uri() + ("?mode=rw" if writable else "?mode=ro"), uri=True, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    if not writable:
        conn.execute("PRAGMA query_only=ON")
    return conn


def read_json(path):
    return json.loads(checked_path(path).read_text(encoding="utf-8-sig"))


def identities(path):
    stat = checked_path(path).stat()
    return [stat.st_dev, stat.st_ino]


def schema(conn):
    return {r[0]: [dict(c) for c in conn.execute("PRAGMA table_info(" + sqlname(r[0]) + ")")]
            for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")}


def rows(conn, table, where="1", values=()):
    result = [dict(r) for r in conn.execute("SELECT * FROM " + sqlname(table) + " WHERE " + where, values)]
    return sorted(result, key=canonical)


def check_subset(current, expected, label):
    if len(current) != len(expected):
        raise CleanupError("Changed record count: " + label)
    for old in expected:
        if not any(all(row.get(k) == v for k, v in old.items()) for row in current):
            raise CleanupError("Changed record identity/version: " + label)


def validate_incoming_foreign_keys(conn, selected, allowed=None):
    allowed = selected if allowed is None else allowed
    tables = schema(conn)
    for child in tables:
        groups = {}
        for fk in conn.execute("PRAGMA foreign_key_list(" + sqlname(child) + ")"):
            groups.setdefault(fk["id"], []).append(dict(fk))
        for group in groups.values():
            group.sort(key=lambda fk: fk["seq"])
            parent = group[0]["table"]
            for parent_row in selected.get(parent, []):
                parent_pk = [c["name"] for c in tables[parent] if c["pk"]]
                values = [parent_row[fk["to"] or parent_pk[index]] for index, fk in enumerate(group)]
                if any(value is None for value in values):
                    continue
                found = rows(conn, child, " AND ".join(sqlname(fk["from"])+"=?" for fk in group), values)
                if any(row not in allowed.get(child, []) for row in found):
                    raise CleanupError("Unapproved incoming foreign-key reference: " + child)


def reject_new_associations(conn, manifest):
    project_ids = {p for u in manifest["units"] for p in u["project_ids"]}
    keys = {key for u in manifest["units"] for key in u["file_index_counts"]}
    for table, columns in schema(conn).items():
        pathcols = [c["name"] for c in columns if c["name"] == "path" or c["name"].endswith("_path")]
        if not pathcols and not any(c["name"] in {"project_id", "source_project_id", "catalog_key"} for c in columns):
            continue
        for row in rows(conn, table):
            if (row.get("project_id") in project_ids or row.get("source_project_id") in project_ids
                    or row.get("catalog_key") in keys
                    or any(isinstance(row.get(col), str) and row[col] and any(inside(row[col], u["path"]) for u in manifest["units"]) for col in pathcols)):
                raise CleanupError("New association/reference appeared after unlink: " + table)
    validate_incoming_foreign_keys(conn, manifest["relations"]["delete_rows"], allowed={})
    for batch in manifest["relations"]["batches"]:
        check_subset(rows(conn,"project_library_batches","batch_id=?",(batch["batch_id"],)), [batch], "preserved completed batch")


def capture(conn, units):
    """Reject new business state rather than applying a generic cascade."""
    tables = schema(conn)
    project_ids = sorted({p for u in units for p in u["project_ids"]})
    members = sorted(m["member_id"] for u in units for m in u["members"])
    keys = sorted({key for u in units for key in u["file_index_counts"]})
    selected = {name: [] for name in DELETE_ORDER}
    for table in tables:
        columns = {c["name"] for c in tables[table]}
        if "project_id" in columns and project_ids:
            found = rows(conn, table, "project_id IN (" + ",".join("?" for _ in project_ids) + ")", project_ids)
            if found and table not in DELETE_ORDER:
                raise CleanupError("New business/project relation must be preserved: " + table)
            if table in selected:
                selected[table] = found
        if "source_project_id" in columns and project_ids:
            found = rows(conn, table, "source_project_id IN (" + ",".join("?" for _ in project_ids) + ")", project_ids)
            if any(table != "project_library_members" or row["member_id"] not in members for row in found):
                raise CleanupError("Cross-project source reference: " + table)
    selected["project_library_members"] = rows(conn, "project_library_members", "member_id IN (" + ",".join("?" for _ in members) + ")", members)
    for unit in units:
        actual = [r for r in selected["project_library_members"] if r["member_id"] in {m["member_id"] for m in unit["members"]}]
        check_subset(actual, unit["members"], "member " + unit["folder"])
        check_subset([r for r in selected["projects"] if r["project_id"] in unit["project_ids"]], unit["projects"], "project " + unit["folder"])
        check_subset([r for r in selected["project_official_workspace_records"] if r["project_id"] in unit["project_ids"]], unit["workspaces"], "workspace " + unit["folder"])
        found = [r for r in rows(conn, "material_archive_folders") if norm(r["folder_path"]) == norm(unit["path"])]
        check_subset(found, unit["archive_indexes"], "archive " + unit["folder"])
        selected["material_archive_folders"].extend(found)
    for table in ("material_archive_files", "library_report_shortcuts"):
        selected[table] = rows(conn, table, "catalog_key IN (" + ",".join("?" for _ in keys) + ")", keys) if keys else []
    for unit in units:
        for key, count in unit["file_index_counts"].items():
            if sum(r["catalog_key"] == key for r in selected["material_archive_files"]) != count:
                raise CleanupError("Changed file index count: " + key)
        check_subset([r for r in selected["library_report_shortcuts"] if r["catalog_key"] in unit["file_index_counts"]], unit["report_shortcuts"], "shortcut")
    for unit in units:
        for project_id, expected_counts in unit.get("db_counts", {}).items():
            actual_counts = {}
            for table, columns in tables.items():
                if any(c["name"] == "project_id" for c in columns):
                    count = conn.execute("SELECT count(*) FROM " + sqlname(table) + " WHERE project_id=?", (project_id,)).fetchone()[0]
                    if count:
                        actual_counts[table] = count
            if actual_counts != expected_counts:
                raise CleanupError("Changed project relation count: " + project_id)
    validate_incoming_foreign_keys(conn, selected)
    # Typed external paths into an approved directory may only be owned by deleted rows.
    for table, columns in tables.items():
        pathcols = [c["name"] for c in columns if c["name"] == "path" or c["name"].endswith("_path")]
        if not pathcols:
            continue
        for row in rows(conn, table):
            if any(isinstance(row.get(col), str) and row[col] and any(inside(row[col], u["path"]) for u in units) for col in pathcols):
                if row not in selected.get(table, []):
                    raise CleanupError("Unapproved path reference: " + table)
    for table in DELETE_ORDER:
        if conn.execute("SELECT 1 FROM sqlite_master WHERE type='trigger' AND tbl_name=?", (table,)).fetchone():
            raise CleanupError("Unexpected delete trigger: " + table)
    batches = []
    for batch_id in sorted({m["batch_id"] for u in units for m in u["members"]}):
        batch = rows(conn, "project_library_batches", "batch_id=?", (batch_id,))
        if len(batch) != 1 or json.loads(batch[0]["payload_json"]).get("status") != "completed":
            raise CleanupError("Old intake is not completed: " + str(batch_id))
        if any(r["member_id"] not in members for r in rows(conn, "project_library_members", "batch_id=?", (batch_id,))):
            raise CleanupError("Shared intake batch outside approved scope")
        batches.extend(batch)
    return {"delete_rows": {k: sorted(v, key=canonical) for k,v in selected.items()},
            "batches": batches, "schema": tables}


def compare_files(path, expected):
    entries = inventory(path)
    actual = {r["relative_path"].casefold(): r for r in entries if not r["directory"]}
    if set(actual) != set(expected):
        raise CleanupError("File set changed: " + str(path))
    for key, old in expected.items():
        current = actual[key]
        if current["size"] != old["size"] or current["sha256"] != old["sha256"]:
            raise CleanupError("File content changed: " + str(path / old["relative_path"]))
    return entries


def select_units(facts, authorization):
    root = checked_path(facts["root"])
    units = [u for u in facts["units"] if u["folder"] in authorization]
    if len(units) != len(authorization):
        raise CleanupError("Approved set is incomplete or duplicated")
    for unit in units:
        target = Path(unit["path"])
        if norm(target.parent) != norm(root) or target.name != unit["folder"]:
            raise CleanupError("Target is not the approved direct child")
        if len(unit["members"]) != 1 or (unit["members"][0]["member_id"], unit["members"][0]["project_id"]) != tuple(authorization[unit["folder"]]):
            raise CleanupError("Approved stable identity mismatch")
        if unit["project_ids"] != ([authorization[unit["folder"]][1]] if authorization[unit["folder"]][1] else []):
            raise CleanupError("Unexpected project owner")
        if unit["disk"]["status"] not in {"complete", "missing"}:
            raise CleanupError("Unverified target disk")
        for comparison in unit["comparisons"]:
            source = comparison["source"]
            if source["status"] != "complete" or inside(source["path"], root) or inside(root, source["path"]):
                raise CleanupError("Source unavailable or overlaps cleanup root")
            compare_files(Path(source["path"]), source["files"])
            old_identity = source.get("identity")
            if old_identity and identities(Path(source["path"])) != [old_identity["device"], old_identity["inode"]]:
                raise CleanupError("Original directory identity changed")
    return units


@contextmanager
def locks(manifest):
    data = Path(manifest["database"]).parent
    journal = GenerationJournal(data / "project_library" / "locks")
    with ExitStack() as stack:
        stack.enter_context(journal.lock("materials-archive"))
        stack.enter_context(journal.lock("library"))
        changes = GenerationJournal(data / "project_library" / "changes")
        for member in sorted(m["member_id"] for u in manifest["units"] for m in u["members"]):
            state = changes.read(member)
            if state and state.get("status") != "completed":
                raise CleanupError("Unfinished library location change: " + member)
        for project_id in sorted({p for u in manifest["units"] for p in u["project_ids"]}):
            generation = GenerationJournal(data / "project_folder_generation")
            stack.enter_context(generation.lock(project_id))
            for store in (generation, GenerationJournal(data / "basic_project_workspace"), ProjectFileGenerationJournal(data / "project_file_generation")):
                state = store.read(project_id)
                if state and state.get("status") != "completed":
                    raise CleanupError("Unfinished project operation: " + project_id)
        yield


def prepare(facts, run, *, authorization=None):
    """Create and verify recoverable backups. Never mutate source DB or directories."""
    authorization = AUTHORIZATION if authorization is None else authorization
    run = checked_path(run, must_exist=False)
    units = select_units(facts, authorization)
    db, root = checked_path(facts["database"]), checked_path(facts["root"])
    if run.exists() or inside(run, root) or inside(root, run) or inside(db, run):
        raise CleanupError("Backup destination must be a new directory outside live data")
    for unit in units:
        for comp in unit["comparisons"]:
            if inside(run, comp["source"]["path"]) or inside(comp["source"]["path"], run):
                raise CleanupError("Backup overlaps an original")
    run.mkdir(parents=True)
    atomic_json(run / "approved-preview.json", facts)
    (run / "authorization.txt").write_text(AUDIT_AUTHORIZATION, encoding="utf-8")
    manifest = {"version": 1, "created_at": stamp(), "database": str(db), "root": str(root), "root_identity": identities(root),
                "authorization": authorization, "units": units, "directories": [], "preview_sha256": digest(run / "approved-preview.json")}
    with locks(manifest):
        # Completed recovery states remain in their shared store; retain scoped copies in audit.
        data = db.parent
        manifest["retained_journal_states"] = {}
        for unit in units:
            member_id = unit["members"][0]["member_id"]
            journal = GenerationJournal(data / "project_library" / "changes")
            state = journal.read(member_id)
            if state:
                manifest["retained_journal_states"]["library_change:" + member_id] = state
            for project_id in unit["project_ids"]:
                for name in ("project_folder_generation", "basic_project_workspace", "project_file_generation"):
                    store_type = ProjectFileGenerationJournal if name == "project_file_generation" else GenerationJournal
                    state = store_type(data / name).read(project_id)
                    if state:
                        manifest["retained_journal_states"][name + ":" + project_id] = state
        with connect(db) as source, sqlite3.connect(run / "database.sqlite3") as destination:
            source.backup(destination)
        with connect(run / "database.sqlite3") as backup:
            if backup.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise CleanupError("Database backup integrity check failed")
            manifest["relations"] = capture(backup, units)
        for unit in units:
            target = Path(unit["path"])
            if unit["disk"]["status"] == "missing":
                if target.exists():
                    raise CleanupError("Previously absent target now exists")
                continue
            entries = compare_files(target, unit["disk"]["files"])
            old_identity = unit["disk"].get("identity")
            if old_identity and identities(target) != [old_identity["device"], old_identity["inode"]]:
                raise CleanupError("Target directory identity changed")
            backup = run / "directories" / unit["folder"]
            copy_verified(target, backup, entries)
            if inventory(backup) != entries:
                raise CleanupError("Directory backup verification failed")
            manifest["directories"].append({"path": str(target), "backup": str(backup), "identity": identities(target), "inventory": entries})
        with connect(db) as current:
            if capture(current, units) != manifest["relations"]:
                raise CleanupError("Candidate relations changed during backup")
        manifest["database_backup_sha256"] = digest(run / "database.sqlite3")
        atomic_json(run / "manifest.json", {"payload": manifest, "sha256": sha256(canonical(manifest).encode()).hexdigest()})
        atomic_json(run / "progress.json", {"status": "prepared", "database_committed": False, "recycled": {}, "events": [{"at": stamp(), "event": "verified_backups_completed"}]})
    return manifest


def load_run(run):
    run = checked_path(run)
    envelope = read_json(run / "manifest.json")
    manifest = envelope["payload"]
    if envelope["sha256"] != sha256(canonical(manifest).encode()).hexdigest():
        raise CleanupError("Manifest checksum mismatch")
    if digest(run / "approved-preview.json") != manifest["preview_sha256"] or digest(run / "database.sqlite3") != manifest["database_backup_sha256"]:
        raise CleanupError("Backup evidence checksum mismatch")
    if identities(Path(manifest["root"])) != manifest["root_identity"]:
        raise CleanupError("Cleanup root identity changed")
    for directory in manifest["directories"]:
        if inventory(Path(directory["backup"])) != directory["inventory"]:
            raise CleanupError("Directory backup has changed")
    return manifest, read_json(run / "progress.json")


def current_deleted_rows(conn, manifest):
    found = {}
    for table, expected in manifest["relations"]["delete_rows"].items():
        pk = [c["name"] for c in manifest["relations"]["schema"][table] if c["pk"]]
        found[table] = []
        for old in expected:
            found[table].extend(rows(conn, table, " AND ".join(sqlname(k)+"=?" for k in pk), [old[k] for k in pk]))
        found[table] = sorted(found[table], key=canonical)
    return found


def save_progress(run, progress, event):
    progress["events"].append({"at": stamp(), "event": event})
    atomic_json(Path(run) / "progress.json", progress)


def apply(run, *, recycler=None):
    """Unlink in one transaction, then recycle remaining exact verified copies."""
    run = checked_path(run)
    manifest, progress = load_run(run)
    if progress["status"] == "restored":
        raise CleanupError("Associations were restored; this run cannot be reapplied")
    if recycler is None:
        from backend.infrastructure.files.windows_recycle import recycle_directory
        recycler = recycle_directory
    with locks(manifest):
        with connect(manifest["database"], writable=True) as conn:
            conn.execute("BEGIN IMMEDIATE")
            found = current_deleted_rows(conn, manifest)
            expected = manifest["relations"]["delete_rows"]
            before = found == expected
            after = all(not value for value in found.values())
            if not before and not after:
                raise CleanupError("Mixed or changed database cleanup state; no automatic replay")
            if before:
                if progress["database_committed"] or progress["recycled"]:
                    raise CleanupError("Restored database conflicts with progress")
                if capture(conn, manifest["units"]) != manifest["relations"]:
                    raise CleanupError("Candidate graph/schema changed after backup")
                for directory in manifest["directories"]:
                    target = Path(directory["path"])
                    if identities(target) != directory["identity"] or inventory(target) != directory["inventory"]:
                        raise CleanupError("Target changed after backup")
                for unit in manifest["units"]:
                    if unit["disk"]["status"] == "missing" and Path(unit["path"]).exists():
                        raise CleanupError("Absent target appeared after backup")
                    for comp in unit["comparisons"]:
                        compare_files(Path(comp["source"]["path"]), comp["source"]["files"])
                baseline_fk = [tuple(r) for r in conn.execute("PRAGMA foreign_key_check")]
                for table in DELETE_ORDER:
                    pk = [c["name"] for c in manifest["relations"]["schema"][table] if c["pk"]]
                    for row in expected[table]:
                        changed = conn.execute("DELETE FROM " + sqlname(table) + " WHERE " + " AND ".join(sqlname(k)+"=?" for k in pk), [row[k] for k in pk]).rowcount
                        if changed != 1:
                            raise CleanupError("Delete did not match one exact row")
                if [tuple(r) for r in conn.execute("PRAGMA foreign_key_check")] != baseline_fk:
                    raise CleanupError("Cleanup introduced foreign-key damage")
            reject_new_associations(conn, manifest)
            conn.commit()
        progress["database_committed"] = True
        save_progress(run, progress, "database_unlink_confirmed")
        for directory in manifest["directories"]:
            target = Path(directory["path"])
            key = str(target)
            if key in progress["recycled"]:
                receipt = progress["recycled"][key]
                if target.exists() or inventory(Path(receipt["recycled_path"])) != directory["inventory"]:
                    raise CleanupError("Completed recycle receipt no longer matches")
                continue
            if not target.exists():
                raise CleanupError("Unreceipted missing directory: inspect system Recycle Bin before resume")
            if identities(target) != directory["identity"] or inventory(target) != directory["inventory"]:
                raise CleanupError("Target changed before recycling")
            def record(receipt):
                if receipt["source"] != key or inventory(Path(receipt["recycled_path"])) != directory["inventory"]:
                    raise CleanupError("Recycle receipt/content mismatch")
                progress["recycled"][key] = receipt
                save_progress(run, progress, "recycled " + key)
            recycler(target, record)
            if key not in progress["recycled"] or target.exists():
                raise CleanupError("No durable system Recycle Bin receipt")
        progress["status"] = "completed"
        save_progress(run, progress, "completed")
    return verify(run)


def verify(run):
    manifest, progress = load_run(run)
    with connect(manifest["database"]) as conn:
        if any(current_deleted_rows(conn, manifest).values()):
            raise CleanupError("Selected associations remain")
        reject_new_associations(conn, manifest)
    for directory in manifest["directories"]:
        if Path(directory["path"]).exists():
            raise CleanupError("Selected directory has not been recycled")
        receipt = progress["recycled"].get(directory["path"])
        if not receipt or inventory(Path(receipt["recycled_path"])) != directory["inventory"]:
            raise CleanupError("System Recycle Bin evidence missing/changed")
    for unit in manifest["units"]:
        for comparison in unit["comparisons"]:
            compare_files(Path(comparison["source"]["path"]), comparison["source"]["files"])
    return {"status": progress["status"], "directories_recycled": len(progress["recycled"]), "deleted_row_counts": {t:len(r) for t,r in manifest["relations"]["delete_rows"].items()}, "backup_directory": str(Path(run))}


def restore_associations(run):
    """Selective undo only. Never replace the live DB or overwrite conflicting rows."""
    run = checked_path(run)
    manifest, progress = load_run(run)
    with locks(manifest), connect(manifest["database"], writable=True) as conn:
        conn.execute("BEGIN IMMEDIATE")
        if any(current_deleted_rows(conn, manifest).values()):
            raise CleanupError("Restore requires all selected primary keys to be absent")
        for table in reversed(DELETE_ORDER):
            for row in manifest["relations"]["delete_rows"][table]:
                columns = list(row)
                conn.execute("INSERT INTO " + sqlname(table) + " (" + ",".join(sqlname(k) for k in columns) + ") VALUES (" + ",".join("?" for _ in columns) + ")", [row[k] for k in columns])
        conn.commit()
        progress["status"] = "restored"
        save_progress(run, progress, "selective_association_restore")
    return {"status": "restored", "note": "Restore folders separately from verified backups only to absent original paths; never overwrite."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "apply", "verify", "restore-associations"))
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--preview", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        if args.preview is None:
            parser.error("prepare requires --preview")
        facts = read_json(args.preview)
        if norm(facts["root"]) != norm("D:/ConnLabProjectsDev") or norm(facts["database"]) != norm("D:/PythonProject/connlab/data/connlab.sqlite3"):
            raise CleanupError("CLI is restricted to the explicitly authorized production root/database")
        result = prepare(facts, args.run)
        result = {"status": "prepared", "directories": len(result["directories"]), "run": str(args.run)}
    else:
        result = {"apply": apply, "verify": verify, "restore-associations": restore_associations}[args.command](args.run)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
