"""Bounded, explicit input contracts for standalone temperature analysis."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator
from backend.domain.temperature_data import DataSelection, WorkbookTable
from backend.domain.temperature_rise import Coefficients


class TemperatureModel(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)


class WorkbookTableRequest(TemperatureModel):
    file_name: str = Field(max_length=255)
    sheet_names: list[str] = Field(min_length=1, max_length=256)
    sheet_name: str = Field(max_length=255)
    rows: list[list[str | float | int | bool | None]] = Field(min_length=1, max_length=20000)

    @model_validator(mode='after')
    def bounded_cells(self):
        if any(len(row) > 256 for row in self.rows) or sum(map(len, self.rows)) > 1000000:
            raise ValueError('The sheet exceeds the supported preview size.')
        if any(isinstance(cell, str) and len(cell) > 32767 for row in self.rows for cell in row):
            raise ValueError('A cell is longer than the Excel text limit.')
        return self

    def domain(self):
        return WorkbookTable(self.file_name, tuple(self.sheet_names), self.sheet_name, tuple(tuple(row) for row in self.rows))


class DataSelectionRequest(TemperatureModel):
    header_row: int = Field(ge=1, le=20000)
    start_row: int = Field(ge=2, le=20000)
    end_row: int = Field(ge=2, le=20000)
    ambient_column: int = Field(ge=1, le=256)
    current_column: int = Field(ge=1, le=256)
    temperature_columns: list[int] = Field(min_length=1, max_length=254)
    thermocouples_per_sample: int = Field(ge=1, le=254)
    excluded_rows: list[int] = Field(default_factory=list, max_length=20000)
    current_multiplier: float = Field(default=1, gt=0, le=1000000000)
    sample_groups: list[Annotated[list[int], Field(max_length=254)]] | None = Field(default=None, max_length=254)
    channel_names: dict[Annotated[int, Field(ge=3, le=256)],
                        Annotated[str, StringConstraints(max_length=200, pattern=r'^[^\x00-\x1f]*$')]] = Field(default_factory=dict, max_length=254)

    def domain(self):
        return DataSelection(**(self.model_dump() | {
            'temperature_columns': tuple(self.temperature_columns), 'excluded_rows': tuple(self.excluded_rows),
            'sample_groups': tuple(tuple(group) for group in self.sample_groups) if self.sample_groups is not None else None,
            'channel_names': tuple(self.channel_names.items())}))


class PreparationRequest(TemperatureModel):
    table: WorkbookTableRequest
    selection: DataSelectionRequest
    acknowledge_warnings: bool = False
    zero_intercept: bool = True


class CoefficientsRequest(TemperatureModel):
    a: float
    b: float
    c: float

    def domain(self):
        return Coefficients(self.a, self.b, self.c)


class CurrentRequest(TemperatureModel):
    coefficients: CoefficientsRequest
    target_rise: float = Field(ge=0)


class DeratingSettings(TemperatureModel):
    max_temperature: float = 105
    step: float = 2.5
    ambient_point: float = 75


class DeratingRequest(DeratingSettings):
    coefficients: CoefficientsRequest


class TemperatureReportMetadataRequest(TemperatureModel):
    ltr_number: Annotated[str, StringConstraints(max_length=200, pattern=r'^[^\x00-\x1f]*$')] = ''
    tested_by: Annotated[str, StringConstraints(max_length=200, pattern=r'^[^\x00-\x1f]*$')] = ''
    test_date: Annotated[str, StringConstraints(max_length=80, pattern=r'^[^\x00-\x1f]*$')] = ''
    ambient_temperature: Annotated[str, StringConstraints(max_length=80, pattern=r'^[^\x00-\x1f]*$')] = ''
    relative_humidity: float | None = Field(default=None, ge=0, le=100)
    equipment_id: Annotated[str, StringConstraints(max_length=500, pattern=r'^[^\x00-\x1f]*$')] = ''
    test_condition: Annotated[str, StringConstraints(max_length=500, pattern=r'^[^\x00-\x1f]*$')] = ''
    remark: Annotated[str, StringConstraints(max_length=500, pattern=r'^[^\x00-\x1f]*$')] = ''

    def application(self):
        from backend.application.temperature_report_metadata import TemperatureReportMetadata
        return TemperatureReportMetadata(**self.model_dump())


class DownloadTemperatureRequest(PreparationRequest):
    maximum_coefficients: CoefficientsRequest | None = None
    average_coefficients: CoefficientsRequest | None = None
    target_rise: float | None = Field(default=None, ge=0)
    derating: DeratingSettings | None = None
    report_metadata: TemperatureReportMetadataRequest = Field(default_factory=TemperatureReportMetadataRequest)
