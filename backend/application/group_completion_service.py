"""Manual test-group completion against confirmed Matrix content."""

from dataclasses import asdict
from hashlib import sha256
import json


def group_lineage(snapshot, group):
    source = group.source_group_snapshot_id
    if source and sum(item.source_group_snapshot_id == source for item in snapshot.groups) == 1:
        return source
    return group.draft_group_id


def group_signature(snapshot, group):
    rows = {row.confirmed_row_id: row for row in snapshot.rows}
    rows_by_draft = {row.draft_row_id: row for row in snapshot.rows}
    content = []
    for cell in snapshot.cells:
        if cell.confirmed_group_id != group.confirmed_group_id:
            continue
        row = rows[cell.confirmed_row_id]
        content.append({"row": [row.source_row_snapshot_id or row.draft_row_id, row.test_item, row.source_section, row.method,
                                 row.condition, row.requirement, row.day_expression],
                        "value": cell.cell_value})
    overrides = [{"row": rows[item.confirmed_row_id].source_row_snapshot_id or rows[item.confirmed_row_id].draft_row_id, "sequence": item.step_sequence,
                  "suffix": item.step_suffix_note, "description": item.description,
                  "requirement": item.requirement} for item in snapshot.step_text_overrides
                 if item.confirmed_group_id == group.confirmed_group_id]
    quantities = []
    for item in snapshot.step_quantities:
        if item.confirmed_group_id == group.confirmed_group_id:
            value = asdict(item)
            for key in ("confirmed_step_quantity_id", "confirmed_matrix_id", "confirmed_group_id",
                        "confirmed_row_id", "draft_group_id", "draft_row_id", "confirmed_at", "source"):
                value.pop(key, None)
            value["row_lineage"] = rows[item.confirmed_row_id].source_row_snapshot_id or rows[item.confirmed_row_id].draft_row_id
            quantities.append(value)
    durations = []
    for item in snapshot.duration_authorities:
        if item.confirmed_group_id == group.confirmed_group_id:
            value = asdict(item)
            for key in ("confirmed_duration_authority_id", "confirmed_matrix_id", "confirmed_group_id",
                        "confirmed_row_id", "created_at", "updated_at"):
                value.pop(key, None)
            durations.append(value)
    point_overrides = []
    for item in snapshot.version.point_overrides:
        if item.draft_group_id != group.draft_group_id:
            continue
        value = asdict(item)
        value.pop("draft_group_id", None)
        row = rows_by_draft.get(value.pop("draft_row_id"))
        value["row_lineage"] = (row.source_row_snapshot_id or row.draft_row_id) if row else None
        point_overrides.append(value)
    body = {"lineage": group_lineage(snapshot, group),
            "samples": [group.sample_quantity_expression, group.sample_note],
            "cells": sorted(content, key=lambda item: json.dumps(item, sort_keys=True)),
            "overrides": sorted(overrides, key=lambda item: json.dumps(item, sort_keys=True)),
            "quantities": sorted(quantities, key=lambda item: json.dumps(item, sort_keys=True, default=str)),
            "durations": sorted(durations, key=lambda item: json.dumps(item, sort_keys=True, default=str)),
            "point_profile": asdict(snapshot.version.point_profile) if snapshot.version.point_profile else None,
            "point_overrides": sorted(point_overrides, key=lambda item: json.dumps(item, sort_keys=True, default=str))}
    return sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()


class GroupCompletionService:
    def __init__(self, matrices, records, guard, clock):
        self.matrices, self.records, self.guard, self.clock = matrices, records, guard, clock

    def read(self, project_id):
        snapshot = self.matrices.get_active_by_project(project_id)
        if snapshot is None:
            return None
        records = self.records.list_by_project(project_id)
        history = self.matrices.list_by_project(project_id) if records else ()
        groups = []
        for group in snapshot.groups:
            signature = group_signature(snapshot, group)
            record = next((r for r in records if r.group_lineage == group_lineage(snapshot, group)), None)
            uncertain_record = next((r for r in records if r.group_key == group.group_key), None) if record is None else None
            is_current = record is not None and record.signature == signature and all(
                len(matches := [old_group for old_group in old.groups if group_lineage(old, old_group) == group_lineage(snapshot, group)]) == 1
                and group_signature(old, matches[0]) == record.signature
                for old in history if old.version.confirmed_revision >= record.matrix_revision
            ) and any(old.version.confirmed_revision == record.matrix_revision for old in history)
            groups.append({"group_key": group.group_key, "group_label": group.group_label,
                           "completed": bool(is_current and record.completed),
                           "needs_review": bool((record and record.completed and not is_current) or (uncertain_record and uncertain_record.completed)),
                           "completed_at": record.completed_at if is_current and record.completed else None})
        return {"confirmed_matrix_id": snapshot.version.confirmed_matrix_id,
                "estimated_completion_date": snapshot.version.estimated_completion_date,
                "groups": groups, "completed_count": sum(g["completed"] for g in groups),
                "total_count": len(groups)}

    def update(self, project_id, matrix_id, group_key, completed):
        self.guard(project_id)
        snapshot = self.matrices.get_active_by_project(project_id)
        if snapshot is None or snapshot.version.confirmed_matrix_id != matrix_id:
            raise ValueError("Matrix changed. Reload before updating group completion.")
        matches = [group for group in snapshot.groups if group.group_key == group_key]
        if len(matches) != 1:
            raise LookupError("Confirmed Matrix group was not found.")
        group = matches[0]
        self.records.save(project_id, group_lineage(snapshot, group), group.group_key, snapshot.version.confirmed_revision, group_signature(snapshot, group),
                          completed, self.clock() if completed else None)
        return self.read(project_id)
