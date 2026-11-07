"""Project-specific report evidence, not a second test authority or release workflow."""
from dataclasses import dataclass


SOURCE_ROLES = frozenset({"original", "layout_reference", "specification", "temperature", "cr", "mechanical", "photo", "evidence", "tools_result_package"})
MAPPING_KINDS = frozenset({"specification", "identity", "temperature", "cr", "mechanical", "photo", "acceptance"})


class ReportAuthoringConflict(ValueError):
    """The reviewed evidence changed; reread before making a new decision."""


@dataclass(frozen=True)
class ReportSource:
    source_id: str
    role: str
    file_name: str
    sha256: str
    size_bytes: int
    created_at: str
    report_dl: str = ""
    source_locator: str = ""


@dataclass(frozen=True)
class ReportMapping:
    mapping_id: str
    source_id: str
    kind: str
    label: str
    source_locator: str
    value: str = ""
    status: str = "pending"
    reason: str = ""
    group_id: str = ""
    row_id: str = ""
    step_token: str = ""
    sample_ids: tuple[str, ...] = ()
    matrix_id: str = ""
    confirmed_by: str = ""
    confirmed_at: str = ""
    report_text: str = ""
    fact_role: str = "unspecified"
    report_target: dict | None = None


@dataclass(frozen=True)
class ReportAuthoringState:
    project_id: str
    revision: int = 0
    sources: tuple[ReportSource, ...] = ()
    mappings: tuple[ReportMapping, ...] = ()
    base_source_id: str | None = None
    outputs: tuple[dict, ...] = ()
    results: tuple[dict, ...] = ()
    customer_outputs: tuple[dict, ...] = ()
    assembly_plan: dict | None = None
    delivery: dict | None = None


def validate_mapping(mapping: ReportMapping) -> None:
    if mapping.fact_role not in {'unspecified', 'specification_number', 'revision', 'revision_date', 'authorization_date'}:
        raise ValueError('Choose the fact role from the supported specification fields.')
    if mapping.status == 'confirmed' and mapping.report_text and mapping.fact_role in {'revision_date', 'authorization_date'} and not mapping.report_target:
        raise ValueError('Select the exact report location for this date; authorization and revision dates are different facts.')
    if mapping.kind not in MAPPING_KINDS or mapping.status not in {"pending", "confirmed"}:
        raise ValueError("Choose a supported mapping type and decision state.")
    if not mapping.label.strip() or not mapping.source_locator.strip():
        raise ValueError("A mapping needs a label and an exact source location.")
    if mapping.status == "confirmed":
        if not mapping.value.strip() or not mapping.reason.strip():
            raise ValueError("Confirm the value and explain the supporting evidence; otherwise keep it pending.")
        if mapping.kind in {"temperature", "cr", "mechanical", "acceptance"} and not all((mapping.group_id, mapping.row_id, mapping.step_token)):
            raise ValueError("Confirm the Matrix Group and Step for this result or acceptance decision.")
