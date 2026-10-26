"""Existing E-4515 conversion plus explicitly selected editable temperature evidence."""
from dataclasses import asdict
from io import BytesIO
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
from backend.infrastructure.office.office_protected_document_gateway import ProtectedWordPackageGateway
from backend.infrastructure.office.office_lifecycle import OfficeAutomationUnavailable
from backend.infrastructure.office.report_authoring.customer_audit import audit_customer_package
from backend.infrastructure.office.report_authoring.results_document import measurement_table, result_notes, style_generated_section, node, set_text
from backend.infrastructure.office.report_authoring.word_copy import NS, text
from backend.infrastructure.office.report_authoring.pagination import protect_table_starts


class CustomerReportCopy:
    def __init__(self, *, converter, template, temperature_chart, protected=None):
        self.converter, self.template, self.temperature_chart = converter, template, temperature_chart
        self.protected = protected or ProtectedWordPackageGateway()

    def generate(self, source, output, temperature_results):
        if output.exists():
            raise ValueError('Customer report output exists; originals are never overwritten.')
        with TemporaryDirectory(prefix='connlab-customer-') as directory:
            converted = Path(directory)/'customer.docx'
            try:
                self.converter.generate_customer_report(source_path=source, template_path=self.template(), output_path=converted)
            except OfficeAutomationUnavailable as exc:
                raise ValueError('Customer conversion requires a working Microsoft Word installation on the server computer. No original was changed.') from exc
            plain = Path(directory)/'editable.docx'
            protection = self.protected.stage_editable_copy(converted, plain)
            for index, result in enumerate(temperature_results):
                if result['kind'] != 'temperature':
                    raise ValueError('Only selected temperature measurements belong in the customer temperature supplement.')
                if self._contains_complete_temperature(plain, result):
                    continue
                tag = 'connlab-customer-temperature:' + result['result_id']
                self._append_temperature(plain, result, tag)
                charted = Path(directory)/f'chart-{index}.docx'
                self.temperature_chart(plain, charted, result['data']['analysis'], tag)
                plain = charted
            paginated = Path(directory)/'paginated.docx'
            preserve_customer_table_starts(plain, paginated)
            plain = paginated
            output.write_bytes(plain.read_bytes())
            self.protected.restore_password_protection(output, protection)

    @staticmethod
    def _contains_complete_temperature(path, result):
        with ZipFile(path) as package:
            root = etree.fromstring(package.read('word/document.xml'))
            markers = {f"connlab-report-result:{result['result_id']}", f"connlab-customer-temperature:{result['result_id']}"}
            matches = [section for section in root.xpath('//w:sdt', namespaces=NS)
                if (tag := section.find('w:sdtPr/w:tag', NS)) is not None and tag.get(f'{{{NS["w"]}}}val') in markers]
            if len(matches) > 1:
                raise ValueError('Customer conversion duplicated a temperature evidence region. Review the generated copy before continuing.')
            if not matches:
                return False
            section = matches[0]
            charts = section.xpath('.//*[local-name()="chart"]')
            if not section.xpath('.//w:tbl', namespaces=NS) or not charts:
                raise ValueError('The converted temperature evidence is incomplete. Its editable table and curve must both be retained.')
            return True

    @staticmethod
    def _append_temperature(path, result, tag):
        with ZipFile(path) as source:
            root = etree.fromstring(source.read('word/document.xml'))
            body = root.find('w:body', NS)
            section = node('sdt'); properties = node('sdtPr'); marker = node('tag')
            marker.set(f'{{{NS["w"]}}}val', tag); properties.append(marker); section.append(properties)
            content = node('sdtContent')
            heading = node('p'); set_text(heading, f"Temperature rise — Group {result['target']['group_label']}, Step {result['target']['step_token']}")
            content.append(heading); content.append(measurement_table(result))
            for line in result_notes(result):
                paragraph = node('p'); set_text(paragraph, line); content.append(paragraph)
            section.append(content)
            style_generated_section(section, body.find('w:tbl', NS))
            index = next((i for i, block in enumerate(body) if 'End of Report' in text(block)),
                         len(body)-1 if len(body) and body[-1].tag == node('sectPr').tag else len(body))
            body.insert(index, section)
            buffer = BytesIO()
            with ZipFile(buffer, 'w', ZIP_DEFLATED) as target:
                for info in source.infolist():
                    target.writestr(info, etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
                        if info.filename == 'word/document.xml' else source.read(info.filename))
        path.write_bytes(buffer.getvalue())

    def audit(self, source, *, sensitive_terms, forbidden_project_ids, reviewed_parts, expected_project_dl=None):
        with self.protected.readable_copy(source) as readable:
            audit = asdict(audit_customer_package(readable, sensitive_terms=sensitive_terms,
                forbidden_project_ids=forbidden_project_ids, reviewed_parts=reviewed_parts))
            if expected_project_dl:
                # The existing E-4515 projection appends exactly -CR (optionally followed
                # by a separate Rev.X label); arbitrary project-number prefixes do not match.
                pattern = re.compile(r'(?<![A-Za-z0-9-])' + re.escape(expected_project_dl) + r'(?:-CR)?(?![A-Za-z0-9-])', re.I)
                with ZipFile(readable) as package:
                    visible = []
                    for name in package.namelist():
                        if name == 'word/document.xml' or re.fullmatch(r'word/(?:header|footer)\d+\.xml', name):
                            tree = etree.fromstring(package.read(name))
                            visible.extend(text(paragraph) for paragraph in tree.xpath('//w:p', namespaces=NS))
                if not any(pattern.search(value) for value in visible):
                    audit['issues'] = [*audit['issues'], {'code': 'missing_current_project_identity', 'location': 'report',
                        'message': 'The customer copy does not contain the current project identity. Fill the approved template identity before delivery.', 'sha256': None}]
                    audit['passed'] = False
            return audit

    def part(self, source, name):
        # Only expose a retained package part, never resolve the name as a disk path.
        with self.protected.readable_copy(source) as readable, ZipFile(readable) as package:
            if name not in package.namelist():
                raise LookupError('Customer package part not found.')
            info = package.getinfo(name)
            if info.file_size > 50 * 1024 * 1024:
                raise ValueError('Package part is too large to download for review.')
            return package.read(name)


def preserve_customer_table_starts(source, output):
    """Keep a customer table's opening together without chaining its remaining data rows.

    Called only on the newly generated plaintext copy. No source/template properties or
    global styles change; all non-document package parts retain their exact bytes.
    """
    if output.exists():
        raise ValueError('Customer pagination output already exists.')
    with ZipFile(source) as package:
        root = etree.fromstring(package.read('word/document.xml'))
        protect_table_starts(root, customer=True)
        with ZipFile(output, 'w', ZIP_DEFLATED) as target:
            for info in package.infolist():
                target.writestr(info, etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
                    if info.filename == 'word/document.xml' else package.read(info.filename))
