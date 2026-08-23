"""Project active Confirmed Matrix contact plans into specialized record rows."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import re

from backend.domain import ConfirmedMatrixSnapshot, ConfirmedMatrixStepQuantity
from backend.application.contact_point_profile_expression import (
    ContactPointExpressionError,
    parse_point_expression,
)
from backend.application.matrix_record_sample_quantity import (
    resolve_matrix_record_sample_count,
)

_POSITIVE_INTEGER = re.compile(r"^[1-9][0-9]*$")
_ZERO = re.compile(r"^0$")
_SUPPORTED_KINDS = {"llcr", "cr_specified_current"}
_RECORD_TYPES = {"llcr", "cr"}
_CURRENT = re.compile(r"(?<![A-Z0-9.])([0-9]+(?:\.[0-9]+)?)\s*(MA|A)\b", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class LlcrCrRecordDiagnostic:
    """One safe, scoped reason a contact-plan target cannot generate."""

    code: str
    severity: str
    message: str
    confirmed_group_id: str | None = None
    confirmed_row_id: str | None = None
    step_sequence: int | None = None
    family_id: str | None = None
    normalized_prefix: str | None = None
    first_family_id: str | None = None
    first_family_label: str | None = None
    second_family_id: str | None = None
    second_family_label: str | None = None


@dataclass(frozen=True, slots=True)
class LlcrCrRecordRow:
    """One manual-entry row in a generated specialized workbook section."""

    sample_index: int
    contact_id: str
    contact_label: str


@dataclass(frozen=True, slots=True)
class LlcrCrRecordStage:
    """One Matrix-derived measurement stage within a Group record block."""

    label: str
    source_step: str
    confirmed_row_id: str
    test_item: str
    condition: str
    requirement: str
    test_current_ampere: str | None = None


@dataclass(frozen=True, slots=True)
class LlcrCrRecordSection:
    """One confirmed Group-Step/type block in a specialized workbook."""

    record_type: str
    confirmed_group_id: str
    confirmed_row_id: str
    step_sequence: int
    step_suffix_note: str
    group_label: str
    source_step: str
    sample_count: int
    readings_per_sample: int
    rows: tuple[LlcrCrRecordRow, ...]
    category_id: str | None = None
    category_label: str | None = None
    point_expression: str | None = None
    stages: tuple[LlcrCrRecordStage, ...] = ()
    record_prefix: str | None = None


@dataclass(frozen=True, slots=True)
class LlcrCrRecordProjection:
    """Read-only projection used by preview and generation services."""

    project_id: str
    confirmed_matrix_id: str
    confirmed_revision: int
    status: str
    sections: tuple[LlcrCrRecordSection, ...]
    diagnostics: tuple[LlcrCrRecordDiagnostic, ...]
    preview_fingerprint: str | None
    measurement_plan_revision_id: str | None = None
    measurement_plan_revision_sequence: int | None = None
    effective_measurement_plan_status: str | None = None
    omission_diagnostics: tuple[str, ...] = ()
    record_type: str | None = None
    point_profile_revision_id: str | None = None
    point_profile_revision_sequence: int | None = None
    point_profile_fingerprint: str | None = None
    delta_r_enabled: bool = True
    matrix_source: str = "confirmed"

    @property
    def row_count(self) -> int:
        return sum(len(section.rows) for section in self.sections)


def build_point_profile_llcr_cr_record_projection(
    snapshot: ConfirmedMatrixSnapshot,
    effective_profile,
    record_type: str,
) -> LlcrCrRecordProjection:
    """Project one independent LLCR or CR workbook from confirmed authorities."""
    if record_type not in _RECORD_TYPES:
        raise ValueError("Record type must be llcr or cr.")
    groups = {group.confirmed_group_id: group for group in snapshot.groups}
    rows = {row.confirmed_row_id: row for row in snapshot.rows}
    row_order = {row.confirmed_row_id: row.row_order for row in snapshot.rows}
    quantities_by_group: dict[str, list[ConfirmedMatrixStepQuantity]] = {}
    for quantity in snapshot.step_quantities:
        quantities_by_group.setdefault(quantity.confirmed_group_id, []).append(quantity)
    for quantities in quantities_by_group.values():
        quantities.sort(
            key=lambda item: (
                item.step_sequence,
                row_order.get(item.confirmed_row_id, 1_000_000),
                _suffix_identity(item.step_suffix_note),
            )
        )

    targets: list[tuple[object, list[ConfirmedMatrixStepQuantity]]] = []
    for group in sorted(snapshot.groups, key=lambda item: item.group_order):
        group_quantities = quantities_by_group.get(group.confirmed_group_id, [])
        matching = [
            quantity
            for quantity in group_quantities
            if _matrix_record_type(rows.get(quantity.confirmed_row_id), quantity) == record_type
        ]
        if matching:
            targets.append((group, matching))
    if not targets:
        return _point_profile_projection(
            snapshot, effective_profile, record_type, "empty", (), (), None
        )
    if not getattr(effective_profile, "is_usable", False):
        message = getattr(effective_profile, "message", None) or (
            "Confirm Point Profile before generating test records."
        )
        diagnostic = LlcrCrRecordDiagnostic(
            code="point_profile_not_confirmed", severity="blocked", message=message
        )
        return _point_profile_projection(
            snapshot, effective_profile, record_type, "blocked", (), (diagnostic,), None
        )

    categories = tuple(
        category for category in effective_profile.categories if bool(category.get("included", True))
    )
    if record_type == "cr" and effective_profile.cr_category_ids:
        selected = set(effective_profile.cr_category_ids)
        categories = tuple(
            category for category in categories if str(category.get("category_id")) in selected
        )
    sections: list[LlcrCrRecordSection] = []
    diagnostics: list[LlcrCrRecordDiagnostic] = []
    for group, matching in targets:
        sample_count = resolve_matrix_record_sample_count(
            group.sample_quantity_expression,
            group.sample_note,
            record_type,
        )
        if sample_count is None:
            diagnostics.append(
                LlcrCrRecordDiagnostic(
                    code="sample_quantity_not_positive_integer",
                    severity="review_required",
                    message=f"Confirm a positive whole-number sample quantity for {group.group_label}.",
                    confirmed_group_id=group.confirmed_group_id,
                )
            )
            continue
        stages = _point_profile_stages(
            matching,
            quantities_by_group.get(group.confirmed_group_id, []),
            rows,
            record_type,
        )
        for category in categories:
            try:
                points = parse_point_expression(category.get("point_expression")).points
            except ContactPointExpressionError as exc:
                diagnostics.append(
                    LlcrCrRecordDiagnostic(
                        code="point_expression_invalid",
                        severity="blocked",
                        message=str(exc),
                        confirmed_group_id=group.confirmed_group_id,
                        family_id=str(category.get("category_id") or ""),
                    )
                )
                continue
            prefix = str(category.get("record_prefix") or "").strip().upper()
            label = str(category.get("label") or prefix).strip()
            materialized_rows = tuple(
                LlcrCrRecordRow(
                    sample_index=sample,
                    contact_id=f"{prefix}{point}",
                    contact_label=label,
                )
                for sample in range(1, sample_count + 1)
                for point in points
            )
            sections.append(
                LlcrCrRecordSection(
                    record_type=record_type,
                    confirmed_group_id=group.confirmed_group_id,
                    confirmed_row_id=matching[0].confirmed_row_id,
                    step_sequence=matching[0].step_sequence,
                    step_suffix_note=_suffix_identity(matching[0].step_suffix_note),
                    group_label=group.group_label.strip(),
                    source_step=", ".join(stage.source_step for stage in stages),
                    sample_count=sample_count,
                    readings_per_sample=len(points),
                    rows=materialized_rows,
                    category_id=str(category.get("category_id") or ""),
                    category_label=label,
                    point_expression=str(category.get("point_expression") or ""),
                    stages=stages,
                    record_prefix=prefix,
                )
            )
    status = _projection_status(sections, diagnostics)
    fingerprint = (
        _point_profile_fingerprint(snapshot, effective_profile, record_type, sections, diagnostics)
        if status == "ready"
        else None
    )
    return _point_profile_projection(
        snapshot,
        effective_profile,
        record_type,
        status,
        tuple(sections) if status == "ready" else (),
        tuple(diagnostics),
        fingerprint,
    )


def build_llcr_cr_record_projection(
    snapshot: ConfirmedMatrixSnapshot,
) -> LlcrCrRecordProjection:
    """Build deterministic rows solely from one active confirmed snapshot."""
    groups = {group.confirmed_group_id: group for group in snapshot.groups}
    rows = {row.confirmed_row_id: row for row in snapshot.rows}
    group_order = {group.confirmed_group_id: group.group_order for group in snapshot.groups}
    row_order = {row.confirmed_row_id: row.row_order for row in snapshot.rows}
    candidates = sorted(
        snapshot.step_quantities,
        key=lambda quantity: (
            group_order.get(quantity.confirmed_group_id, 1_000_000),
            row_order.get(quantity.confirmed_row_id, 1_000_000),
            quantity.step_sequence,
            _suffix_identity(quantity.step_suffix_note),
        ),
    )

    sections: list[LlcrCrRecordSection] = []
    diagnostics: list[LlcrCrRecordDiagnostic] = []
    for quantity in candidates:
        plan = quantity.contact_plan
        if plan is None or plan.contact_kind not in _SUPPORTED_KINDS or not plan.included:
            continue
        group = groups.get(quantity.confirmed_group_id)
        row = rows.get(quantity.confirmed_row_id)
        if group is None or row is None:
            diagnostics.append(_diagnostic(quantity, "invalid_confirmed_lineage", "blocked", "Confirmed Matrix contact target is incomplete."))
            continue
        section, section_diagnostics = _project_section(quantity, group.group_label, group.sample_quantity_expression)
        diagnostics.extend(section_diagnostics)
        if section is not None:
            sections.append(section)

    status = _projection_status(sections, diagnostics)
    fingerprint = _fingerprint(snapshot, sections, diagnostics) if status == "ready" else None
    return LlcrCrRecordProjection(
        project_id=snapshot.version.project_id,
        confirmed_matrix_id=snapshot.version.confirmed_matrix_id,
        confirmed_revision=snapshot.version.confirmed_revision,
        status=status,
        sections=tuple(sections) if status == "ready" else (),
        diagnostics=tuple(diagnostics),
        preview_fingerprint=fingerprint,
    )


def _project_section(
    quantity: ConfirmedMatrixStepQuantity,
    group_label: str,
    sample_expression: str,
) -> tuple[LlcrCrRecordSection | None, list[LlcrCrRecordDiagnostic]]:
    sample_count = _positive_integer(sample_expression)
    if sample_count is None:
        return None, [_diagnostic(quantity, "sample_quantity_not_positive_integer", "review_required", "Confirm a positive whole-number sample quantity.")]
    plan = quantity.contact_plan
    assert plan is not None
    materialized: list[tuple[str, str, int]] = []
    normalized_prefixes: dict[str, tuple[str, str]] = {}
    diagnostics: list[LlcrCrRecordDiagnostic] = []
    for family in plan.families:
        if not family.included:
            continue
        count = _positive_integer(family.count_per_sample)
        if count is None:
            if _ZERO.fullmatch(_text(family.count_per_sample)):
                continue
            diagnostics.append(_diagnostic(quantity, "family_count_not_positive_integer", "review_required", "Confirm a positive whole-number count for each included contact family.", family_id=family.family_id))
            continue
        normalized_prefix = _normalized_prefix(family.record_prefix)
        if not normalized_prefix:
            diagnostics.append(_diagnostic(quantity, "record_prefix_missing", "blocked", "Confirm a record prefix for each materialized contact family.", family_id=family.family_id))
            continue
        prior_family = normalized_prefixes.get(normalized_prefix)
        if prior_family is not None:
            diagnostics.append(
                _diagnostic(
                    quantity,
                    "normalized_prefix_collision",
                    "blocked",
                    "Contact prefixes must be unique within this Group-Step record section.",
                    family_id=family.family_id,
                    normalized_prefix=normalized_prefix,
                    first_family_id=prior_family[0],
                    first_family_label=prior_family[1],
                    second_family_id=family.family_id,
                    second_family_label=family.family_label.strip(),
                )
            )
            continue
        normalized_prefixes[normalized_prefix] = (
            family.family_id,
            family.family_label.strip(),
        )
        materialized.append((family.record_prefix.strip().upper(), family.record_label.strip(), count))

    if diagnostics:
        return None, diagnostics
    readings_per_sample = _positive_integer(plan.readings_per_sample)
    total_count = sum(count for _, _, count in materialized)
    if readings_per_sample is None or readings_per_sample != total_count:
        return None, [_diagnostic(quantity, "readings_per_sample_mismatch", "review_required", "Confirmed readings per sample must equal the included contact-family count total.")]
    rows = tuple(
        LlcrCrRecordRow(sample_index=sample, contact_id=f"{prefix}{index}", contact_label=label)
        for sample in range(1, sample_count + 1)
        for prefix, label, count in materialized
        for index in range(1, count + 1)
    )
    return (
        LlcrCrRecordSection(
            record_type=plan.contact_kind,
            confirmed_group_id=quantity.confirmed_group_id,
            confirmed_row_id=quantity.confirmed_row_id,
            step_sequence=quantity.step_sequence,
            step_suffix_note=_suffix_identity(quantity.step_suffix_note),
            group_label=group_label.strip(),
            source_step=_source_step(quantity),
            sample_count=sample_count,
            readings_per_sample=readings_per_sample,
            rows=rows,
        ),
        [],
    )


def _projection_status(
    sections: list[LlcrCrRecordSection], diagnostics: list[LlcrCrRecordDiagnostic]
) -> str:
    if any(diagnostic.severity == "blocked" for diagnostic in diagnostics):
        return "blocked"
    if diagnostics:
        return "review_required"
    return "ready" if sections else "empty"


def _diagnostic(
    quantity: ConfirmedMatrixStepQuantity,
    code: str,
    severity: str,
    message: str,
    *,
    family_id: str | None = None,
    normalized_prefix: str | None = None,
    first_family_id: str | None = None,
    first_family_label: str | None = None,
    second_family_id: str | None = None,
    second_family_label: str | None = None,
) -> LlcrCrRecordDiagnostic:
    return LlcrCrRecordDiagnostic(
        code=code,
        severity=severity,
        message=message,
        confirmed_group_id=quantity.confirmed_group_id,
        confirmed_row_id=quantity.confirmed_row_id,
        step_sequence=quantity.step_sequence,
        family_id=family_id,
        normalized_prefix=normalized_prefix,
        first_family_id=first_family_id,
        first_family_label=first_family_label,
        second_family_id=second_family_id,
        second_family_label=second_family_label,
    )


def _fingerprint(
    snapshot: ConfirmedMatrixSnapshot,
    sections: list[LlcrCrRecordSection],
    diagnostics: list[LlcrCrRecordDiagnostic],
) -> str:
    payload = {
        "confirmed_matrix_id": snapshot.version.confirmed_matrix_id,
        "confirmed_revision": snapshot.version.confirmed_revision,
        "sections": [asdict(section) for section in sections],
        "diagnostics": [asdict(diagnostic) for diagnostic in diagnostics],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()


def _point_profile_projection(
    snapshot: ConfirmedMatrixSnapshot,
    effective_profile,
    record_type: str,
    status: str,
    sections: tuple[LlcrCrRecordSection, ...],
    diagnostics: tuple[LlcrCrRecordDiagnostic, ...],
    fingerprint: str | None,
) -> LlcrCrRecordProjection:
    return LlcrCrRecordProjection(
        project_id=snapshot.version.project_id,
        confirmed_matrix_id=snapshot.version.confirmed_matrix_id,
        confirmed_revision=snapshot.version.confirmed_revision,
        status=status,
        sections=sections,
        diagnostics=diagnostics,
        preview_fingerprint=fingerprint,
        record_type=record_type,
        point_profile_revision_id=getattr(effective_profile, "revision_id", None),
        point_profile_revision_sequence=getattr(effective_profile, "revision_sequence", None),
        point_profile_fingerprint=getattr(effective_profile, "fingerprint", None),
        delta_r_enabled=(
            bool(getattr(effective_profile, "delta_r_enabled", True))
            if record_type == "llcr"
            else False
        ),
    )


def _point_profile_stages(
    matching: list[ConfirmedMatrixStepQuantity],
    all_quantities: list[ConfirmedMatrixStepQuantity],
    rows: dict[str, object],
    record_type: str,
) -> tuple[LlcrCrRecordStage, ...]:
    stages: list[LlcrCrRecordStage] = []
    for index, quantity in enumerate(matching):
        row = rows.get(quantity.confirmed_row_id)
        if row is None:
            continue
        if index == 0:
            label = "Initial"
        elif index == len(matching) - 1:
            label = "Final"
        else:
            previous = _previous_non_measurement(quantity, all_quantities, rows)
            previous_label = getattr(previous, "test_item", "") if previous else ""
            label = f"After {previous_label.strip() or f'Step {quantity.step_sequence - 1}'}"
        stages.append(
            LlcrCrRecordStage(
                label=label,
                source_step=_source_step(quantity),
                confirmed_row_id=quantity.confirmed_row_id,
                test_item=str(getattr(row, "test_item", "") or "").strip(),
                condition=str(getattr(row, "condition", "") or "").strip(),
                requirement=str(getattr(row, "requirement", "") or "").strip(),
                test_current_ampere=(
                    _test_current_ampere(str(getattr(row, "condition", "") or ""))
                    if record_type == "cr"
                    else None
                ),
            )
        )
    return tuple(stages)


def _previous_non_measurement(
    current: ConfirmedMatrixStepQuantity,
    all_quantities: list[ConfirmedMatrixStepQuantity],
    rows: dict[str, object],
):
    for quantity in reversed(all_quantities):
        if quantity.step_sequence >= current.step_sequence:
            continue
        row = rows.get(quantity.confirmed_row_id)
        if _matrix_record_type(row, quantity) is None:
            return row
    return None


def _matrix_record_type(row, quantity: ConfirmedMatrixStepQuantity) -> str | None:
    text_value = re.sub(
        r"[^A-Z0-9]+", " ", str(getattr(row, "test_item", "") or "").upper()
    ).strip()
    if "LLCR" in text_value or (
        "CONTACT RESISTANCE" in text_value and "LOW LEVEL" in text_value
    ):
        return "llcr"
    if text_value == "CR" or "CONTACT RESISTANCE" in text_value:
        return "cr"
    plan = quantity.contact_plan
    if plan is not None and plan.included:
        if plan.contact_kind == "llcr":
            return "llcr"
        if plan.contact_kind == "cr_specified_current":
            return "cr"
    return None


def _test_current_ampere(condition: str) -> str | None:
    match = _CURRENT.search(condition)
    if match is None:
        return None
    try:
        value = Decimal(match.group(1))
    except InvalidOperation:
        return None
    if match.group(2).upper() == "MA":
        value /= Decimal("1000")
    return format(value.normalize(), "f")


def _point_profile_fingerprint(
    snapshot: ConfirmedMatrixSnapshot,
    effective_profile,
    record_type: str,
    sections: list[LlcrCrRecordSection],
    diagnostics: list[LlcrCrRecordDiagnostic],
) -> str:
    payload = {
        "record_type": record_type,
        "confirmed_matrix_id": snapshot.version.confirmed_matrix_id,
        "confirmed_revision": snapshot.version.confirmed_revision,
        "point_profile_revision_id": effective_profile.revision_id,
        "point_profile_fingerprint": effective_profile.fingerprint,
        "delta_r_enabled": bool(effective_profile.delta_r_enabled),
        "sections": [asdict(section) for section in sections],
        "diagnostics": [asdict(diagnostic) for diagnostic in diagnostics],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()


def _positive_integer(value: str | None) -> int | None:
    text = _text(value)
    return int(text) if _POSITIVE_INTEGER.fullmatch(text) else None


def _normalized_prefix(value: str | None) -> str:
    return re.sub(r"[^A-Z0-9]+", "", _text(value).upper())


def _source_step(quantity: ConfirmedMatrixStepQuantity) -> str:
    token = _text(quantity.raw_token) or str(quantity.step_sequence)
    suffix = _suffix_identity(quantity.step_suffix_note)
    return f"{token}({suffix})" if suffix else token


def _suffix_identity(value: str | None) -> str:
    return _text(value)


def _text(value: str | None) -> str:
    return (value or "").strip()
