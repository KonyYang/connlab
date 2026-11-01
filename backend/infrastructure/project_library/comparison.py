"""Business-readable comparisons of already captured project snapshots."""


def snapshot_differences(current, incoming):
    notes = [f"Existing project: {current.get('title', '')}", f"Incoming project: {incoming.get('title', '')}"]
    before = {row["relative_path"]: row for row in current["files"] if not row["directory"]}
    after = {row["relative_path"]: row for row in incoming["files"] if not row["directory"]}
    added, removed = after.keys() - before.keys(), before.keys() - after.keys()
    changed = {path for path in before.keys() & after.keys() if before[path] != after[path]}
    notes.append(f"Files: {len(added)} added, {len(changed)} changed, {len(removed)} absent from the incoming copy.")
    if current["rows"] != incoming["rows"]:
        notes.append("Saved project or test data differs between these copies.")
    else:
        notes.append("Saved project and test data matches.")
    return notes
