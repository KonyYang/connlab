"""Bounded operator entry for the separately approved renamed legacy copy.

The CLI has a fixed production root/database and one immutable member/cache/batch scope.
The Python seam permits isolated paths with the same bounded identity for verification.
It never expands or reuses the completed nine-copy cleanup run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import legacy_import_cleanup as engine

ROOT = Path("D:/ConnLabProjectsDev")
DATABASE = Path("D:/PythonProject/connlab/data/connlab.sqlite3")
FOLDER = "DL-2026-11-013 [56cdd25d]"
MEMBER = "33043ab04dfb4bb484e2d9f30a0422ca"
CACHE = "9b8d61be32ba41ef8186b172edb4256f"
BATCH = "3cf6adc1df33432686200577226889b6"
AUTHORIZATION = {FOLDER: (MEMBER, None)}
AUDIT_AUTHORIZATION = (
    "User separately authorized only DL-2026-11-013 [56cdd25d], member " + MEMBER
    + ", cache " + CACHE + ", completed batch " + BATCH
    + ": first create and verify a new database and complete directory backup; unlink only "
    "one member, one derived folder cache and 26 file indexes, then send this copy to the "
    "Windows system Recycle Bin. Preserve originals, the unsuffixed directory, all other "
    "directories, root/configuration, completed batch audit and recovery logs. Local only; "
    "no push, publication or packaging. This is not the earlier nine-copy authorization."
)
EXPECTED_COUNTS = {"project_library_members": 1, "material_archive_folders": 1, "material_archive_files": 26}


def validate_unit(units):
    if len(units) != 1:
        raise engine.CleanupError("Only the separately approved single copy is allowed")
    unit = units[0]
    members = unit.get("members", [])
    caches = unit.get("archive_indexes", [])
    comparisons = unit.get("comparisons", [])
    if (unit.get("folder") != FOLDER or Path(unit["path"]).name != FOLDER
            or len(members) != 1 or members[0].get("member_id") != MEMBER
            or members[0].get("project_id") is not None or members[0].get("source_project_id") is not None
            or members[0].get("batch_id") != BATCH
            or engine.norm(members[0]["folder_path"]) != engine.norm(unit["path"])
            or unit.get("project_ids") != [] or unit.get("projects") != [] or unit.get("workspaces") != []
            or len(caches) != 1 or caches[0].get("folder_id") != CACHE
            or engine.norm(caches[0]["folder_path"]) != engine.norm(unit["path"])
            or unit.get("file_index_counts") != {"member:" + MEMBER: 26}
            or unit.get("report_shortcuts") != [] or unit.get("disk", {}).get("status") != "complete"
            or len(unit["disk"].get("files", {})) != 27 or len(comparisons) != 1
            or engine.norm(comparisons[0]["source"]["path"]) != engine.norm(members[0]["source_path"])):
        raise engine.CleanupError("The approved single-copy identity or relationship scope changed")
    return unit


def validate_manifest(manifest):
    unit = validate_unit(manifest["units"])
    authorization = {key: tuple(value) for key, value in manifest["authorization"].items()}
    counts = {table: len(value) for table, value in manifest["relations"]["delete_rows"].items() if value}
    if (authorization != AUTHORIZATION or manifest.get("audit_authorization") != AUDIT_AUTHORIZATION
            or counts != EXPECTED_COUNTS or len(manifest["directories"]) != 1
            or engine.norm(manifest["directories"][0]["path"]) != engine.norm(unit["path"])
            or engine.norm(Path(unit["path"]).parent) != engine.norm(manifest["root"])):
        raise engine.CleanupError("Run is not the separately approved single-copy cleanup")


def prepare(facts, run):
    validate_unit(facts["units"])
    manifest = engine.prepare(facts, run, authorization=AUTHORIZATION, audit_authorization=AUDIT_AUTHORIZATION)
    validate_manifest(manifest)
    return manifest


def load_run(run):
    manifest, progress = engine.load_run(run)
    validate_manifest(manifest)
    if (Path(run)/"authorization.txt").read_text(encoding="utf-8") != AUDIT_AUTHORIZATION:
        raise engine.CleanupError("The single-copy authorization record changed")
    return manifest, progress


def apply(run, *, recycler=None):
    load_run(run)
    return engine.apply(run, recycler=recycler)


def verify(run):
    load_run(run)
    return engine.verify(run)


def restore_associations(run):
    load_run(run)
    return engine.restore_associations(run)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "apply", "verify", "restore-associations"))
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--preview", type=Path)
    args = parser.parse_args()
    facts = engine.read_json(args.preview) if args.command == "prepare" and args.preview else None
    if args.command == "prepare" and facts is None:
        parser.error("prepare requires --preview")
    manifest = facts if facts is not None else load_run(args.run)[0]
    if engine.norm(manifest["root"]) != engine.norm(ROOT) or engine.norm(manifest["database"]) != engine.norm(DATABASE):
        raise engine.CleanupError("CLI is restricted to the approved production root/database")
    if args.command == "prepare":
        result = prepare(facts, args.run)
        result = {"status": "prepared", "directories": len(result["directories"]), "run": str(args.run)}
    else:
        result = {"apply": apply, "verify": verify, "restore-associations": restore_associations}[args.command](args.run)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
