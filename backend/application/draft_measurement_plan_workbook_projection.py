"""Pure editable-revision projection for draft LLCR/CR workbooks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import re

from backend.application.matrix_record_sample_quantity import (
    parse_simple_positive_sample_count,
)

_POSITIVE_INTEGER = re.compile(r"^[1-9][0-9]*$")
_SUPPORTED_KINDS = {"llcr", "cr_specified_current"}


@dataclass(frozen=True, slots=True)
class DraftWorkbookDiagnostic:
    code: str
    severity: str
    message: str


@dataclass(frozen=True, slots=True)
class DraftWorkbookRow:
    sample_index: int
    contact_id: str
    contact_label: str


@dataclass(frozen=True, slots=True)
class DraftWorkbookSection:
    record_type: str
    group_label: str
    source_step: str
    sample_count: int
    readings_per_sample: int
    rows: tuple[DraftWorkbookRow, ...]


@dataclass(frozen=True, slots=True)
class DraftMeasurementPlanWorkbookProjection:
    project_id: str
    revision_id: str | None
    revision_sequence: int | None
    revision_state: str | None
    revision_fingerprint: str | None
    matrix_id: str | None
    matrix_revision: int | None
    matrix_binding_fingerprint: str | None
    status: str
    output_label: str | None
    sections: tuple[DraftWorkbookSection, ...]
    diagnostics: tuple[DraftWorkbookDiagnostic, ...]
    preview_fingerprint: str | None

    @property
    def row_count(self) -> int:
        return sum(len(section.rows) for section in self.sections)

    @property
    def generate_allowed(self) -> bool:
        return self.status in {"ready", "review_required"} and bool(
            self.preview_fingerprint
        )


def build_draft_measurement_plan_workbook_projection(
    workspace: dict[str, object],
) -> DraftMeasurementPlanWorkbookProjection:
    """Project only the current editable revision returned by the workspace boundary."""
    project_id = str(workspace.get("project_id") or "")
    revision_id = _text(workspace.get("editable_revision_id"))
    revision_state = _text(workspace.get("editable_revision_state"))
    revision_fingerprint = _text(workspace.get("editable_revision_fingerprint"))
    revision = _mapping(workspace.get("revision"))
    binding = _mapping(workspace.get("matrix_binding"))
    diagnostics: list[DraftWorkbookDiagnostic] = []
    if not project_id or not revision_id or revision_state not in {"draft", "needs_review"}:
        diagnostics.append(_diagnostic("editable_revision_required", "blocked", "Open the current editable measurement plan before previewing."))
    if not revision_fingerprint:
        diagnostics.append(_diagnostic("revision_fingerprint_missing", "blocked", "Editable measurement plan fingerprint is unavailable."))
    if not binding.get("base_confirmed_matrix_id") or not binding.get("matrix_binding_fingerprint"):
        diagnostics.append(_diagnostic("matrix_binding_missing", "blocked", "Measurement plan Matrix binding is unavailable."))

    sections: list[DraftWorkbookSection] = []
    for target in workspace.get("targets", []):
        if not isinstance(target, dict) or not _included_eligible_target(target):
            continue
        section, target_diagnostics = _section(target)
        diagnostics.extend(target_diagnostics)
        if section is not None:
            sections.append(section)

    status = _status(sections, diagnostics, workspace.get("impacts", []))
    label = "DRAFT" if status == "ready" else "NEEDS REVIEW" if status == "review_required" else None
    published_sections = tuple(sections) if label else ()
    fingerprint = _fingerprint(
        project_id, revision_id, revision, binding, status, label, published_sections, diagnostics
    ) if label else None
    return DraftMeasurementPlanWorkbookProjection(
        project_id=project_id,
        revision_id=revision_id or None,
        revision_sequence=_integer(revision.get("revision_sequence")),
        revision_state=revision_state or None,
        revision_fingerprint=revision_fingerprint or None,
        matrix_id=_text(binding.get("base_confirmed_matrix_id")) or None,
        matrix_revision=_integer(binding.get("base_matrix_revision")),
        matrix_binding_fingerprint=_text(binding.get("matrix_binding_fingerprint")) or None,
        status=status,
        output_label=label,
        sections=published_sections,
        diagnostics=tuple(diagnostics),
        preview_fingerprint=fingerprint,
    )


def _included_eligible_target(target: dict[str, object]) -> bool:
    return bool(target.get("eligible")) and bool(target.get("included")) and target.get("contact_kind") in _SUPPORTED_KINDS


def _section(target: dict[str, object]) -> tuple[DraftWorkbookSection | None, list[DraftWorkbookDiagnostic]]:
    sample_count = parse_simple_positive_sample_count(
        target.get("sample_quantity_expression")
    )
    if sample_count is None:
        return None, [_diagnostic("sample_quantity_not_positive_integer", "blocked", "Use a positive whole-number sample quantity.")]
    materialized: list[tuple[str, str, int]] = []
    prefixes: set[str] = set()
    diagnostics: list[DraftWorkbookDiagnostic] = []
    for family in target.get("families", []):
        if not isinstance(family, dict) or not family.get("included"):
            continue
        count = _positive_integer(family.get("count_per_sample"))
        if count is None:
            if _integer(family.get("count_per_sample")) == 0:
                continue
            diagnostics.append(_diagnostic("family_count_not_positive_integer", "blocked", "Use a positive whole-number count for each included contact family."))
            continue
        prefix = _text(family.get("record_prefix"))
        normalized = re.sub(r"[^A-Z0-9]+", "", prefix.upper())
        label = _text(family.get("record_label"))
        if not normalized or not label:
            diagnostics.append(_diagnostic("family_record_metadata_missing", "blocked", "Each included contact family needs a label and prefix."))
        elif normalized in prefixes:
            diagnostics.append(_diagnostic("normalized_prefix_collision", "blocked", "Contact prefixes must be unique within this Group-Step record section."))
        else:
            prefixes.add(normalized)
            materialized.append((prefix.upper(), label, count))
    readings = _integer(target.get("readings_per_sample"))
    if not materialized and not diagnostics:
        return None, []
    if readings is None or readings != sum(count for _, _, count in materialized):
        diagnostics.append(_diagnostic("readings_per_sample_mismatch", "blocked", "Readings per sample must equal the included contact-family count total."))
    if diagnostics:
        return None, diagnostics
    rows = tuple(
        DraftWorkbookRow(sample, f"{prefix}{index}", label)
        for sample in range(1, sample_count + 1)
        for prefix, label, count in materialized
        for index in range(1, count + 1)
    )
    return DraftWorkbookSection(
        record_type=str(target["contact_kind"]),
        group_label=_text(target.get("group_label")),
        source_step=f"{target.get('step_sequence', '')}{_text(target.get('step_suffix_note'))}",
        sample_count=sample_count,
        readings_per_sample=readings,
        rows=rows,
    ), []


def _status(sections: list[DraftWorkbookSection], diagnostics: list[DraftWorkbookDiagnostic], impacts: object) -> str:
    if any(item.severity == "blocked" for item in diagnostics):
        return "blocked"
    if not sections:
        return "empty"
    if any(isinstance(item, dict) and item.get("severity") == "review_required" and item.get("resolution_state") == "open" for item in impacts if isinstance(impacts, list)):
        return "review_required"
    return "ready"


def _fingerprint(project_id: str, revision_id: str, revision: dict[str, object], binding: dict[str, object], status: str, label: str | None, sections: tuple[DraftWorkbookSection, ...], diagnostics: list[DraftWorkbookDiagnostic]) -> str:
    payload = {"contract": "draft-workbook:v1", "project_id": project_id, "revision_id": revision_id, "revision": revision, "binding": binding, "status": status, "label": label, "sections": [asdict(item) for item in sections], "diagnostics": [asdict(item) for item in diagnostics]}
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _diagnostic(code: str, severity: str, message: str) -> DraftWorkbookDiagnostic:
    return DraftWorkbookDiagnostic(code, severity, message)


def _mapping(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _text(value: object) -> str:
    return str(value or "").strip()


def _integer(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _positive_integer(value: object) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool):
        return value if value > 0 else None
    text = _text(value)
    return int(text) if _POSITIVE_INTEGER.fullmatch(text) else None
