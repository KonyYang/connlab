"""Validate the explicit project point profile and step-limited Matrix coverage."""

from __future__ import annotations

import re
from dataclasses import replace
from hashlib import sha256

from backend.application.contact_point_profile_expression import (
    ContactPointExpressionError,
    parse_point_expression,
)
from backend.application.contact_point_profile_confirmed_consumer_adapter import EffectiveConfirmedPointProfile
from backend.domain.confirmed_matrix_authority_models import ConfirmedMatrixSnapshot
from backend.domain.matrix_contact_measurement_models import point_profile_to_json, point_overrides_to_json
from backend.domain.matrix_contact_measurement_models import (
    MatrixPointCategory,
    MatrixPointProfile,
    MatrixStepPointCategory,
    MatrixStepPointOverride,
)
from backend.modules.test_plan.matrix_step_sequence_validation import parse_step_tokens


_PREFIX = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}\Z")


def electrical_test_kind(test_item: str) -> str | None:
    """Recognize electrical measurement rows, never arbitrary step descriptions."""
    text = re.sub(r"[^A-Z0-9]+", " ", test_item.upper()).strip()
    if re.search(r"\bIR\b|\bINSULATION RESISTANCE\b", text):
        return "ir"
    if re.search(r"\bDWV\b|\bDIELECTRIC WITHSTANDING VOLTAGE\b", text):
        return "dwv"
    return None


def _validated_electrical_count(value: str | None, kind: str) -> str | None:
    text = (value or "").strip()
    if not text:
        return None
    if not re.fullmatch(r"[0-9]{1,5}", text) or not 1 <= int(text) <= 8192:
        raise ValueError(f"{kind} test points per sample must be a whole number from 1 to 8192.")
    return str(int(text))


def validate_matrix_test_points(
    profile: MatrixPointProfile | None,
    overrides: tuple[MatrixStepPointOverride, ...],
) -> tuple[MatrixPointProfile | None, tuple[MatrixStepPointOverride, ...]]:
    """Return canonical explicit IDs; never promote count-only legacy suggestions."""
    if profile is None:
        if overrides:
            raise ValueError("A project Point Profile is required before step exceptions.")
        return None, ()
    ir_count = _validated_electrical_count(profile.ir_points_per_sample, "IR")
    dwv_count = _validated_electrical_count(profile.dwv_points_per_sample, "DWV")
    if len(profile.categories) > 256:
        raise ValueError("Project Point Profile allows at most 256 categories.")
    seen_prefixes: set[str] = set()
    project_points: dict[str, set[str]] = {}
    categories: list[MatrixPointCategory] = []
    total = 0
    for category in profile.categories:
        prefix = category.prefix.strip()
        key = prefix.casefold()
        if not _PREFIX.fullmatch(prefix) or key in seen_prefixes:
            raise ValueError("Project Point Profile category prefix is invalid or duplicated.")
        try:
            parsed = parse_point_expression(category.point_expression)
        except ContactPointExpressionError as exc:
            raise ValueError(str(exc)) from exc
        seen_prefixes.add(key)
        project_points[key] = set(parsed.points)
        total += parsed.count
        categories.append(MatrixPointCategory(prefix, parsed.canonical, category.cr_selected))
    if total > 8192:
        raise ValueError("Project Point Profile may contain at most 8192 points.")
    profile = MatrixPointProfile(tuple(categories), profile.delta_r_enabled, ir_count, dwv_count)
    normalized_overrides: list[MatrixStepPointOverride] = []
    seen_steps: set[tuple[str, str, int, str]] = set()
    for override in overrides:
        suffix = override.step_suffix_note.strip()
        identity = (override.draft_group_id, override.draft_row_id, override.step_sequence, suffix)
        if override.step_sequence <= 0 or identity in seen_steps or not override.categories:
            raise ValueError("Step point exception identity or categories are invalid.")
        seen_steps.add(identity)
        seen_categories: set[str] = set()
        subsets: list[MatrixStepPointCategory] = []
        for category in override.categories:
            prefix = category.prefix.strip()
            key = prefix.casefold()
            if key in seen_categories or key not in project_points:
                raise ValueError("Step point exception category is not in the project Point Profile.")
            seen_categories.add(key)
            try:
                parsed = parse_point_expression(category.point_expression)
            except ContactPointExpressionError as exc:
                raise ValueError(str(exc)) from exc
            if not set(parsed.points).issubset(project_points[key]):
                raise ValueError("Step point exception contains IDs outside the project Point Profile.")
            subsets.append(MatrixStepPointCategory(prefix, parsed.canonical))
        normalized_overrides.append(MatrixStepPointOverride(
            override.draft_group_id, override.draft_row_id, override.step_sequence,
            suffix, tuple(subsets),
        ))
    return profile, tuple(normalized_overrides)


