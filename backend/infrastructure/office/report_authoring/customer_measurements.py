"""Project-owned result regions rendered into a customer copy from confirmed measurements."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree

from backend.infrastructure.office.customer_content_review import _Review
from backend.infrastructure.office.customer_content_temperature import review_temperature_table
from backend.infrastructure.office.report_authoring.region_parts import R, remove_replaced_region_parts
from backend.infrastructure.office.report_authoring.results_document import (
    measurement_table, node, result_notes, set_text, style_generated_section, summary, value_table,
)
from backend.infrastructure.office.report_authoring.word_copy import NS, text


def _paragraph(label):
    p = node('p')
    set_text(p, label)
    return p


def _region(tag, blocks):
    section, props, marker, content = (node(name) for name in ('sdt', 'sdtPr', 'tag', 'sdtContent'))
    marker.set(f'{{{NS["w"]}}}val', tag)
    props.append(marker)
    content.extend(blocks)
    section.extend([props, content])
    return section


def _marker(result):
    return '[[ConnLabCustomerEvidence-' + result['result_id'] + ']]'


def _write_package(source, output, edit):
    with ZipFile(source) as package:
        parts = {name: package.read(name) for name in package.namelist()}
    root = etree.fromstring(parts['word/document.xml'])
    removed = edit(root)
    parts['word/document.xml'] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    with ZipFile(output, 'x', ZIP_DEFLATED) as package:
        for name, data in remove_replaced_region_parts(parts, removed).items():
            package.writestr(name, data)


def stage_project_evidence(source, output, results):
    """Keep the insertion position, without sending raw channels, charts or workbooks through Word."""
    by_tag = {'connlab-report-result:' + item['result_id']: item for item in results}

    def edit(root):
        removed = set()
        for section in root.xpath('//w:sdt', namespaces=NS):
            tag = section.find('w:sdtPr/w:tag', NS)
            result = by_tag.get(tag.get(f'{{{NS["w"]}}}val')) if tag is not None else None
            if result:
                removed.update(val for item in section.iter() for key, val in item.attrib.items() if key.startswith('{'+R+'}'))
                section.getparent().replace(section, _paragraph(_marker(result)))
        summaries = {}
        for result in results:
            if result['kind'] == 'temperature':
                points = _measured(result)
                summaries[summary(result)] = '; '.join(f"{p['current']:g} A: measured Max {p['maximum']:g} °C" for p in points)
        for p in root.xpath('//w:tc/w:p', namespaces=NS):
            if text(p) in summaries:
                set_text(p, summaries[text(p)])
        return removed

    _write_package(source, output, edit)
    return output


def _measured(result):
    return [p for p in result['data']['analysis']['points'] if p['source_row'] is not None]


def customer_reference(result):
    return _region('connlab-customer-reference:' + result['result_id'],
                   [measurement_table(result), *map(_paragraph, result_notes(result))])


def project_supplements(results, decisions=None):
    review = _Review(decisions)
    sections = {}
    for result in results:
        kind = result['kind']
        label = f"Group {result['target']['group_label']}, Step {result['target']['step_token']}"
        heading = ('Related report evidence' if kind == 'external_reference' else 'Temperature rise') + ' — ' + label
        blocks = [_paragraph(heading)]
        if kind == 'temperature':
            points = _measured(result)
            if not points:
                raise ValueError(f'{label} has no confirmed measured temperature rise.')
            headers = ['Applied current', *[f"{p['current']:g} A" for p in points]]
            rows = [['Max T-Rise (°C)', *[f"{p['maximum']:g}" for p in points]]]
            review.temperatures.append(dict(label=label, headers=headers, rows=rows))
            blocks.append(value_table(headers, rows))
        elif kind == 'linked_temperature':
            for index, raw in enumerate(result['data']['blocks']):
                table = etree.fromstring(raw.encode())
                if table.tag != node('tbl').tag:
                    continue
                cells = [[text(cell).strip() for cell in row.findall('w:tc', NS)] for row in table.findall('w:tr', NS)]
                projected = review_temperature_table(table, cells, [heading], f"supp-{result['result_id']}-{index}", review)
                if projected and projected['rows']:
                    blocks.append(value_table(projected['headers'], projected['rows']))
                elif projected is None:
                    raise ValueError(f'{label}: label the measured current and maximum temperature rise in the linked table before generating.')
            blocks.append(customer_reference(result))
        elif kind == 'external_reference':
            blocks.append(customer_reference(result))
        else:
            raise ValueError('Unsupported result in customer temperature evidence.')
        sections[_marker(result)] = _region('connlab-report-result:' + result['result_id'], blocks)
    if decisions is not None and set(decisions) != review.used:
        raise ValueError('The selected temperature rows changed. Review the current report.')
    return review, sections


def insert_customer_supplements(source: Path, output: Path, sections):
    def edit(root):
        body = root.find('w:body', NS)
        for marker, section in sections.items():
            style_generated_section(section, body.find('w:tbl', NS))
            placeholders = [p for p in body.xpath('.//w:p', namespaces=NS) if text(p) == marker]
            if len(placeholders) > 1:
                raise ValueError('Word produced two copies of the same temperature evidence.')
            if placeholders:
                placeholders[0].getparent().replace(placeholders[0], section)
            else:
                # E-4515 omits internal appendices. Carry their reviewed summary across once.
                end = next((block for block in body if 'end of report' in text(block).casefold()), body.find('w:sectPr', NS))
                body.insert(body.index(end) if end is not None else len(body), section)
        return set()
    _write_package(source, output, edit)
