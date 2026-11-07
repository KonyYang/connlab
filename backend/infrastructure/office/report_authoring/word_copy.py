"""Local XML edits retain the remaining approved Word package byte-for-byte."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from hashlib import sha256
import re
from lxml import etree
from backend.infrastructure.office.office_protected_document_gateway import ProtectedWordPackageGateway

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def text(element):
    return "".join(element.xpath(".//w:t/text()", namespaces=NS))


class ReportCopyWriter:
    def __init__(self, protected=None):
        self.protected = protected or ProtectedWordPackageGateway()

    def preview_facts(self, source: Path, replacements):
        _validate_replacements(replacements)
        with self.protected.readable_copy(source) as readable, ZipFile(readable) as archive:
            paragraphs = []
            for name in archive.namelist():
                if _text_part(name):
                    root = etree.fromstring(archive.read(name))
                    paragraphs.extend((name, index, paragraph) for index, paragraph in enumerate(root.xpath("//w:p", namespaces=NS)))
            changes = []
            for replacement in replacements:
                old, new, target = replacement_parts(replacement)
                selected = [(name, paragraph) for name, index, paragraph in paragraphs
                            if fact_target_matches(name, index, paragraph, target)]
                matches = [(name, _paragraph_text(paragraph).count(old)) for name, paragraph in selected if old in _paragraph_text(paragraph)]
                count = sum(item[1] for item in matches)
                if not count:
                    raise ValueError(f"The report does not contain the exact old text: {old}. Review the mapping before applying.")
                changes.append({"old": old, "new": new, "occurrences": count, "parts": sorted({item[0] for item in matches}),
                                **({'target': target} if target else {})})
            return changes

    def fact_targets(self, source: Path, old_text: str):
        if not old_text.strip():
            raise ValueError('Enter the exact old report text before choosing its location.')
        targets = []
        with self.protected.readable_copy(source) as readable, ZipFile(readable) as archive:
            for name in archive.namelist():
                if not _text_part(name):
                    continue
                root = etree.fromstring(archive.read(name))
                for index, paragraph in enumerate(root.xpath('//w:p', namespaces=NS)):
                    value = _paragraph_text(paragraph)
                    if old_text in value:
                        targets.append({'text': value, 'target': {'part': name, 'paragraph': index,
                            'sha256': sha256(etree.tostring(paragraph, method='c14n')).hexdigest()}})
        return targets

    def apply_facts(self, source: Path, output: Path, replacements):
        self.preview_facts(source, replacements)
        protection = self.protected.stage_editable_copy(source, output)
        changed = {}
        with ZipFile(output) as archive:
            for name in archive.namelist():
                if not _text_part(name):
                    continue
                root = etree.fromstring(archive.read(name))
                count = 0
                for index, paragraph in enumerate(root.xpath("//w:p", namespaces=NS)):
                    selected = [replacement_parts(item) for item in replacements
                                if fact_target_matches(name, index, paragraph, replacement_parts(item)[2])]
                    for old, new, _ in selected:
                        count += _replace_paragraph(paragraph, old, new)
                if count:
                    changed[name] = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
            payload = BytesIO()
            with ZipFile(payload, "w", ZIP_DEFLATED) as target:
                for info in archive.infolist():
                    target.writestr(info, changed.get(info.filename, archive.read(info.filename)))
        output.write_bytes(payload.getvalue())
        self.protected.restore_password_protection(output, protection)

    def prepare(self, source: Path, output: Path, *, source_dl: str, project_dl: str, reference: bool):
        protection = self.protected.stage_editable_copy(source, output)
        if not reference:
            self.protected.restore_password_protection(output, protection)
            return
        issues = ["Review project facts, specification revision/date, sample identities, photos and appendices before delivery."]
        identity_pattern = (re.compile(re.escape(source_dl) + r"(?![A-Za-z0-9-])", re.I)
                            if source_dl.strip() else None)
        if identity_pattern is None:
            issues.append("This template has no previous project identity. Fill and confirm the current project identity before delivery.")
        replacements = {}
        with ZipFile(output) as archive:
            for name in archive.namelist():
                if name != "word/document.xml" and not re.fullmatch(r"word/(header|footer)\d+\.xml", name):
                    continue
                root = etree.fromstring(archive.read(name))
                changed = 0
                if identity_pattern is not None:
                    for paragraph in root.xpath("//w:p", namespaces=NS):
                        changed += _replace_paragraph_pattern(paragraph, identity_pattern, project_dl)
                if name == "word/document.xml":
                    cleared_tables = set()
                    for table in root.xpath("//w:body/w:tbl", namespaces=NS):
                        rows = table.findall("w:tr", NS)
                        if not rows:
                            continue
                        headers = [text(cell).strip().casefold() for cell in rows[0].findall("w:tc", NS)]
                        columns = [index for index, label in enumerate(headers) if label in {"result", "comment", "results", "comments"}]
                        if not columns:
                            continue
                        for row in rows[1:]:
                            cells = row.findall("w:tc", NS)
                            for index in columns:
                                if index < len(cells):
                                    for node in cells[index].xpath(".//w:t", namespaces=NS):
                                        if node.text:
                                            cleared_tables.add(table)
                                        changed += bool(node.text)
                                        node.text = ""
                    # Clearing old results can shorten the page flow and strand
                    # a later Group heading. Preserve explicit pagination choices.
                    # Local import avoids pagination's shared XML-helper cycle.
                    from backend.infrastructure.office.report_authoring.pagination import reflow_headings, protect_reflow_headings
                    protect_reflow_headings(reflow_headings(root, cleared_tables))
                    issues.append("Previous project's Result and Comment cells were cleared; no prior Pass or exception was adopted.")
                if changed:
                    replacements[name] = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
            payload = BytesIO()
            with ZipFile(payload, "w", ZIP_DEFLATED) as target:
                for info in archive.infolist():
                    target.writestr(info, replacements.get(info.filename, archive.read(info.filename)))
        output.write_bytes(payload.getvalue())
        self.protected.restore_password_protection(output, protection)
        return issues


def _text_part(name):
    return name == "word/document.xml" or bool(re.fullmatch(r"word/(header|footer)\d+\.xml", name))


def _paragraph_nodes(paragraph):
    return paragraph.xpath("./w:r/w:t|./w:hyperlink/w:r/w:t", namespaces=NS)


def _paragraph_text(paragraph):
    return "".join(node.text or "" for node in _paragraph_nodes(paragraph))


def _replace_paragraph(paragraph, old, new):
    return _replace_paragraph_pattern(paragraph, re.compile(re.escape(old)), new)


def _replace_paragraph_pattern(paragraph, pattern, new):
    joined = _paragraph_text(paragraph)
    positions = [match.span() for match in pattern.finditer(joined)]
    for start, stop in reversed(positions):
        offset = 0
        inserted = False
        for node in _paragraph_nodes(paragraph):
            value = node.text or ""
            end = offset + len(value)
            if offset < stop and end > start:
                prefix = value[:max(0, start - offset)]
                suffix = value[max(0, stop - offset):]
                node.text = prefix + (new if not inserted else "") + suffix
                node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                inserted = True
            offset = end
    return len(positions)


def _validate_replacements(replacements):
    for index, replacement in enumerate(replacements):
        old, new, target = replacement_parts(replacement)
        if not old:
            raise ValueError('Replacement source text must not be empty.')
        for other_index, other in enumerate(replacements):
            other_old, _, other_target = replacement_parts(other)
            separate = target and other_target and (target['part'], target['paragraph']) != (other_target['part'], other_target['paragraph'])
            if index != other_index and not separate and (old in other_old or other_old in old or other_old in new):
                raise ValueError('Overlapping or cascading replacements need separate reviewed updates.')


def replacement_parts(replacement):
    if isinstance(replacement, dict):
        return replacement['old'], replacement['new'], replacement.get('target')
    return *replacement, None


def fact_target_matches(part, index, paragraph, target):
    if target is None:
        return True
    if target['part'] != part or target['paragraph'] != index:
        return False
    if sha256(etree.tostring(paragraph, method='c14n')).hexdigest() != target['sha256']:
        raise ValueError('The exact report target changed. Select its location again.')
    return True
