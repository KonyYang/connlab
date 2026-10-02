"""IR/DWV record data and projections owned by the application boundary."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import date, datetime
from hashlib import sha256
import json
import re

from backend.application.confirmed_matrix_llcr_cr_record_projection import _point_profile_stages
from backend.application.matrix_editor_llcr_cr_record_projection import _draft_snapshot
from backend.application.matrix_test_points_authority import electrical_test_kind, validate_matrix_test_points
from backend.application.matrix_step_text_output import confirmed_step_text_lookup
from backend.modules.fee_evaluation.fee_default_fill_common import parse_primary_sample_quantity


@dataclass(frozen=True, slots=True)
class IrDwvEquipment:
    instrument: str = ""
    gage_id: str = ""
    last_calibration: date | datetime | str | None = None
    calibration_due: date | datetime | str | None = None


@dataclass(frozen=True, slots=True)
class IrDwvRecordSourceStep:
    """Keep Matrix intent separate from the template's result-unit defaults."""

    confirmed_step_quantity_id: str
    confirmed_row_id: str
    step_sequence: int
    step_suffix_note: str
    source_step: str
    test_item: str
    condition: str
    requirement: str


@dataclass(frozen=True, slots=True)
class IrDwvRecordStep:
    label: str
    ir_condition: str
    dwv_condition: str
    measurement_pairs: tuple[str, ...] = ()
    expected_fee_quantity: int | None = None
    description_is_override: bool = False
    ir_enabled: bool = True
    dwv_enabled: bool = True
    ir_source_step: IrDwvRecordSourceStep | None = None
    dwv_source_step: IrDwvRecordSourceStep | None = None


@dataclass(frozen=True, slots=True)
class IrDwvRecordGroup:
    label: str
    sample_count: int
    steps: tuple[IrDwvRecordStep, ...]


@dataclass(frozen=True, slots=True)
class IrDwvRecordProjection:
    request_number: str
    product_name: str
    tested_by: str = ""
    checked_by: str = ""
    approved_by: str = ""
    requestor: str = ""
    start_date: date | datetime | str | None = None
    finish_date: date | datetime | str | None = None
    ambient_temperature: str = ""
    relative_humidity: str = ""
    equipment: tuple[IrDwvEquipment, ...] = ()
    groups: tuple[IrDwvRecordGroup, ...] = ()


@dataclass(frozen=True, slots=True)
class IrDwvRecordDiagnostic:
    code: str
    message: str
    level: str = "info"


@dataclass(frozen=True, slots=True)
class MatrixEditorIrDwvRecordProjection:
    project_id: str
    confirmed_matrix_id: str
    confirmed_revision: int
    status: str
    workbook: IrDwvRecordProjection
    diagnostics: tuple[IrDwvRecordDiagnostic, ...]
    preview_fingerprint: str
    record_type: str = "ir_dwv"

    @property
    def sections(self):
        """The existing publication contract checks whether any blocks exist."""
        return self.workbook.groups


def build_matrix_editor_ir_dwv_record_projection(
    *, project_id, groups, rows, point_profile, point_overrides=(),
    step_text_overrides=(), header=None, source_fingerprint="", record_type="ir_dwv",
) -> MatrixEditorIrDwvRecordProjection:
    if record_type != "ir_dwv":
        raise ValueError("Record type must be ir_dwv.")
    profile, overrides = validate_matrix_test_points(point_profile, point_overrides)
    snapshot = _draft_snapshot(
        project_id=project_id, groups=groups, rows=rows,
        point_profile=profile, point_overrides=overrides,
        step_text_overrides=step_text_overrides,
    )
    return build_ir_dwv_record_projection(snapshot, header=header, source_fingerprint=source_fingerprint)