def validate_matrix_point_targets(
    overrides: tuple[MatrixStepPointOverride, ...],
    *,
    profile: MatrixPointProfile | None = None,
    groups: tuple[object, ...],
    rows: tuple[object, ...],
    cells: tuple[object, ...],
) -> None:
    """Exceptions may narrow only selected contact-test steps actually in the Matrix."""
    selected_groups = {group.draft_group_id for group in groups if group.is_selected}
    contact_rows = {
        row.draft_row_id: _contact_row_kind(row.test_item) for row in rows
        if not row.is_sample_row and _contact_row_kind(row.test_item) is not None
    }
    targets: dict[tuple[str, str, int, str], str] = {}
    for cell in cells:
        if cell.draft_group_id not in selected_groups or cell.draft_row_id not in contact_rows:
            continue
        tokens, _warnings = parse_step_tokens(cell.cell_value)
        targets.update({
            (cell.draft_group_id, cell.draft_row_id, token.sequence,
             (token.suffix_note or "").strip()): contact_rows[cell.draft_row_id]
            for token in tokens
        })
    cr_categories = {
        item.prefix.casefold() for item in profile.categories if item.cr_selected
    } if profile is not None else set()
    if profile is not None and profile.categories and "cr" in targets.values() and not cr_categories:
        raise ValueError("CR Matrix steps require at least one category selected for CR.")
    for override in overrides:
        identity = (
            override.draft_group_id, override.draft_row_id,
            override.step_sequence, override.step_suffix_note,
        )
        if identity not in targets:
            raise ValueError("Step point exception must target a selected LLCR/CR Matrix step.")
        if targets[identity] == "cr" and any(
            item.prefix.casefold() not in cr_categories for item in override.categories
        ):
            raise ValueError("CR step point exception includes a category not selected for CR.")


def _contact_row_kind(test_item: str) -> str | None:
    text = re.sub(r"[^A-Z0-9]+", " ", (test_item or "").upper()).strip()
    if "LLCR" in text or ("CONTACT RESISTANCE" in text and "LOW LEVEL" in text):
        return "llcr"
    if text == "CR" or text.startswith("CR ") or "CONTACT RESISTANCE" in text:
        return "cr"
    return None


def effective_matrix_point_profile(
    snapshot: ConfirmedMatrixSnapshot,
) -> EffectiveConfirmedPointProfile | None:
    """Project a confirmed Matrix-owned profile into existing Fee/record consumers."""
    profile = snapshot.version.point_profile
    if profile is None or not profile.categories:
        return None
    profile, overrides = validate_matrix_test_points(profile, snapshot.version.point_overrides)
    assert profile is not None
    categories = tuple({
        "category_id": category.prefix.casefold(),
        "category_ordinal": index,
        "label": category.prefix,
        "record_prefix": category.prefix,
        "point_expression": category.point_expression,
        "count_per_sample": parse_point_expression(category.point_expression).count,
        "included": True,
    } for index, category in enumerate(profile.categories))
    cr_ids = tuple(category.prefix.casefold() for category in profile.categories if category.cr_selected)
    fingerprint = sha256((
        (point_profile_to_json(replace(profile, ir_points_per_sample=None, dwv_points_per_sample=None)) or "")
        + point_overrides_to_json(overrides)
    ).encode("utf-8")).hexdigest()
    return EffectiveConfirmedPointProfile(
        status="confirmed",
        readings_per_sample=str(sum(int(item["count_per_sample"]) for item in categories)),
        revision_id=snapshot.version.confirmed_matrix_id,
        revision_sequence=snapshot.version.confirmed_revision,
        fingerprint=fingerprint,
        lineage=f"Confirmed Matrix v{snapshot.version.confirmed_revision} Test points ({fingerprint})",
        message=None,
        cr_readings_per_sample=str(sum(
            int(item["count_per_sample"]) for item in categories
            if item["category_id"] in cr_ids
        )),
        categories=categories,
        cr_category_ids=cr_ids,
        cr_selection_explicit=True,
        delta_r_enabled=profile.delta_r_enabled,
        step_overrides=overrides,
    )


def effective_point_count(
    profile: EffectiveConfirmedPointProfile,
    *, group_id: str, row_id: str, step_sequence: int, step_suffix_note: str,
    record_type: str,
) -> int:
    """Return the exact count for one step, inheriting the project default."""
    selected = (
        {str(item) for item in profile.cr_category_ids}
        if record_type == "cr" else None
    )
    matching = next((item for item in profile.step_overrides if (
        item.draft_group_id, item.draft_row_id, item.step_sequence, item.step_suffix_note
    ) == (group_id, row_id, step_sequence, step_suffix_note)), None)
    if matching is not None:
        return sum(
            parse_point_expression(item.point_expression).count
            for item in matching.categories
            if selected is None or item.prefix.casefold() in selected
        )
    return sum(
        parse_point_expression(str(item["point_expression"])).count
        for item in profile.categories
        if selected is None or str(item["category_id"]) in selected
    )
