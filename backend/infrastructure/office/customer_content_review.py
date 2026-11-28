"""Inspect customer-visible report tables and prepare a separate, reviewed Word source."""
from __future__ import annotations

import re
from contextlib import contextmanager
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile, is_zipfile

from docx.oxml import parse_xml
from docx.oxml.ns import qn
from lxml import etree

from backend.infrastructure.office.customer_report_document_gateway import (
    _MATERIAL_PLACEHOLDERS, _NON_PRODUCT_SAMPLE_PATTERN, _SOURCE_HEADINGS,
    _customer_sample_material, _matches_heading, _sample_table_columns,
)
from backend.infrastructure.office.office_protected_document_gateway import ProtectedWordPackageGateway
from backend.infrastructure.office.customer_content_temperature import _TEMPERATURE, review_temperature_table
from backend.infrastructure.office.customer_content_charts import customer_chart_parts
from backend.infrastructure.office.report_authoring.region_parts import R, remove_replaced_region_parts


@contextmanager
def _read_source(source, expected_hash=None):
    if hasattr(source, "read"):
        source.seek(0)
        raw = source.read()
    else:
        raw = Path(source).read_bytes()
    fingerprint = sha256(raw).hexdigest()
    if expected_hash is not None and fingerprint != expected_hash:
        raise ValueError("The internal report changed. Review the current file before generating.")
    memory = BytesIO(raw)
    with TemporaryDirectory(prefix="connlab-content-") as directory:
        if is_zipfile(memory):
            readable = memory
        else:
            snapshot = Path(directory) / "input.docx"
            snapshot.write_bytes(raw)
            readable = Path(directory) / "editable.docx"
            ProtectedWordPackageGateway().stage_editable_copy(snapshot, readable)
        try:
            with ZipFile(readable) as package:
                infos = package.infolist()
                if (len(infos) > 5000 or sum(i.file_size for i in infos) > 256 * 1024 * 1024
                        or len({i.filename for i in infos}) != len(infos)):
                    raise ValueError("The expanded Word document exceeds the supported package limits.")
                xml = package.read("word/document.xml")
                if b"<!DOCTYPE" in xml:
                    raise ValueError("Unsupported Word document XML.")
                root = parse_xml(xml)
                yield package, root, fingerprint
        except (BadZipFile, KeyError, etree.XMLSyntaxError) as exc:
            raise ValueError("Cannot read the internal Word document. Choose a readable .docx file.") from exc


def _text(element):
    paragraphs = [element] if element.tag == qn("w:p") else element.xpath(".//w:p")
    lines = []
    for paragraph in paragraphs:
        nodes = paragraph.xpath(".//*[self::w:t or self::w:br or self::w:tab][not(ancestor::w:del or ancestor::w:moveFrom)]")
        lines.append("".join((n.text or "") if n.tag == qn("w:t") else " " for n in nodes))
    return " ".join(" ".join(lines).split())


def _cells(row):
    return row.findall(qn("w:tc"))


def _set_cell(cell, value):
    # Keep cell and text styling, without carrying hidden field codes or revision
    # history containing the old material designation into the public value.
    p_style = cell.find(f".//{qn('w:pPr')}")
    r_style = cell.find(f".//{qn('w:rPr')}")
    cell.clear_content()
    paragraph = etree.SubElement(cell, qn("w:p"))
    if p_style is not None:
        paragraph.append(deepcopy(p_style))
    run = etree.SubElement(paragraph, qn("w:r"))
    if r_style is not None:
        run.append(deepcopy(r_style))
    etree.SubElement(run, qn("w:t")).text = value