def build_ir_dwv_record_projection(snapshot, *, header=None, source_fingerprint=""):
    header = header or IrDwvRecordProjection("", "")
    diagnostics = []
    output_groups = []
    profile = snapshot.version.point_profile
    pairs = tuple(part.strip() for part in re.split(r"[,，;；、\r\n]", profile.electrical_point_pairs or "") if part.strip()) if profile else ()
    if not pairs:
        diagnostics.append(IrDwvRecordDiagnostic(
            "missing_measurement_pairs",
            "Enter explicit IR/DWV measurement pairs in Test points before generating a record. Legacy counts do not identify the test pairs.",
            "error",
        ))
    rows = {row.confirmed_row_id: row for row in snapshot.rows}
    text_lookup = confirmed_step_text_lookup(snapshot)
    for group in snapshot.groups:
        all_quantities = sorted(
            (item for item in snapshot.step_quantities if item.confirmed_group_id == group.confirmed_group_id),
            key=lambda item: (item.step_sequence, item.step_suffix_note or "", rows[item.confirmed_row_id].row_order),
        )
        matching = [item for item in all_quantities if electrical_test_kind(rows[item.confirmed_row_id].test_item)]
        if not matching:
            continue
        samples = parse_primary_sample_quantity(group.sample_quantity_expression)
        if samples is None or samples < 1 or samples != int(samples):
            diagnostics.append(IrDwvRecordDiagnostic("invalid_samples", f"{group.group_label}: sample quantity must begin with a positive whole number.", "error"))
            continue
        if "+" in group.sample_quantity_expression:
            diagnostics.append(IrDwvRecordDiagnostic("primary_sample_quantity", f"{group.group_label}: samples {group.sample_quantity_expression}; the first quantity ({int(samples)}) is used."))
        stages_by_identity = {}
        for kind in ("ir", "dwv"):
            selected = [item for item in matching if electrical_test_kind(rows[item.confirmed_row_id].test_item) == kind]
            stages = _point_profile_stages(selected, all_quantities, rows, kind, text_lookup)
            stages_by_identity.update({item.confirmed_step_quantity_id: stage for item, stage in zip(selected, stages, strict=True)})
        rounds = []
        identities = set()
        previous_electrical = None
        previous_operation = ""
        for item in all_quantities:
            kind = electrical_test_kind(rows[item.confirmed_row_id].test_item)
            if kind is None:
                previous_electrical = None
                previous_operation = rows[item.confirmed_row_id].test_item.strip()
                continue
            suffix = (item.step_suffix_note or "").strip()
            identity = (item.step_sequence, suffix, kind)
            if identity in identities:
                diagnostics.append(IrDwvRecordDiagnostic("ambiguous_step", f"{group.group_label}: more than one {kind.upper()} row identifies step {item.raw_token}.", "error"))
                continue
            identities.add(identity)
            if (previous_electrical is not None
                    and kind not in rounds[-1][0]
                    and suffix == (previous_electrical.step_suffix_note or "").strip()
                    and item.step_sequence - previous_electrical.step_sequence in (0, 1)):
                rounds[-1][0][kind] = item
                # A complete round cannot absorb a third electrical step.
                previous_electrical = None
            else:
                rounds.append(({kind: item}, previous_operation))
                previous_electrical = item
        steps = []
        for index, (quantities, preceding_operation) in enumerate(rounds):
            by_kind = {kind: stages_by_identity[item.confirmed_step_quantity_id]
                       for kind, item in quantities.items()}
            stages = tuple(by_kind.values())
            labels = tuple(dict.fromkeys(stage.label for stage in stages if stage.description_is_override))
            default_label = ("Initial" if index == 0 else "Final" if index == len(rounds) - 1
                             else f"After {preceding_operation}" if preceding_operation else f"Round {index + 1}")
            sources = {kind: IrDwvRecordSourceStep(
                confirmed_step_quantity_id=item.confirmed_step_quantity_id,
                confirmed_row_id=item.confirmed_row_id,
                step_sequence=item.step_sequence, step_suffix_note=(item.step_suffix_note or "").strip(),
                source_step=by_kind[kind].source_step, test_item=by_kind[kind].test_item,
                condition=by_kind[kind].condition, requirement=by_kind[kind].requirement,
            ) for kind, item in quantities.items()}
            steps.append(IrDwvRecordStep(
                label=" / ".join(labels) if labels else default_label,
                ir_condition=by_kind["ir"].condition if "ir" in by_kind else "",
                dwv_condition=by_kind["dwv"].condition if "dwv" in by_kind else "",
                measurement_pairs=pairs, expected_fee_quantity=int(samples) * len(pairs),
                description_is_override=any(stage.description_is_override for stage in stages),
                ir_enabled="ir" in by_kind, dwv_enabled="dwv" in by_kind,
                ir_source_step=sources.get("ir"), dwv_source_step=sources.get("dwv"),
            ))
        label = group.group_label.strip() or group.group_key.strip()
        output_groups.append(IrDwvRecordGroup(
            label=label if label.lower().startswith("group ") else f"Group {label}",
            sample_count=int(samples), steps=tuple(steps),
        ))
    if not output_groups:
        diagnostics.append(IrDwvRecordDiagnostic("no_steps", "Current Matrix does not contain selected IR/DWV steps.", "error"))
    blocked = any(item.level == "error" for item in diagnostics)
    workbook = replace(header, groups=() if blocked else tuple(output_groups))
    signature = sha256(json.dumps({
        "workbook": asdict(workbook), "diagnostics": [asdict(item) for item in diagnostics],
        "source": source_fingerprint, "matrix_id": snapshot.version.confirmed_matrix_id,
        "matrix_revision": snapshot.version.confirmed_revision,
    }, sort_keys=True, default=str).encode("utf-8")).hexdigest()
    return MatrixEditorIrDwvRecordProjection(
        project_id=snapshot.version.project_id,
        confirmed_matrix_id=snapshot.version.confirmed_matrix_id,
        confirmed_revision=snapshot.version.confirmed_revision,
        status="blocked" if blocked else "ready", workbook=workbook,
        diagnostics=tuple(diagnostics), preview_fingerprint=signature,
    )
