"""Coordinate independent measurement imports, explicit mapping, and new workbook exports."""
from dataclasses import asdict
from pathlib import Path
from typing import Protocol

from backend.modules.temperature_rise.calculation import fit_curve, inverse_current, number, stage_endpoints, summarize


class TemperatureRiseWorkbookPort(Protocol):
    def read(self, source: Path) -> list[dict]: ...
    def write(self, source: Path, output: Path, block: dict, result: dict) -> Path: ...


class ToolsTemperatureRiseService:
    def __init__(self, gateway: TemperatureRiseWorkbookPort):
        self.gateway = gateway

    def preview(self, source: Path) -> dict:
        blocks = self.gateway.read(source)
        previews = []
        for block in blocks:
            mapping = block["suggested_mapping"]
            indices = stage_endpoints([number(row["values"][mapping["current"]], "Current") for row in block["rows"]])
            previews.append({key: block[key] for key in ("id", "sheet", "header_row", "headers", "suggested_mapping", "current_metadata")} |
                            {"row_count": len(block["rows"]), "records": block["rows"],
                             "candidate_rows": [block["rows"][index]["row"] for index in indices]})
        return {"blocks": previews}

    def analyze(self, source: Path, options: dict) -> dict:
        block, result = self._calculate(source, options)
        return result

    def suggest(self, source: Path, options: dict) -> dict:
        if not isinstance(options, dict):
            raise ValueError("Select a measurement block and Current column.")
        block = next((block for block in self.gateway.read(source) if block["id"] == str(options.get("block_id"))), None)
        column = options.get("current_column")
        if block is None or type(column) is not int or not 0 <= column < len(block["headers"]):
            raise ValueError("Select a valid Current column in the measurement block.")
        currents = [number(row["values"][column], f'Row {row["row"]} Current') for row in block["rows"]]
        return {"candidate_rows": [block["rows"][index]["row"] for index in stage_endpoints(currents)]}

    def export(self, source: Path, output: Path, options: dict) -> Path:
        block, result = self._calculate(source, options)
        return self.gateway.write(source, output, block, result)

    def _calculate(self, source: Path, options: dict) -> tuple[dict, dict]:
        if not isinstance(options, dict):
            raise ValueError("Confirm measurement settings first.")
        block = next((block for block in self.gateway.read(source) if block["id"] == str(options.get("block_id"))), None)
        if block is None:
            raise ValueError("Select a measurement data block from the preview.")
        mapping = options.get("mapping")
        if not isinstance(mapping, dict) or not isinstance(mapping.get("channels"), list) or not mapping["channels"]:
            raise ValueError("Map Ambient, Current and at least one sample channel.")
        channels = mapping["channels"]
        columns = [mapping.get("ambient"), mapping.get("current")] + [channel.get("column") for channel in channels if isinstance(channel, dict)]
        if len(columns) != len(channels) + 2 or any(type(column) is not int or not 0 <= column < len(block["headers"]) for column in columns) or len(set(columns)) != len(columns):
            raise ValueError("Ambient, Current and included temperature channels must use distinct valid columns.")
        labels = [(str(channel.get("sample", "")).strip(), str(channel.get("point", "")).strip()) for channel in channels]
        if any(not sample or not point for sample, point in labels) or len(set(labels)) != len(labels):
            raise ValueError("Use non-empty sample and point names; each sample/point pair must be unique.")
        selected = options.get("selected_rows")
        known = {row["row"] for row in block["rows"]}
        if not isinstance(selected, list) or not selected or any(type(row) is not int or row not in known for row in selected) or len(set(selected)) != len(selected):
            raise ValueError("Confirm distinct source rows from the preview before calculating.")
        mode = options.get("current_mode", "amperes")
        if mode not in {"amperes", "voltage"}:
            raise ValueError("Select already converted amperes or raw voltage conversion.")
        gain = number(options.get("current_gain", 1), "Current gain") if mode == "voltage" else 1.0
        if gain <= 0:
            raise ValueError("Voltage-to-current gain must be positive.")
        settings = {"mapping": {**mapping, "channels": [{**channel, "sample": sample, "point": point} for channel, (sample, point) in zip(channels, labels)]},
                    "current_mode": mode, "applied_gain": gain,
                    "zero_intercept": options.get("zero_intercept", True), "include_origin": options.get("include_origin", True),
                    "target_rise": number(options.get("target_rise", 30), "Target rise"),
                    "max_temperature": number(options.get("max_temperature", 125), "Maximum temperature"),
                    "derating_factor": number(options.get("derating_factor", .8), "Derating factor")}
        if type(settings["zero_intercept"]) is not bool or type(settings["include_origin"]) is not bool:
            raise ValueError("Intercept and display-origin choices must be boolean.")
        if not 0 < settings["derating_factor"] <= 1:
            raise ValueError("Derating factor must be greater than zero and at most one.")
        currents = [number(row["values"][mapping["current"]], f'Row {row["row"]} Current') * gain for row in block["rows"]]
        points = []
        for row, current in zip(block["rows"], currents):
            if row["row"] not in selected:
                continue
            values = row["values"]
            summary = summarize(number(values[mapping["ambient"]], f'Row {row["row"]} Ambient'),
                                [(sample, point, number(values[channel["column"]], f'Row {row["row"]} {sample}_{point}')) for channel, (sample, point) in zip(channels, labels)])
            points.append({"row": row["row"], "current": current, "raw": values, **summary})
        x = [point["current"] for point in points]
        maximum = fit_curve(x, [point["maximum"] for point in points], zero_intercept=settings["zero_intercept"], include_origin=settings["include_origin"])
        average = fit_curve(x, [point["average_of_max"] for point in points], zero_intercept=settings["zero_intercept"], include_origin=settings["include_origin"])
        ambient_values = options.get("ambient_temperatures", list(range(20, 126, 5)))
        if not isinstance(ambient_values, list) or not 2 <= len(ambient_values) <= 200:
            raise ValueError("Enter 2 to 200 ambient temperatures for the derating curve.")
        ambient_values = sorted(set(number(value, "Ambient temperature") for value in ambient_values))
        if len(ambient_values) < 2:
            raise ValueError("Enter at least two distinct ambient temperatures for derating.")
        derating = []
        for ambient in ambient_values:
            rise = settings["max_temperature"] - ambient
            try:
                basic = inverse_current(average, rise)
            except ValueError as exc:
                raise ValueError(f"Derating at {ambient:g} C: {exc}") from exc
            derating.append({"ambient": ambient, "allowable_rise": rise, "basic_current": basic, "derated_current": basic * settings["derating_factor"]})
        target = inverse_current(maximum, settings["target_rise"])
        return block, {"points": points, "candidate_rows": [block["rows"][index]["row"] for index in stage_endpoints(currents)],
                       "max_curve": asdict(maximum), "avg_curve": asdict(average), "target_current": target,
                       "derating": derating, "settings": settings,
                       "extrapolated": target > max(x) or any(row["basic_current"] > max(x) for row in derating)}