class _Review:
    def __init__(self, decisions=None):
        self.decisions = decisions
        self.fields = []
        self.samples = []
        self.temperatures = []
        self.charts = {}
        self.used = set()

    def choice(self, field):
        self.fields.append(field)
        if self.decisions is None:
            return None
        self.used.add(field["id"])
        if field.get("depends_on") and self.decisions.get(field["depends_on"]) == "omit":
            return None
        value = self.decisions.get(field["id"])
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Choose a customer report value for {field['label']}.")
        if "options" in field and value not in {option["value"] for option in field["options"]}:
            raise ValueError(f"Invalid choice for {field['label']}. Review the current report.")
        if len(value) > 180 or re.search(r"[\x00-\x1f\x7f]", value):
            raise ValueError("Enter a short, single-line customer material name.")
        return value.strip()


def _material_label(value, role):
    label = _customer_sample_material(value, role)
    if label != value or label in {"High Temperature Resin", "Copper Alloy"}:
        return label
    if value.casefold() in _MATERIAL_PLACEHOLDERS:
        return value
    if re.fullmatch(r"(?:stainless steel|steel|alumin[iu]+m|ceramic|glass|metal|copper|titanium|zinc)", value, re.I):
        return value
    return None


def _sample_table(table, index, review, *, sample_section):
    rows = table.findall(qn("w:tr"))
    if not rows:
        return
    columns = _sample_table_columns((_text(cell) for cell in _cells(rows[0])), material_required=not sample_section)
    if not columns:
        return
    for row_index, row in enumerate(rows[1:], 1):
        cells = _cells(row)
        if len(cells) < max(columns.values()):
            raise ValueError("The sample table contains a merged data row. Check the sample descriptions in Word.")
        description = _text(cells[columns["description"] - 1])
        part = _text(cells[columns["part"] - 1])
        sample = {"description": description, "part_number": part, "base_material": "", "housing_material": ""}
        review.samples.append(sample)
        key = f"t{index}-r{row_index}"
        decision = None
        if _NON_PRODUCT_SAMPLE_PATTERN.search(description):
            sample["decision_id"] = key
            decision = review.choice(dict(id=key, kind="sample", label=description, part_number=part,
                                          options=[{"value": "keep", "label": "Keep"}, {"value": "omit", "label": "Omit"}]))
        for role in ("base", "housing"):
            if role not in columns:
                continue
            cell = cells[columns[role] - 1]
            value = _text(cell)
            public = _material_label(value, role)
            if public is None:
                field_id = f"{key}-{role}"
                sample[f"{role}_decision_id"] = field_id
                field = dict(id=field_id, kind="material", label=f"{description} — {role.title()} material",
                             part_number=part, value=value)
                if "decision_id" in sample:
                    field["depends_on"] = key
                public = review.choice(field)
            sample[f"{role}_material"] = public or ""
            if review.decisions is not None and public is not None and public != value:
                _set_cell(cell, public)
        if decision == "omit":
            table.remove(row)


