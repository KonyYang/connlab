"""Bounded report evidence edits; source paths and authority IDs are server owned."""
from typing import Annotated, Literal
from pydantic import BaseModel, Field, ConfigDict
from backend.api.temperature_schemas import DataSelectionRequest


class FactTarget(BaseModel):
    model_config = ConfigDict(extra='forbid')
    part: str = Field(pattern=r'^word/(document|header\d+|footer\d+)\.xml$')
    paragraph: int = Field(ge=0, le=100000)
    sha256: str = Field(pattern=r'^[0-9a-f]{64}$')


class MappingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=0)
    mapping_id: str = Field(default="", max_length=64)
    source_id: str = Field(min_length=1, max_length=64)
    kind: Literal["specification", "identity", "temperature", "cr", "mechanical", "photo", "acceptance"]
    label: str = Field(min_length=1, max_length=500)
    source_locator: str = Field(min_length=1, max_length=1000)
    value: str = Field(default="", max_length=5000)
    status: Literal["pending", "confirmed"] = "pending"
    reason: str = Field(default="", max_length=5000)
    group_id: str = Field(default="", max_length=128)
    row_id: str = Field(default="", max_length=128)
    step_token: str = Field(default="", max_length=64)
    sample_ids: list[str] = Field(default_factory=list, max_length=1000)
    confirmed_by: str = Field(default="Lab User", min_length=1, max_length=255)
    report_text: str = Field(default="", max_length=5000)
    fact_role: Literal['unspecified', 'specification_number', 'revision', 'revision_date', 'authorization_date'] = 'unspecified'
    report_target: FactTarget | None = None


class SelectBaseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=0)
    source_id: str = Field(min_length=1, max_length=64)


class AdoptWorkingCopyRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_revision: int = Field(ge=0)
    source_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    source_mode: Literal['official', 'download_draft']


class WorkingLlcrRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_revision: int = Field(ge=0)
    expected_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    dataset_revision_id: str = Field(min_length=1, max_length=128)


CellAddress = Annotated[str, Field(pattern=r'^[A-Za-z]{1,3}[1-9][0-9]{0,4}$')]


class ElectricalRecordSelection(BaseModel):
    model_config = ConfigDict(extra='forbid')
    stage: str = Field(min_length=1, max_length=200)
    measurement: Literal['ir', 'dwv']
    cells: dict[Literal['sample', 'pair', 'value', 'breakdown'], CellAddress]
    unit: Literal['MΩ', 'GΩ', 'Ω', 'µA', 'μA', 'uA', 'mA', 'nA']
    voltage_v: str = Field(default='', max_length=40)
    duration_s: str = Field(default='', max_length=40)
    condition_locator: str = Field(default='', max_length=500)


class ResistanceRecordSelection(BaseModel):
    model_config = ConfigDict(extra='forbid')
    stage: str = Field(min_length=1, max_length=200)
    quantity: Literal['absolute', 'delta', 'delta_from_absolute']
    cells: dict[Literal['sample', 'pair', 'value', 'baseline'], CellAddress]
    unit: Literal['mΩ', 'Ω']


class ElectricalSelection(BaseModel):
    model_config = ConfigDict(extra='forbid')
    type: Literal['electrical']
    records: list[ElectricalRecordSelection] = Field(min_length=1, max_length=500)
    selection_confirmed: bool = False


class ResistanceSelection(BaseModel):
    model_config = ConfigDict(extra='forbid')
    type: Literal['resistance_stages']
    records: list[ResistanceRecordSelection] = Field(min_length=1, max_length=500)
    selection_confirmed: bool = False


class ResultAdoption(BaseModel):
    model_config = ConfigDict(extra='forbid')
    report_identity: str = Field(min_length=1, max_length=500)
    source_version: str = Field(min_length=1, max_length=200)
    source_locator: str = Field(min_length=1, max_length=1000)
    adopted_scope: str = Field(min_length=1, max_length=3000)
    applicability_reason: str = Field(default='', max_length=5000)
    adverse_observations: str = Field(default='', max_length=5000)
    source_observations: str = Field(default='', max_length=5000)
    confirmed: bool = False
    customer_reference_allowed: bool = False


