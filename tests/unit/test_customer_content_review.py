from hashlib import sha256
from io import BytesIO
from zipfile import ZipFile

import pytest
from docx import Document
from docx.opc.part import Part
from docx.opc.packuri import PackURI
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree
from openpyxl import load_workbook

from backend.infrastructure.office.customer_content_review import inspect_document, prepare_document


def add_table(doc, values):
    table = doc.add_table(rows=0, cols=len(values[0]))
    for row in values:
        for cell, value in zip(table.add_row().cells, row, strict=True):
            cell.text = value
    return table


def test_one_review_controls_only_the_ambiguous_sample_and_public_material_labels(tmp_path):
    source, output = tmp_path / "internal.docx", tmp_path / "prepared.docx"
    doc = Document()
    doc.add_paragraph("3. SAMPLE DESCRIPTION")
    values = [
        ["Description", "Part #", "Contact Base Material", "Housing Material"],
        ["Board connector", "P1", "C11000", "PA66"],
        ["Soft busbar", "P2", "C18150", "PA46HFX61S"],
        ["Fixture PCB", "P3", "Unclassified 123", "N/A"],
    ]
    add_table(doc, values)
    doc.add_paragraph("4. TEST DESCRIPTION")
    add_table(doc, values)
    doc.save(source)
    original = source.read_bytes()
    view = inspect_document(source)
    handle = BytesIO(original)
    handle.seek(11)
    assert inspect_document(handle) == view
    assert view["source_sha256"] == sha256(original).hexdigest()
    samples = {item["label"]: item["id"] for item in view["fields"] if item["kind"] == "sample"}
    assert set(samples) == {"Soft busbar", "Fixture PCB"}
    material = next(item for item in view["fields"] if item["kind"] == "material")
    assert material["depends_on"] == samples["Fixture PCB"]
    with pytest.raises(ValueError, match="choice|confirm|Choose"):
        prepare_document(source, output, {})
    assert not output.exists()
    prepare_document(handle, output, {samples["Soft busbar"]: "keep", samples["Fixture PCB"]: "omit"},
                     expected_source_sha256=view["source_sha256"])
    prepared = Document(output)
    assert [[cell.text for cell in row.cells] for row in prepared.tables[0].rows[1:]] == [
        ["Board connector", "P1", "Copper Alloy", "High Temperature Resin"],
        ["Soft busbar", "P2", "Copper Alloy", "High Temperature Resin"],
    ]
    assert [[cell.text for cell in row.cells] for row in prepared.tables[1].rows] == values
    assert source.read_bytes() == original


def test_temperature_retains_measured_maxima_for_each_condition_and_resolves_unknown_row(tmp_path):
    source, output = tmp_path / "internal.docx", tmp_path / "prepared.docx"
    doc = Document()
    doc.add_paragraph("6. TEST RESULTS")
    head = ["Applied current / A", "350", "450 (4 h)"]
    maximum = ["Max T-Rise", "19.9", "38.1"]
    doc.add_paragraph("Table 1: Temperature rise in still air (°C)")
    add_table(doc, [head, ["1# - T1", "14.0", "31.9"], ["3# Single Max", "19.9", "38.1"],
                    maximum, ["Avg of Max T-Rise", "15.2", "35.6"]])
    doc.add_paragraph("Table 2: Temperature rise in airflow (°C)")
    add_table(doc, [head, ["Probe A", "4.4", "9.5"], ["Probe B", "5.0", "11.0"],
                    ["Maximum allowed", "40", "45"]])
    doc.save(source)
    view = inspect_document(source)
    assert view["temperatures"][0]["rows"] == [maximum]
    [choice] = view["fields"]
    assert choice["kind"] == "temperature"
    assert len(choice["options"]) == 2
    selected = next(option for option in choice["options"] if "Probe B" in option["label"])
    prepare_document(source, output, {choice["id"]: selected["value"]})
    assert [[[c.text for c in r.cells] for r in t.rows] for t in Document(output).tables] == [
        [head, maximum], [head, ["Probe B", "5.0", "11.0"]]]


