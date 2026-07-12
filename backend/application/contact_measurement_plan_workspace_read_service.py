"""Read-only operator workspace projection for contact measurement plans."""

from __future__ import annotations

from collections.abc import Iterable


class ContactMeasurementPlanWorkspaceReadService:
    """Enrich accepted authority rows without changing authority semantics."""

    def __init__(self, *, repository, confirmed_store, enabled: bool) -> None:
        self._repository = repository
        self._confirmed_store = confirmed_store
        self._enabled = enabled

    def get_workspace(self, project_id: str) -> dict[str, object]:
        if not self._enabled:
            return _empty_workspace(
                project_id,
                "disabled",
                ("Independent contact measurement authority is disabled.",),
            )
        root = self._repository.get_root(project_id)
        if root is None:
            return _empty_workspace(project_id, "not_started")
        editable = self._repository.get_editable_revision(project_id)
        active = self._repository.get_active_revision(project_id)
        revision = editable or active
        if revision is None:
            return _empty_workspace(
                project_id,
                "authority_corrupt",
                ("Contact measurement authority requires maintenance before use.",),
                root=root,
            )
        current_matrix = self._confirmed_store.get_active_by_project(project_id)
        targets = [_target_payload(target, self._repository.families(target.measurement_plan_target_snapshot_id)) for target in self._repository.targets(revision.measurement_plan_revision_id)]
        impacts = [
            _impact_payload(impact, current_matrix)
            for impact in self._repository.impacts(revision.measurement_plan_revision_id)
        ]
        open_review_count = sum(
            1
            for impact in impacts
            if impact["severity"] == "review_required"
            and impact["resolution_state"] == "open"
        )
        status = "needs_review" if open_review_count else revision.state
        return {
            "status": status,
            "project_id": project_id,
            "active_confirmed_revision_id": root.active_confirmed_revision_id,
            "editable_revision_id": root.editable_revision_id,
            "editable_revision_state": editable.state if editable is not None else None,
            "editable_revision_fingerprint": (
                editable.revision_fingerprint if editable is not None else None
            ),
            "revision": {
                "revision_id": revision.measurement_plan_revision_id,
                "revision_sequence": revision.revision_sequence,
                "state": revision.state,
                "fingerprint": revision.revision_fingerprint,
            },
            "matrix_binding": _matrix_binding(revision, current_matrix),
            "targets": targets,
            "impacts": impacts,
            "summary": _summary(targets, open_review_count),
            "diagnostics": _diagnostics(status, current_matrix),
        }

    def get_summary(self, project_id: str) -> dict[str, object]:
        """Return the compact Matrix surface from the same no-write projection."""
        workspace = self.get_workspace(project_id)
        revision = workspace.get("revision")
        return {
            "status": workspace["status"],
            "project_id": project_id,
            "revision_id": revision["revision_id"] if revision else None,
            "revision_sequence": revision["revision_sequence"] if revision else None,
            "summary": workspace["summary"],
            "matrix_binding": workspace["matrix_binding"],
            "diagnostics": workspace["diagnostics"],
        }


def _empty_workspace(
    project_id: str,
    status: str,
    diagnostics: tuple[str, ...] = (),
    *,
    root=None,
) -> dict[str, object]:
    return {
        "status": status,
        "project_id": project_id,
        "active_confirmed_revision_id": getattr(root, "active_confirmed_revision_id", None),
        "editable_revision_id": getattr(root, "editable_revision_id", None),
        "editable_revision_state": None,
        "editable_revision_fingerprint": None,
        "revision": None,
        "matrix_binding": None,
        "targets": [],
        "impacts": [],
        "summary": _summary([], 0),
        "diagnostics": list(diagnostics),
    }


def _target_payload(target, families: Iterable[object]) -> dict[str, object]:
    return {
        "stable_target_key": target.stable_target_key,
        "group_label": target.group_label,
        "test_item": target.test_item,
        "contact_kind": target.contact_kind,
        "step_sequence": target.step_sequence,
        "step_suffix_note": target.step_suffix_note,
        "sample_quantity_expression": target.sample_quantity_expression,
        "eligible": target.eligible,
        "included": target.included,
        "exclusion_reason": target.exclusion_reason,
        "is_override": target.is_override,
        "coverage_state": target.coverage_state,
        "readings_per_sample": target.readings_per_sample,
        "target_review_state": target.impact_status,
        "target_review_reason": target.impact_reason,
        "families": [
            {
                "family_id": family.family_id,
                "family_ordinal": family.family_ordinal,
                "label": family.label,
                "count_per_sample": family.count_per_sample,
                "record_label": family.record_label,
                "record_prefix": family.record_prefix,
                "included": family.included,
                "is_custom": family.is_custom,
            }
            for family in families
        ],
    }


def _matrix_binding(revision, current_matrix) -> dict[str, object]:
    return {
        "base_confirmed_matrix_id": revision.base_confirmed_matrix_id,
        "base_matrix_revision": revision.base_matrix_revision,
        "current_confirmed_matrix_id": (
            current_matrix.version.confirmed_matrix_id if current_matrix is not None else None
        ),
        "current_matrix_revision": (
            current_matrix.version.confirmed_revision if current_matrix is not None else None
        ),
        "matrix_binding_fingerprint": revision.matrix_binding_fingerprint,
    }


def _impact_payload(impact, current_matrix) -> dict[str, object]:
    return {
        "impact_subject_key": impact.impact_subject_key,
        "category": impact.category,
        "severity": impact.severity,
        "resolution_state": impact.resolution_state,
        "reason": impact.reason,
        "candidate": _candidate_context(impact.impact_subject_key, current_matrix),
    }


def _candidate_context(subject_key: str, current_matrix) -> dict[str, object] | None:
    if current_matrix is None or not subject_key.startswith("cmp-candidate:v1|"):
        return None
    parts = dict(
        token.split(":", 1)
        for token in subject_key.split("|")[1:]
        if ":" in token
    )
    group = next(
        (item for item in current_matrix.groups if item.confirmed_group_id == parts.get("group")),
        None,
    )
    row = next(
        (item for item in current_matrix.rows if item.confirmed_row_id == parts.get("row")),
        None,
    )
    try:
        step_sequence = int(parts["step"])
    except (KeyError, ValueError):
        return None
    if group is None or row is None:
        return None
    return {
        "group_label": group.group_label,
        "test_item": row.test_item,
        "step_sequence": step_sequence,
        "step_suffix_note": parts.get("suffix", ""),
    }


def _summary(targets: list[dict[str, object]], needs_review_count: int) -> dict[str, object]:
    included = [target for target in targets if bool(target["included"])]
    values_by_kind: dict[str, set[int]] = {"llcr": set(), "cr_specified_current": set()}
    for target in included:
        kind = str(target["contact_kind"])
        if kind in values_by_kind:
            values_by_kind[kind].add(int(target["readings_per_sample"]))
    readings = {
        kind: next(iter(values)) if len(values) == 1 else None
        for kind, values in values_by_kind.items()
    }
    return {
        "included_target_count": len(included),
        "total_target_count": len(targets),
        "needs_review_count": needs_review_count,
        "readings_by_kind": readings,
    }


def _diagnostics(status: str, current_matrix) -> list[str]:
    if current_matrix is None:
        return ["Active confirmed Matrix is unavailable."]
    if status == "needs_review":
        return ["Contact measurement changes require review."]
    return []
