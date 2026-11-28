"""Project working-copy adapter for reviewed E-4515 customer downloads."""
from dataclasses import asdict
from hashlib import sha256
from contextlib import contextmanager
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
from backend.infrastructure.office.office_protected_document_gateway import ProtectedWordPackageGateway
from backend.infrastructure.office.office_lifecycle import OfficeAutomationUnavailable
from backend.infrastructure.office.report_authoring.customer_audit import audit_customer_package
from backend.infrastructure.office.report_authoring.results_document import measurement_table, result_notes
from backend.infrastructure.office.customer_content_review import inspect_document, prepare_document
from backend.infrastructure.office.customer_report_notices import read_customer_notices
from backend.infrastructure.office.report_authoring.customer_measurements import (
    customer_reference, insert_customer_supplements, project_supplements, stage_project_evidence,
)
from backend.infrastructure.office.report_authoring.word_copy import NS, text
from backend.infrastructure.office.report_authoring.pagination import protect_table_starts


class CustomerReportCopy:
    def __init__(self, *, converter, template, protected=None):
        self.converter, self.template = converter, template
        self.protected = protected or ProtectedWordPackageGateway()

    @contextmanager
    def _project_input(self, source, results, directory, expected_sha256=None):
        # The same immutable snapshot binds choices, generated lineage and project evidence.
        snapshot = Path(directory) / 'internal.docx'
        raw = Path(source).read_bytes()
        digest = sha256(raw).hexdigest()
        if expected_sha256 is not None and digest != expected_sha256:
            raise ValueError('The internal report changed. Reopen it before generating.')
        snapshot.write_bytes(raw)
        if not results:
            yield snapshot, digest
            return
        with self.protected.readable_copy(snapshot) as readable:
            staged = stage_project_evidence(readable, Path(directory) / 'project.docx', results)
            yield staged, digest

    def inspect_content(self, source, temperature_results=()):
        with TemporaryDirectory(prefix='connlab-customer-') as directory:
            with self._project_input(source, temperature_results, directory) as (staged, digest):
                review = inspect_document(staged)
                extra, _ = project_supplements(temperature_results)
                review['fields'].extend(extra.fields)
                review['temperatures'].extend(extra.temperatures)
                return {**review, 'source_sha256': digest}

    review_notices = staticmethod(read_customer_notices)

    def generate(self, source, output, temperature_results):
        self.generate_reviewed(source, output, temperature_results, {}, None)

    def generate_reviewed(self, source, output, temperature_results, decisions, source_sha256):
        if output.exists():
            raise ValueError('Customer report output exists; originals are never overwritten.')
        with TemporaryDirectory(prefix='connlab-customer-') as directory:
            root = Path(directory)
            with self._project_input(source, temperature_results, directory, source_sha256) as (staged, digest):
                supplement_choices = {k: v for k, v in decisions.items() if k.startswith('tsupp-')}
                body_choices = {k: v for k, v in decisions.items() if k not in supplement_choices}
                reviewed = prepare_document(staged, root / 'reviewed.docx', body_choices)
                _, sections = project_supplements(temperature_results, supplement_choices)
                converted = root / 'customer.docx'
                try:
                    self.converter.generate_customer_report(source_path=reviewed, template_path=self.template(),
                        output_path=converted, lineage_sha256=digest)
                except OfficeAutomationUnavailable as exc:
                    raise ValueError('Customer conversion requires Microsoft Word on this computer.') from exc
            plain = root / 'editable.docx'
            protection = self.protected.stage_editable_copy(converted, plain)
            if sections:
                supplemented = root / 'supplemented.docx'
                insert_customer_supplements(plain, supplemented, sections)
                plain = supplemented
            paginated = root / 'paginated.docx'
            preserve_customer_table_starts(plain, paginated)
            self.protected.restore_password_protection(paginated, protection)
            with output.open('xb') as target:
                target.write(paginated.read_bytes())

    def audit(self, source, *, sensitive_terms, forbidden_project_ids, reviewed_parts, expected_project_dl=None, scoped_references=()):
        allowed_regions = {}
        for result in scoped_references:
            data = result['data']
            if not data['adoption'].get('confirmed') or not data['adoption'].get('customer_reference_allowed'):
                continue
            if result['kind'] == 'linked_temperature':
                expected = ''.join(text(etree.fromstring(block.encode())) for block in data['blocks']) + ''.join(data['adoption_notes'])
            else:
                expected = text(measurement_table(result)) + ''.join(result_notes(result))
            allowed_regions['connlab-report-result:' + result['result_id']] = expected
            allowed_regions['connlab-customer-reference:' + result['result_id']] = text(customer_reference(result))
            # Also recognize already-retained reports generated before customer summaries.
            customer_expected = expected if result['kind'] == 'linked_temperature' else f"Related report evidence — Group {result['target']['group_label']}, Step {result['target']['step_token']}" + expected
            allowed_regions['connlab-customer-temperature:' + result['result_id']] = customer_expected
        with self.protected.readable_copy(source) as readable:
            audit = asdict(audit_customer_package(readable, sensitive_terms=sensitive_terms,
                forbidden_project_ids=forbidden_project_ids, reviewed_parts=reviewed_parts, allowed_reference_regions=allowed_regions))
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
