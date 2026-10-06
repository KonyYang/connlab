"""Stateless temperature Tools use cases with a workbook IO boundary."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
import re

from backend.application.temperature_data_preparation import (
    DataRegionError, PreparedData, prepare_data, selection_for_region, suggest_selection,
)
from backend.application.temperature_channel_layout import ChannelLayout, inspect_channel_layout
from backend.domain.temperature_data import DataSelection, WorkbookTable
from backend.domain.temperature_rise import (
    Coefficients, DeratingAnalysis, TemperatureRiseAnalysis, analyze_temperature_rise,
    generate_derating,
)


class TemperatureWorkbookPort(Protocol):
    def read_upload(self, content: bytes, file_name: str, *, sheet_name: str | None = None) -> WorkbookTable: ...
    def render(self, file_name: str, *, table: WorkbookTable, selection: DataSelection,
              prepared: PreparedData, analysis: TemperatureRiseAnalysis,
              maximum_coefficients: Coefficients, average_coefficients: Coefficients,
              target_rise: float | None, derating: DeratingAnalysis | None) -> bytes: ...


@dataclass(frozen=True)
class DeratingParameters:
    max_temperature: float = 105
    step: float = 2.5
    ambient_point: float = 75


@dataclass(frozen=True)
class WorkbookImportResult:
    table: WorkbookTable
    selection: DataSelection | None
    region_issue: str | None = None
    channel_layout: ChannelLayout | None = None


class ToolsTemperatureService:
    def __init__(self, workbook: TemperatureWorkbookPort):
        self.workbook = workbook

    def import_workbook(self, content: bytes, name: str, sheet_name: str | None = None,
                        *, region: tuple[int, int, int] | None = None) -> WorkbookImportResult:
        file_name = safe_workbook_name(name)
        table = self.workbook.read_upload(content, file_name, sheet_name=sheet_name)
        if region is not None:
            return self._import_result(table, selection_for_region(table, *region))
        try:
            return self._import_result(table, suggest_selection(table))
        except DataRegionError as exc:
            # A readable source stays available for manual recovery, not an accepted guess.
            return WorkbookImportResult(table, None, str(exc))

    @staticmethod
    def _import_result(table: WorkbookTable, selection: DataSelection) -> WorkbookImportResult:
        layout = inspect_channel_layout(table, selection.header_row, selection.start_row, selection.end_row)
        return WorkbookImportResult(table, selection, channel_layout=layout)

    def analyze(self, table: WorkbookTable, selection: DataSelection, *, zero_intercept: bool,
                acknowledge_warnings: bool = False) -> TemperatureRiseAnalysis:
        prepared = self._confirmed_data(table, selection, acknowledge_warnings)
        return analyze_temperature_rise(prepared.measurements,
            thermocouples_per_sample=selection.thermocouples_per_sample, zero_intercept=zero_intercept)

    def download(self, table: WorkbookTable, selection: DataSelection, *, zero_intercept: bool,
                 acknowledge_warnings: bool, maximum_coefficients: Coefficients | None,
                 average_coefficients: Coefficients | None, target_rise: float | None,
                 derating_parameters: DeratingParameters | None) -> tuple[str, bytes]:
        prepared = self._confirmed_data(table, selection, acknowledge_warnings)
        analysis = analyze_temperature_rise(prepared.measurements,
            thermocouples_per_sample=selection.thermocouples_per_sample, zero_intercept=zero_intercept)
        maximum = maximum_coefficients or analysis.maximum_fit.coefficients
        average = average_coefficients or analysis.average_fit.coefficients
        if zero_intercept and (maximum.c != 0 or average.c != 0):
            raise ValueError('Zero Intercept requires both c coefficients to be zero.')
        derating = None
        if derating_parameters:
            if not zero_intercept:
                raise ValueError('Generate Derating with Zero Intercept enabled.')
            derating = generate_derating(average, max_temperature=derating_parameters.max_temperature,
                step=derating_parameters.step, ambient_point=derating_parameters.ambient_point)
        name = f'{Path(safe_workbook_name(table.file_name)).stem}_T-rise_Derating.xlsx'
        content = self.workbook.render(name, table=table, selection=selection, prepared=prepared, analysis=analysis,
            maximum_coefficients=maximum, average_coefficients=average, target_rise=target_rise, derating=derating)
        return name, content

    @staticmethod
    def _confirmed_data(table, selection, acknowledge_warnings):
        prepared = prepare_data(table, selection, acknowledge_warnings=acknowledge_warnings)
        if not prepared.ready:
            raise ValueError('Review the flagged rows, correct or exclude invalid readings, and confirm the data first.')
        return prepared


def safe_workbook_name(name: str) -> str:
    name = re.split(r'[/\\]', name)[-1]
    name = re.sub(r'[<>:"|?*\x00-\x1f]', '_', name).strip(' .')
    stem, suffix = Path(name).stem, Path(name).suffix.lower()
    if suffix not in ('.xls', '.xlsx', '.xlsm', '.csv'):
        raise ValueError('Select an Excel .xls, .xlsx, .xlsm or CSV .csv file.')
    if not stem or stem.upper() in {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}:
        stem = 'Scanner Data'
    return stem[:140] + suffix