def _scan(root, decisions):
    review = _Review(decisions)
    section = None
    index = 0
    context = []
    temperature = None
    temperature_region = None
    pending_charts = []
    pending_region = None

    def bind(charts, summary):
        for chart in charts:
            rid = chart.get(qn("r:id"))
            if not rid or rid in review.charts and review.charts[rid] is not summary:
                raise ValueError("A temperature chart refers to more than one condition. Check the internal report.")
            review.charts[rid] = summary

    def check_unbound():
        if pending_charts:
            raise ValueError("A temperature chart has no matching measurement table. Place it beside its measured maximum table in the internal report.")
    body = root.find(qn("w:body"))
    if body is None:
        raise ValueError("The selected Word file has no document body.")
    blocks = body.xpath(".//*[self::w:p or self::w:tbl][not(ancestor::w:tbl or ancestor::w:del or ancestor::w:moveFrom)]")
    for block in blocks:
        region = next((node for node in block.iterancestors(qn("w:sdt"))
                       if any((t.get(qn("w:val")) or "").startswith("connlab-report-result:")
                              for t in node.findall(f"{qn('w:sdtPr')}/{qn('w:tag')}"))), None)
        if region is not temperature_region:
            temperature = None
        if region is not pending_region:
            check_unbound()
        if block.tag == qn("w:p"):
            label = _text(block)
            # Authoring adds these internal notes after the measurement table.
            # Restrict removal to its tagged result, preserving authored prose.
            if temperature is not None and temperature_region is not None and temperature_region in block.iterancestors():
                if label.startswith(("Measured temperature rise is listed above. Regression model:",
                                     "Max fit:", "Avg of Max fit:", "Displayed coefficients are rounded",
                                     "Tools effective ", "Retained Tools calculator ", "Retained Tools derating ")):
                    if decisions is not None:
                        block.getparent().remove(block)
                    continue
            charts = block.xpath(".//c:chart")
            if len(label) < 85:
                for number, heading in enumerate(_SOURCE_HEADINGS, 1):
                    if _matches_heading(label, number, heading):
                        check_unbound()
                        section = number
                        context.clear()
                        temperature = None
                        break
            if label:
                new_caption = _TEMPERATURE.search(label) and not re.match(r"notes?\b|\*|fig(?:ure)?[.\s\d]", label, re.I)
                if new_caption:
                    temperature = None
                    if pending_charts and context and _TEMPERATURE.search(context[-1]):
                        check_unbound()
                context = [*context[-2:], label]
                if not re.match(r"note\b|^\*|fig(?:ure)?[.\s\d]|measured temperature|temperature rise", label, re.I):
                    temperature = None
            if charts:
                if temperature is not None:
                    bind(charts, temperature)
                elif any(_TEMPERATURE.search(line) for line in context):
                    pending_charts.extend(charts)
                    pending_region = region
            continue
        if section in {None, 1, 2, 3}:
            _sample_table(block, index, review, sample_section=section == 3)
        temperature = None
        temperature_region = region
        if section in {None, 2, 6} or temperature_region is not None:
            rows = [[_text(cell) for cell in _cells(row)] for row in block.findall(qn("w:tr"))]
            temperature = review_temperature_table(block, rows, context, index, review)
        if temperature is not None:
            bind(pending_charts, temperature)
            pending_charts.clear()
        else:
            check_unbound()
        context.clear()
        index += 1
    check_unbound()
    if decisions is not None and set(decisions) - review.used:
        raise ValueError("The customer choices do not match the current internal report.")
    return review


def inspect_document(path):
    with _read_source(path) as (_, root, digest):
        review = _scan(root, None)
        return dict(source_sha256=digest, fields=review.fields, samples=review.samples, temperatures=review.temperatures)


def prepare_document(source, output, decisions, *, expected_source_sha256=None):
    output = Path(output)
    if output.exists():
        raise ValueError("The customer conversion needs a new output path.")
    if not isinstance(decisions, dict):
        raise ValueError("Provide the customer report choices before generating.")
    with _read_source(source, expected_source_sha256) as (package, root, _):
        def relationship_ids():
            return {value for node in root.iter() for attr, value in node.attrib.items() if attr.startswith("{" + R + "}")}

        old_ids = relationship_ids()
        review = _scan(root, decisions)
        updates, removed = customer_chart_parts(package, review.charts)
        updates["word/document.xml"] = etree.tostring(root, encoding="UTF-8", xml_declaration=True, standalone=True)
        dropped_ids = old_ids - relationship_ids()
        if dropped_ids:
            # Images and workbooks attached only to omitted rows must leave the
            # package too, while media shared with a retained row stays intact.
            parts = {n: package.read(n) for n in package.namelist() if n not in updates and n not in removed}
            updates = remove_replaced_region_parts({**parts, **updates}, dropped_ids)
            removed.update(set(package.namelist()) - updates.keys())
        with output.open("xb") as stream:
            try:
                with ZipFile(stream, "w", ZIP_DEFLATED) as target:
                    for info in package.infolist():
                        if info.filename not in removed and info.filename not in updates:
                            target.writestr(info, package.read(info))
                    for name, content in updates.items():
                        target.writestr(name, content)
            except Exception:
                stream.close()
                output.unlink(missing_ok=True)
                raise
    return output