def test_prepared_temperature_chart_contains_only_measured_maxima_and_preserves_tag(tmp_path):
    from backend.infrastructure.office.report_authoring.temperature_chart import C, R
    original = tmp_path / "working.docx"
    doc = Document()
    doc.add_paragraph("6. TEST RESULTS")
    tag = OxmlElement("w:sdt")
    props = OxmlElement("w:sdtPr")
    name = OxmlElement("w:tag")
    name.set(qn("w:val"), "connlab-report-result:run1")
    props.append(name)
    tag.append(props)
    content = OxmlElement("w:sdtContent")
    tag.append(content)
    doc.element.body.sectPr.addprevious(tag)
    content.append(doc.add_paragraph("Temperature rise (°C)")._p)
    content.append(add_table(doc, [["Measured rise / °C", "100 A", "200 A"], ["Channel 1", "6", "9"],
                                   ["Max", "7.1", "10.2"], ["Avg of Max", "6.1", "9.1"]])._tbl)
    content.append(doc.add_paragraph("Avg of Max fit: a=123.45")._p)
    raw = Part(PackURI("/word/embeddings/internal.xlsx"),
               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", b"private-raw-measurements")
    for index in range(3):
        drawing, chart = OxmlElement("w:drawing"), OxmlElement("c:chart")
        part = Part(PackURI(f"/word/charts/measurements{index}.xml"),
                    "application/vnd.openxmlformats-officedocument.drawingml.chart+xml",
                    f'<c:chartSpace xmlns:c="{C}"><c:chart/></c:chartSpace>'.encode())
        part.relate_to(raw, R + "/package")
        part.relate_to("file:///private-original.xlsx", R + "/externalLinkPath", is_external=True)
        chart.set(qn("r:id"), doc.part.relate_to(part, R + "/chart"))
        drawing.append(chart)
        paragraph = doc.add_paragraph()
        paragraph.add_run()._r.append(drawing)
        # One chart precedes the table and two follow it in the same report region.
        if index == 0:
            content.insert(1, paragraph._p)
        else:
            content.append(paragraph._p)
    doc.save(original)
    prepared = prepare_document(original, tmp_path / "public.docx", {})
    with ZipFile(prepared) as package:
        main = package.read("word/document.xml")
        assert b"connlab-report-result:run1" in main
        assert b"Channel 1" not in main and b"Avg of Max" not in main
        assert "word/embeddings/internal.xlsx" not in package.namelist()
        for index in range(3):
            assert b"private-original" not in package.read(f"word/charts/_rels/measurements{index}.xml.rels")
            data = etree.fromstring(package.read(f"word/charts/measurements{index}.xml"))
            assert len(data.findall(f".//{{{C}}}ser")) == 1
            assert [float(n.text) for n in data.findall(f".//{{{C}}}yVal//{{{C}}}v")] == [7.1, 10.2]
        embeds = [n for n in package.namelist() if n.endswith(".xlsx")]
        assert len(embeds) == 3
        for embed in embeds:
            book = load_workbook(BytesIO(package.read(embed)), data_only=True)
            assert list(book.active.values)[1:] == [(100, 7.1, "100 A"), (200, 10.2, "200 A")]
            book.close()


def test_vertical_temperature_table_keeps_measured_maximum_and_its_condition(tmp_path):
    source = tmp_path / "measurements.docx"
    doc = Document()
    doc.add_paragraph("6. TEST RESULTS")
    doc.add_paragraph("Temperature rise by condition (°C)")
    add_table(doc, [["Test Condition", "Current / A", "TC 1", "Max Temperature Rise (°C)", "Allowed maximum"],
                    ["Still air", "100", "4.2", "5.2", "40"], ["Airflow", "100", "2.2", "3.2", "40"],
                    ["Limit", "100", "N/A", "45", "45"]])
    doc.save(source)
    prepared = prepare_document(source, tmp_path / "public.docx", {})
    assert [[c.text for c in row.cells] for row in Document(prepared).tables[0].rows] == [
        ["Test Condition", "Current / A", "Max Temperature Rise (°C)"],
        ["Still air", "100", "5.2"], ["Airflow", "100", "3.2"]]


def test_unknown_temperature_columns_offer_only_observed_readings_across_all_conditions(tmp_path):
    src = tmp_path / "internal.docx"
    doc = Document()
    doc.add_paragraph("Temperature rise (°C)")
    add_table(doc, [["Test Condition", "Reading A", "Reading B", "Average"],
                    ["Still air", "8", "10", "9"], ["Airflow", "3", "5", "4"]])
    doc.save(src)
    [field] = inspect_document(src)["fields"]
    assert [o["label"] for o in field["options"]] == ["Reading A", "Reading B"]
    upper = field["options"][1]
    assert upper["rows"] == [["Still air", "10"], ["Airflow", "5"]]
    out = prepare_document(src, tmp_path / "public.docx", {field["id"]: upper["value"]})
    assert [[c.text for c in r.cells] for r in Document(out).tables[0].rows[1:]] == upper["rows"]


def test_sample_table_without_material_columns_still_prompts_for_auxiliary_parts(tmp_path):
    path = tmp_path / "internal.docx"
    doc = Document()
    doc.add_paragraph("3. SAMPLE DESCRIPTION")
    add_table(doc, [["Description", "Part #"], ["Mounting PCBs", "P-1"], ["Test bus-bar", "P-2"]])
    doc.save(path)
    fields = inspect_document(path)["fields"]
    assert [f["label"] for f in fields] == ["Mounting PCBs", "Test bus-bar"]
    with pytest.raises(ValueError, match="changed"):
        prepare_document(path, tmp_path / "unused.docx", {}, expected_source_sha256="0" * 64)
    with pytest.raises(ValueError, match="choices"):
        prepare_document(path, tmp_path / "unused.docx", None)


def test_multirow_summary_headers_name_each_condition_without_changing_the_word_table(tmp_path):
    src = tmp_path / "internal.docx"
    doc = Document()
    doc.add_paragraph("2. CONCLUSIONS")
    t = add_table(doc, [["Test Condition", "", ""], ["", "at 100 A", "at 200 A"],
                        ["Still air", "2.4 °C", "6.9 °C"]])
    t.cell(0, 1).merge(t.cell(0, 2)).text = "Maximum T-Rise"
    doc.save(src)
    [table] = inspect_document(src)["temperatures"]
    assert table["headers"] == ["Test Condition", "Maximum T-Rise at 100 A", "Maximum T-Rise at 200 A"]
    assert table["rows"] == [["Still air", "2.4 °C", "6.9 °C"]]
    out = prepare_document(src, tmp_path / "public.docx", {})
    assert len(Document(out).tables[0].rows) == 3