class LinkedRegionSelection(BaseModel):
    model_config = ConfigDict(extra='forbid')
    start: int = Field(ge=0, le=100000)
    end: int = Field(ge=0, le=100000)
    freeze_external_charts: bool = False


class ResultImportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=0)
    source_id: str = Field(min_length=1, max_length=64)
    kind: Literal["temperature", "cr", "mechanical", "mechanical_qualitative", 'electrical', 'resistance_stages', 'external_reference', 'linked_temperature']
    semantic_selection: Annotated[ElectricalSelection | ResistanceSelection, Field(discriminator='type')] | None = None
    adoption: ResultAdoption | None = None
    linked_region: LinkedRegionSelection | None = None
    package_entry_id: str | None = Field(default=None, min_length=1, max_length=128)
    source_project_confirmed: bool = False
    sheet_name: str = Field(default="", max_length=255)
    start_row: int = Field(default=2, ge=1, le=20000)
    end_row: int = Field(default=2, ge=1, le=20000)
    columns: dict[Literal["sample", "record_id", "color", "voltage", "current", "initial_mohm", "value", "hold_seconds"], int] = Field(default_factory=dict)
    sample_ids: list[str] = Field(default_factory=list, max_length=256)
    unit: Literal["mV", "V", "N"] = "mV"
    quantity: Literal["absolute", "delta"] = "absolute"
    test_type: Literal["mating", "unmating", "retention"] = "retention"
    measurement_kind: Literal["peak", "hold"] = "peak"
    temperature_selection: DataSelectionRequest | None = None
    zero_intercept: bool = True
    acknowledge_warnings: bool = False
    group_id: str = Field(min_length=1, max_length=128)
    row_id: str = Field(min_length=1, max_length=128)
    step_token: str = Field(min_length=1, max_length=64)
    outcome: Literal["pending", "pass", "fail", "not_applicable"] = "pending"
    acceptance_reason: str = Field(default="", max_length=5000)
    confirmed_by: str = Field(default="Lab User", min_length=1, max_length=255)
    preview_sha256: str | None = Field(default=None, min_length=64, max_length=64)


class FactUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=0)
    output_id: str = Field(min_length=1, max_length=64)
    mapping_ids: list[str] = Field(min_length=1, max_length=100)
    preview_sha256: str | None = Field(default=None, min_length=64, max_length=64)


class ResultUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=0)
    output_id: str = Field(min_length=1, max_length=64)
    output_sha256: str = Field(min_length=64, max_length=64)
    result_id: str = Field(min_length=1, max_length=64)
    result_table: int = Field(ge=0, le=10000)
    result_row: int = Field(ge=1, le=20000)
    appendix_table: int | None = Field(default=None, ge=0, le=10000)
    appendix_title: str = Field(default='', max_length=500)
    evidence_start: int | None = Field(default=None, ge=0, le=20000)
    evidence_end: int | None = Field(default=None, ge=0, le=20000)
    evidence_selection_confirmed: bool = False


class PhotoAssignment(BaseModel):
    model_config = ConfigDict(extra='forbid')
    slot_id: str = Field(min_length=1, max_length=500)
    source_id: str = Field(min_length=1, max_length=64)
    crop_mode: Literal['preserve', 'centre_crop'] = 'preserve'
    accept_slot_transform: bool = False


class PhotoUpdateRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_revision: int = Field(ge=0)
    output_id: str = Field(min_length=1, max_length=64)
    output_sha256: str = Field(min_length=64, max_length=64)
    assignments: list[PhotoAssignment] = Field(min_length=1, max_length=100)


class InventorySelection(BaseModel):
    model_config = ConfigDict(extra='forbid')
    relative_path: str = Field(min_length=1, max_length=2000)
    file_token: str = Field(pattern=r'^[0-9a-f]{64}$')
    role: Literal['original', 'layout_reference', 'specification', 'temperature', 'cr', 'mechanical', 'photo', 'evidence', 'tools_result_package']


class InventoryRetainRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_revision: int = Field(ge=0)
    root_token: str = Field(pattern=r'^[0-9a-f]{64}$')
    items: list[InventorySelection] = Field(min_length=1, max_length=50)


