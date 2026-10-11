"""Session-local report facts, separate from temperature calculation inputs."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TemperatureReportMetadata:
    ltr_number: str = ''
    tested_by: str = ''
    test_date: str = ''
    ambient_temperature: str = ''
    relative_humidity: float | None = None
    equipment_id: str = ''
    test_condition: str = ''
    remark: str = ''
