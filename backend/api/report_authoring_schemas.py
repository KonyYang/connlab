"""Bounded report evidence edits; source paths and authority IDs are server owned."""
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict
from backend.api.temperature_schemas import DataSelectionRequest


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


class SelectBaseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=0)
    source_id: str = Field(min_length=1, max_length=64)


class ResultImportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=0)
    source_id: str = Field(min_length=1, max_length=64)
    kind: Literal["temperature", "cr", "mechanical"]
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