class BatchResultSelection(BaseModel):
    model_config = ConfigDict(extra='forbid')
    result_id: str = Field(min_length=1, max_length=64)
    result_table: int | None = Field(default=None, ge=0, le=10000)
    result_row: int | None = Field(default=None, ge=1, le=20000)
    appendix_table: int | None = Field(default=None, ge=0, le=10000)
    appendix_title: str = Field(default='', max_length=500)
    evidence_start: int | None = Field(default=None, ge=0, le=20000)
    evidence_end: int | None = Field(default=None, ge=0, le=20000)
    evidence_selection_confirmed: bool = False


class AssemblyPreviewRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_revision: int = Field(ge=0)
    output_id: str = Field(min_length=1, max_length=64)
    output_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    mapping_ids: list[str] = Field(default_factory=list, max_length=100)
    results: list[BatchResultSelection] = Field(default_factory=list, max_length=100)
    assignments: list[PhotoAssignment] = Field(default_factory=list, max_length=100)
    llcr_dataset_id: str | None = Field(default=None, min_length=1, max_length=100)
    photo_plan_id: str | None = Field(default=None, pattern=r'^[0-9a-f]{32}$')
    renumber_figures: bool = False


class DocumentReviewRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_revision: int = Field(ge=0)
    output_id: str = Field(min_length=1, max_length=64)
    output_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')


class ConfirmedPhotoAssignment(PhotoAssignment):
    scope: Literal['step', 'sample_overview', 'project_context'] = 'step'
    group_id: str = Field(default='', max_length=128)
    row_id: str = Field(default='', max_length=128)
    step_token: str = Field(default='', max_length=64)
    sample_ids: list[str] = Field(default_factory=list, max_length=256)
    stage: str = Field(min_length=1, max_length=100)
    reason: str = Field(min_length=1, max_length=2000)
    reuse_reason: str = Field(default='', max_length=2000)
    accept_context_change: bool = False


class PhotoPlanRequest(DocumentReviewRequest):
    review_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    confirmed_by: str = Field(min_length=1, max_length=255)
    assignments: list[ConfirmedPhotoAssignment] = Field(min_length=1, max_length=100)


class RegionDecision(BaseModel):
    model_config = ConfigDict(extra='forbid')
    region_id: str = Field(min_length=1, max_length=300)
    region_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    source_id: str = Field(min_length=1, max_length=64)
    locator: str = Field(min_length=1, max_length=2000)
    reason: str = Field(min_length=1, max_length=2000)


class RegionReviewRequest(DocumentReviewRequest):
    review_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    confirmed_by: str = Field(min_length=1, max_length=255)
    decisions: list[RegionDecision] = Field(min_length=1, max_length=500)


class VisualPageReviewRequest(DocumentReviewRequest):
    preview_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    pages: list[int] = Field(min_length=1, max_length=2000)
    confirmed_by: str = Field(min_length=1, max_length=255)
    notes: str = Field(default='', max_length=5000)


class AssemblyApplyRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_revision: int = Field(ge=0)
    plan_id: str = Field(pattern=r'^[0-9a-f]{32}$')
    preview_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')


class CustomerCopyRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_revision: int = Field(ge=0)
    output_id: str = Field(min_length=1, max_length=64)
    output_sha256: str = Field(min_length=64, max_length=64)
    temperature_result_ids: list[str] = Field(default_factory=list, max_length=100)


class CustomerCheckRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_revision: int = Field(ge=0)
    output_id: str = Field(min_length=1, max_length=64)
    output_sha256: str = Field(min_length=64, max_length=64)
    sensitive_terms: list[str] = Field(default_factory=list, max_length=200)
    forbidden_project_ids: list[str] = Field(default_factory=list, max_length=100)
    reviewed_parts: dict[str, str] = Field(default_factory=dict, max_length=1000)
    disclosure_scope_confirmed: bool = False
    reviewed_by: str = Field(default='Lab User', min_length=1, max_length=255)
    content_review_sha256: str | None = Field(default=None, min_length=64, max_length=64)
