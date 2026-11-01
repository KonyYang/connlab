"""Business-readable comparisons of already captured project snapshots."""
import json


def file_differences(before, after):
    before = {row["relative_path"]: row for row in before if not row["directory"]}
    after = {row["relative_path"]: row for row in after if not row["directory"]}
    added, removed = after.keys() - before.keys(), before.keys() - after.keys()
    changed = {path for path in before.keys() & after.keys() if before[path] != after[path]}
    notes = [f"Files: {len(added)} added, {len(changed)} changed, {len(removed)} absent from the incoming copy."]
    for label, paths in (("Changed", changed), ("Added", added), ("Absent from incoming copy", removed)):
        ordered = sorted(paths)
        notes.extend(f"{label}: {path}" for path in ordered[:10])
        if len(ordered) > 10:
            notes.append(f"{label}: {len(ordered) - 10} more files.")
    return notes


def comparable(rows):
    return sorted(json.dumps(row, sort_keys=True, ensure_ascii=False) for row in rows)


def business_differences(before, after):
    notes = []
    for field, label in (("product_name", "Sample"), ("test_item", "Test item"), ("requestor", "Requestor"), ("status", "Project status")):
        left = sorted({str(row[field]) for row in before.get("projects", []) if row.get(field) is not None})
        right = sorted({str(row[field]) for row in after.get("projects", []) if row.get(field) is not None})
        if left != right:
            notes.append(f"{label}: {'; '.join(left)[:160] or 'Not recorded'} → {'; '.join(right)[:160] or 'Not recorded'}.")
    families = {
        "project_basic_information_records": "Basic information",
        "confirmed_matrix_versions": "Matrix versions", "confirmed_matrix_groups": "Matrix groups",
        "confirmed_matrix_rows": "Matrix test items", "confirmed_matrix_cells": "Matrix steps",
        "project_matrix_draft_records": "Matrix drafts", "result_dataset_revisions": "Test result revisions",
        "measurement_plan_revisions": "Measurement plan revisions", "project_schedule_revisions": "Schedule revisions",
        "group_completion_events": "Group completion records",
    }
    for name, label in families.items():
        left, right = before.get(name, []), after.get(name, [])
        if comparable(left) == comparable(right):
            continue
        versions = lambda rows: sorted({str(row[key]) for row in rows for key in ("revision", "version", "confirmed_revision") if row.get(key) is not None})
        old_versions, new_versions = versions(left), versions(right)
        detail = f" Versions {'/'.join(old_versions) or 'none'} → {'/'.join(new_versions) or 'none'}." if old_versions != new_versions else " Contents differ."
        notes.append(f"{label}: {len(left)} existing → {len(right)} incoming.{detail}")
    return notes


def snapshot_differences(current, incoming):
    notes = [f"Existing project: {current.get('title', '')}", f"Incoming project: {incoming.get('title', '')}"]
    notes.extend(file_differences(current["files"], incoming["files"]))
    if {name: comparable(rows) for name, rows in current["rows"].items()} != {name: comparable(rows) for name, rows in incoming["rows"].items()}:
        notes.extend(business_differences(current["rows"], incoming["rows"]))
        notes.append("Saved project or test data differs between these copies.")
    else:
        notes.append("Saved project and test data matches.")
    return notes
