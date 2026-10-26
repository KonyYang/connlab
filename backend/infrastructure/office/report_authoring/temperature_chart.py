"""Embed an editable temperature chart in one explicitly selected report region.

The calculation remains in temperature_rise. This adapter packages its existing results,
formula caches and native Excel chart for Word without re-saving unrelated DOCX parts.
"""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
from math import isfinite
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from lxml import etree
from openpyxl import Workbook

from backend.domain.temperature_rise import Coefficients
from backend.infrastructure.office.temperature_workbook_gateway import _chart, _series, _formula_caches

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
C = "http://schemas.openxmlformats.org/drawingml/2006/chart"
P = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"


def _xml(content):
    root = etree.fromstring(content, parser=etree.XMLParser(resolve_entities=False, no_network=True))
    if root.getroottree().docinfo.doctype:
        raise ValueError("Report document type declarations are unsupported.")
    return root


def _bytes(node):
    return etree.tostring(node, encoding="UTF-8", xml_declaration=True, standalone=True)


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError("Temperature chart requires finite numeric analysis values.")
    return value


def _chart_workbook(analysis):
    points = analysis["points"]
    if not 2 <= len(points) <= 20000:
        raise ValueError("Temperature chart requires 2–20000 analyzed points.")
    fits = [Coefficients(**{key: _number(value) for key, value in analysis[name]["fitted_coefficients"].items()})
            for name in ("maximum_fit", "average_fit")]
    book = Workbook()
    sheet = book.active
    sheet.title = "Temperature rise"
    sheet.append(["Applied current (A)", "Measured Max (°C)", "Measured Avg of Max (°C)",
                  "Fitted Max (°C)", "Fitted Avg of Max (°C)", "Point origin"])
    caches = {}
    for row, point in enumerate(points, 2):
        current, maximum, average = (_number(point[key]) for key in ("current", "maximum", "average"))
        if current < 0:
            raise ValueError("Applied current must be nonnegative.")
        sheet.append([current, maximum, average, None, None,
                      "Model origin (not measured)" if point["source_row"] is None else f'Source row {point["source_row"]}'])
        for column, fit in zip(("D", "E"), fits):
            sheet[f"{column}{row}"] = f"=({fit.a!r}*A{row}+({fit.b!r}))*A{row}+({fit.c!r})"
            caches[f"{column}{row}"] = fit.evaluate(current)
    chart = _chart("Temperature Rise vs Applied Current", "Applied Current (A)", "T-rise (°C)")
    chart.layout.manualLayout.h = .58
    chart.legend.layout.manualLayout.x = .05
    chart.legend.layout.manualLayout.y = .84
    chart.legend.layout.manualLayout.w = .9
    chart.legend.layout.manualLayout.h = .15
    measured_start = 3 if points[0]["source_row"] is None else 2
    end = len(points) + 1
    for column, title, color in ((2, "Measured Max", "C00000"), (3, "Measured Avg of Max", "0070C0")):
        series = _series(sheet, 1, column, measured_start, end, title, color)
        series.marker.symbol = "circle"
        series.marker.size = 5
        series.marker.graphicalProperties.solidFill = color
        series.marker.graphicalProperties.line.solidFill = color
        series.graphicalProperties.line.solidFill = None
        series.graphicalProperties.line.noFill = True
        chart.series.append(series)
    # Sample the existing domain fit densely. The source point table stays separate
    # so interpolated values cannot be mistaken for actual scanner readings.
    sheet["H1"], sheet["I1"], sheet["J1"] = "Fit current (A)", "Fitted Max (°C)", "Fitted Avg of Max (°C)"
    low, high = min(p["current"] for p in points), max(p["current"] for p in points)
    for row in range(2, 103):
        current = low + (high - low) * (row - 2) / 100
        sheet[f"H{row}"] = current
        for column, fit in zip(("I", "J"), fits):
            sheet[f"{column}{row}"] = f"=({fit.a!r}*H{row}+({fit.b!r}))*H{row}+({fit.c!r})"
            caches[f"{column}{row}"] = fit.evaluate(current)
    for column, title, color in ((9, "Fitted Max", "C00000"), (10, "Fitted Avg of Max", "0070C0")):
        series = _series(sheet, 8, column, 2, 102, title, color, caches)
        series.marker.symbol = "none"
        chart.series.append(series)
    chart.y_axis.scaling.min = min(0, *caches.values(),
                                  *(point[key] for point in points for key in ("maximum", "average")))
    for row in sheet:
        for cell in row:
            if isinstance(cell.value, (float, int)) or cell.data_type == "f":
                cell.number_format = "0.000"
    for column in "ABCDEFGHIJ":
        sheet.column_dimensions[column].width = 24
    sheet.add_chart(chart, "L2")
    memory = BytesIO()
    book.save(memory)
    book.close()
    return _formula_caches(memory.getvalue(), {sheet.title: caches})


