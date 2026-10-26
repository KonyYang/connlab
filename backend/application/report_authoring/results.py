"""Confirmed source-column projections retain raw values and their measurement meaning."""
from dataclasses import asdict
from decimal import Decimal, InvalidOperation
from backend.domain.temperature_data import DataSelection, column_letter


class ReportResultReader:
    def __init__(self, workbook, temperature):
        self.workbook = workbook
        self.temperature = temperature

    def table(self, content, file_name, sheet_name=None):
        return self.workbook.read_upload(content, file_name, sheet_name=sheet_name or None)

    def preview(self, content, file_name, request):
        table = self.table(content, file_name, request["sheet_name"])
        kind = request["kind"]
        if kind == "temperature":
            raw = request.get("temperature_selection")
            if raw is None:
                raise ValueError("Confirm the ambient/current/temperature columns and sample groups first.")
            selection = DataSelection(**{**raw, "temperature_columns": tuple(raw["temperature_columns"]),
                "excluded_rows": tuple(raw.get("excluded_rows", [])),
                "sample_groups": tuple(tuple(group) for group in raw["sample_groups"]) if raw.get("sample_groups") else None,
                "channel_names": tuple((int(key), value) for key, value in raw.get("channel_names", {}).items())})
            analysis = self.temperature.analyze(table, selection, zero_intercept=request["zero_intercept"],
                acknowledge_warnings=request["acknowledge_warnings"])
            identities = [value.strip() for value in request.get('sample_ids', [])]
            if identities and (len(identities) != selection.sample_count or len(set(identities)) != len(identities) or not all(identities)):
                raise ValueError('Temperature sample identities must be unique and match the confirmed channel groups.')
            return {"sheet_name": table.sheet_name, "analysis": asdict(analysis),
                "raw_rows": [{"source_row": index, "values": list(table.rows[index - 1])}
                    for index in range(selection.start_row, selection.end_row + 1) if index not in selection.excluded_rows],
                "selection": raw, "sample_ids": identities, "unit": "°C", "quantity": "measured_temperature_rise"}
        start, end = request["start_row"], request["end_row"]
        if not 1 <= start <= end <= len(table.rows):
            raise ValueError("Select an existing, ordered source row range.")
        columns = request["columns"]
        def cell(row_number, name, required=True):
            column = columns.get(name)
            if column is None:
                if not required:
                    return ""
                raise ValueError(f"Select the {name} column.")
            if not 1 <= column <= len(table.rows[row_number - 1]):
                raise ValueError(f"Row {row_number}: the {name} column is outside the sheet.")
            value = table.rows[row_number - 1][column - 1]
            if required and (value is None or str(value).strip() == ""):
                raise ValueError(f"Row {row_number}: {name} is empty. Correct the source or narrow the range.")
            return value if value is not None else ""
        rows = []
        seen = set()
        for number in range(start, end + 1):
            sample = str(cell(number, "sample")).strip()
            record_id = str(cell(number, "record_id", False)).strip()
            if (sample, record_id) in seen:
                raise ValueError("Duplicate sample/record identity. Select the correct record-ID column or row range.")
            seen.add((sample, record_id))
            item = {"sample_id": sample, "record_id": record_id,
                "color": str(cell(number, "color", False)).strip(), "source_row": number,
                "source_cells": {key: f"{column_letter(column)}{number}" for key, column in columns.items()}}
            if kind == "cr":
                voltage, current = decimal(cell(number, "voltage")), decimal(cell(number, "current"))
                if current <= 0:
                    raise ValueError(f"Row {number}: measured current must be positive; a rated-current default is not used.")
                if request["unit"] not in {"mV", "V"}:
                    raise ValueError("Confirm voltage as mV or V; current must be amperes.")
                resistance = voltage / current * (1000 if request["unit"] == "V" else 1)
                if voltage < 0:
                    raise ValueError(f"Row {number}: negative voltage needs source review, not an automatic absolute value.")
                item.update(voltage=str(voltage), voltage_unit=request["unit"], current_a=str(current),
                    resistance_mohm=str(resistance))
                if request["quantity"] == "delta":
                    initial = decimal(cell(number, "initial_mohm"))
                    item.update(initial_mohm=str(initial), delta_mohm=str(resistance - initial))
                numeric = Decimal(item.get("delta_mohm", item["resistance_mohm"]))
            else:
                if request["unit"] != "N":
                    raise ValueError("Confirm mechanical summary values in newtons (N).")
                value = decimal(cell(number, "value"))
                if value < 0:
                    raise ValueError("Negative force needs an explicit source correction, not an inferred magnitude.")
                item.update(value=str(value), unit="N")
                if request["measurement_kind"] == "hold":
                    duration = decimal(cell(number, "hold_seconds"))
                    if duration <= 0:
                        raise ValueError("Confirm a positive hold duration in seconds.")
                    item["hold_seconds"] = str(duration)
                numeric = value
            item["summary_value"] = str(numeric)
            rows.append(item)
        values = [Decimal(item["summary_value"]) for item in rows]
        mean = sum(values) / len(values)
        stdev = (sum((value - mean) ** 2 for value in values) / (len(values) - 1)).sqrt() if len(values) > 1 else None
        return {"sheet_name": table.sheet_name, "rows": rows, "unit": "mΩ" if kind == "cr" else "N",
            "quantity": request["quantity"] if kind == "cr" else request["measurement_kind"],
            "test_type": request["test_type"] if kind == "mechanical" else "contact_resistance",
            "summary": {"min": str(min(values)), "max": str(max(values)), "average": str(mean),
                        "stdev": str(stdev) if stdev is not None else None}}


def decimal(value):
    if isinstance(value, bool):
        raise ValueError("Boolean cells are not measurements.")
    try:
        number = Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise ValueError(f"A selected measurement is not numeric: {value!s}") from exc
    if not number.is_finite():
        raise ValueError("Measurements must be finite numbers.")
    return number
