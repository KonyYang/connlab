"""Live Matrix per-step output text, keyed before sample-row filtering."""

from pydantic import BaseModel, Field


class MatrixStepTextOutputOverrideRequest(BaseModel):
    group_key: str = Field(min_length=1)
    row_order: int = Field(gt=0)
    step_sequence: int = Field(gt=0)
    step_suffix_note: str = ""
    description: str | None = None
    requirement: str | None = None
