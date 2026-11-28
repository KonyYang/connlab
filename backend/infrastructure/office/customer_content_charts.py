"""Replace linked or embedded T-rise charts with the reviewed measured maxima only."""
import posixpath
import re
from io import BytesIO
from urllib.parse import unquote
from zipfile import ZipFile

from lxml import etree
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.data_source import AxDataSource, NumData, NumVal, StrData, StrRef, StrVal

from backend.infrastructure.office.report_authoring.temperature_chart import C, CT, P, R, _bytes, _xml
from backend.infrastructure.office.temperature_workbook_gateway import _chart, _series


def _relationships(part):
    directory, name = posixpath.split(part)
    return posixpath.join(directory, "_rels", name + ".rels")


def _target(part, rel):
    if rel.get("TargetMode") == "External":
        return None
    return posixpath.normpath(posixpath.join(posixpath.dirname(part), unquote(rel.get("Target")))).lstrip("/")


def _reachable(package, updates):
    # Drop old chart data only once its last internal relationship is gone.
    names = set(package.namelist()) | updates.keys()
    visited, pending = set(), [""]
    while pending:
        part = pending.pop()
        if part in visited:
            continue
        visited.add(part)
        rels = _relationships(part)
        if rels not in names:
            continue
        visited.add(rels)
        root = _xml(updates[rels] if rels in updates else package.read(rels))
        pending.extend(target for rel in root if (target := _target(part, rel)) in names)
    return visited


def _measured_chart(summary):
    headers, rows = summary["headers"], summary["rows"]
    maximum = next((i for i, label in enumerate(headers) if re.search(r"\bmax(?:imum)?\b|最大", label, re.I)), None)
    column_choices = [opt["label"] for opt in summary.get("options", ()) if opt["value"].startswith("c")]
    if column_choices:
        maximum = next((i for i, h in enumerate(headers) if h in column_choices), maximum)
    if maximum is None:
        points = zip(headers[1:], rows[0][1:], strict=True)
    else:
        current = next((i for i, label in enumerate(headers) if re.search(r"current|电流", label, re.I)), 0)
        points = ((r[current], r[maximum]) for r in rows)
    book = Workbook()
    sheet = book.active
    sheet.title = "Measured maxima"
    sheet.append(["Applied current", "Measured maximum rise", "Test condition"])
    numeric_axis = True
    for condition, value in points:
        current_value = re.match(r"^\s*([-+]?\d+(?:[.,]\d+)?)", condition)
        reading = re.fullmatch(r"\s*([-+]?\d+(?:[.,]\d+)?)\s*(?:°[CF]|℃|℉|K)?\s*", value, re.I)
        if reading:
            numeric_axis = numeric_axis and current_value is not None
            sheet.append([float(current_value[1].replace(",", ".")) if current_value else None,
                          float(reading[1].replace(",", ".")), condition])
            sheet.cell(sheet.max_row, 3).data_type = "s"
    if sheet.max_row < 2:
        raise ValueError("The measured maximum chart needs numeric currents and readings. Check its source table.")
    units = " ".join([*headers, summary["label"], *rows[0][:1]])
    axis_unit = re.search(r"°\s*([CF])", units, re.I)
    current_unit = re.search(r"\b(kA|mA|A)\b", units)
    title = "Measured maximum temperature rise"
    y_title = "Maximum rise" + (f" (°{axis_unit[1].upper()})" if axis_unit else "")
    if numeric_axis:
        chart = _chart(title, "Applied current" + (f" ({current_unit[1]})" if current_unit else ""), y_title)
        series = _series(sheet, 1, 2, 2, sheet.max_row, "Measured maximum", "205CA7")
        series.marker.symbol = "circle"
        chart.series.append(series)
    else:
        chart = BarChart()
        chart.title, chart.y_axis.title = title, y_title
        chart.add_data(Reference(sheet, min_col=2, min_row=2, max_row=sheet.max_row))
        series = chart.series[0]
        values = list(sheet.iter_rows(min_row=2, values_only=True))
        series.cat = AxDataSource(strRef=StrRef(f=str(Reference(sheet, min_col=3, min_row=2, max_row=sheet.max_row)),
            strCache=StrData(ptCount=len(values), pt=[StrVal(idx=i, v=v[2]) for i,v in enumerate(values)])))
        series.val.numRef.numCache = NumData(ptCount=len(values), pt=[NumVal(idx=i, v=v[1]) for i,v in enumerate(values)])
        chart.legend = None
    chart.y_axis.scaling.min = min(0, *(r[1] for r in sheet.iter_rows(min_row=2, values_only=True)))
    sheet.add_chart(chart, "E2")
    buffer = BytesIO()
    book.save(buffer)
    book.close()
    with ZipFile(buffer) as workbook:
        chart_xml = _xml(workbook.read("xl/charts/chart1.xml"))
    external = etree.SubElement(chart_xml, f"{{{C}}}externalData", {f"{{{R}}}id": "rIdWorkbook"})
    etree.SubElement(external, f"{{{C}}}autoUpdate", val="0")
    return _bytes(chart_xml), buffer.getvalue()


def customer_chart_parts(package, charts):
    if not charts:
        return {}, set()
    main = "word/document.xml"
    document_rels = {r.get("Id"): r for r in _xml(package.read(_relationships(main)))}
    updates, private_workbooks = {}, set()
    types = _xml(package.read("[Content_Types].xml"))
    for rid, summary in charts.items():
        rel = document_rels.get(rid)
        part = _target(main, rel) if rel is not None else None
        if not part or part not in package.namelist() or rel.get("Type") != R + "/chart":
            raise ValueError("The temperature chart link is unavailable. Check its chart in the internal report.")
        chart_rels = _relationships(part)
        if chart_rels in package.namelist():
            for old in _xml(package.read(chart_rels)):
                if old.get("Type") in {R + "/package", R + "/oleObject"} and (target := _target(part, old)):
                    private_workbooks.add(target)
        workbook = f"word/embeddings/customer-max-{len(updates)}.xlsx"
        while workbook in package.namelist() or workbook in updates:
            workbook = workbook.removesuffix(".xlsx") + "-1.xlsx"
        updates[part], updates[workbook] = _measured_chart(summary)
        relationships = etree.Element(f"{{{P}}}Relationships", nsmap={None: P})
        etree.SubElement(relationships, f"{{{P}}}Relationship", Id="rIdWorkbook", Type=R + "/package",
                         Target=posixpath.relpath(workbook, posixpath.dirname(part)))
        updates[chart_rels] = _bytes(relationships)
        etree.SubElement(types, f"{{{CT}}}Override", PartName="/" + workbook,
                         ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    reachable = _reachable(package, updates)
    if reachable & private_workbooks:
        raise ValueError("A temperature chart shares its internal workbook with another object. Separate it in the internal report.")
    removed = _reachable(package, {}) - reachable
    for override in list(types):
        if override.get("PartName", "").lstrip("/") in removed:
            types.remove(override)
    updates["[Content_Types].xml"] = _bytes(types)
    return updates, removed