def insert_temperature_chart(source_path: Path, output_path: Path, analysis: dict, anchor_tag: str) -> None:
    """Write a new DOCX. Caller owns project/source validation and draft publication."""
    source, output = Path(source_path), Path(output_path)
    if output.exists():
        raise ValueError("Do not overwrite an existing report.")
    raw = source.read_bytes()
    if len(raw) > 60 * 1024 * 1024:
        raise ValueError("Report exceeds the chart update limit.")
    with ZipFile(BytesIO(raw)) as archive:
        entries = archive.infolist()
        if len(entries) > 4000 or sum(entry.file_size for entry in entries) > 200 * 1024 * 1024:
            raise ValueError("Expanded report exceeds the chart update limit.")
        if len({entry.filename for entry in entries}) != len(entries):
            raise ValueError("Duplicate report package parts.")
        parts = {entry.filename: archive.read(entry) for entry in entries}
    document = _xml(parts["word/document.xml"])
    regions = document.xpath(".//w:sdt[w:sdtPr/w:tag/@w:val=$tag]/w:sdtContent", namespaces={"w": W}, tag=anchor_tag)
    if len(regions) != 1:
        raise ValueError("Select exactly one result region for the temperature chart.")
    if regions[0].find(f".//{{{C}}}chart") is not None:
        raise ValueError("The result region already contains a chart; replace its result first.")
    workbook = _chart_workbook(analysis)
    token = sha256((anchor_tag + sha256(workbook).hexdigest()).encode()).hexdigest()[:20]
    chart_name = f"word/charts/connlab-temperature-{token}.xml"
    workbook_name = f"word/embeddings/connlab-temperature-{token}.xlsx"
    if chart_name in parts or workbook_name in parts:
        raise ValueError("Chart package identity already exists.")
    with ZipFile(BytesIO(workbook)) as archive:
        chart = _xml(archive.read("xl/charts/chart1.xml"))
    external = etree.SubElement(chart, f"{{{C}}}externalData", {f"{{{R}}}id": "rIdWorkbook"})
    etree.SubElement(external, f"{{{C}}}autoUpdate", val="0")
    chart_rels = etree.Element(f"{{{P}}}Relationships", nsmap={None: P})
    etree.SubElement(chart_rels, f"{{{P}}}Relationship", Id="rIdWorkbook", Type=R + "/package",
                     Target="../embeddings/" + workbook_name.rsplit("/", 1)[1])
    rels_name = "word/_rels/document.xml.rels"
    rels = _xml(parts[rels_name]) if rels_name in parts else etree.Element(f"{{{P}}}Relationships", nsmap={None: P})
    ids = {node.get("Id") for node in rels}
    index = 1
    while f"rIdTemperature{index}" in ids:
        index += 1
    rid = f"rIdTemperature{index}"
    etree.SubElement(rels, f"{{{P}}}Relationship", Id=rid, Type=R + "/chart", Target="charts/" + chart_name.rsplit("/", 1)[1])
    paragraph = etree.SubElement(regions[0], f"{{{W}}}p")
    run = etree.SubElement(paragraph, f"{{{W}}}r")
    drawing = etree.SubElement(run, f"{{{W}}}drawing")
    inline = etree.SubElement(drawing, f"{{{WP}}}inline", distT="0", distB="0", distL="0", distR="0")
    etree.SubElement(inline, f"{{{WP}}}extent", cx="5486400", cy="3200400")
    doc_ids = [int(node.get("id", "0")) for node in document.iter(f"{{{WP}}}docPr") if node.get("id", "0").isdigit()]
    etree.SubElement(inline, f"{{{WP}}}docPr", id=str(max(doc_ids, default=0) + 1), name="Temperature rise chart")
    graphic = etree.SubElement(inline, f"{{{A}}}graphic")
    data = etree.SubElement(graphic, f"{{{A}}}graphicData", uri=C)
    etree.SubElement(data, f"{{{C}}}chart", {f"{{{R}}}id": rid})
    types = _xml(parts["[Content_Types].xml"])
    for name, content_type in ((chart_name, "application/vnd.openxmlformats-officedocument.drawingml.chart+xml"),
                               (workbook_name, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")):
        etree.SubElement(types, f"{{{CT}}}Override", PartName="/" + name, ContentType=content_type)
    updates = {"word/document.xml": _bytes(document), rels_name: _bytes(rels), "[Content_Types].xml": _bytes(types),
               chart_name: _bytes(chart), workbook_name: workbook,
               "word/charts/_rels/" + chart_name.rsplit("/", 1)[1] + ".rels": _bytes(chart_rels)}
    if source.read_bytes() != raw:
        raise ValueError("Source report changed during chart preparation.")
    memory = BytesIO()
    with ZipFile(memory, "w", ZIP_DEFLATED) as archive:
        for name, content in {**parts, **updates}.items():
            archive.writestr(name, content)
    with output.open("xb") as stream:
        stream.write(memory.getvalue())
