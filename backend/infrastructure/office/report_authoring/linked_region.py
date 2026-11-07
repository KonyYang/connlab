"""Adopt an explicitly selected Word region and only its safe relationship closure."""
from base64 import b64decode, b64encode
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import posixpath
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree

from backend.infrastructure.office.office_protected_document_gateway import ProtectedWordPackageGateway
from backend.infrastructure.office.report_authoring.word_copy import NS, text

W = NS['w']
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
P = 'http://schemas.openxmlformats.org/package/2006/relationships'
C = 'http://schemas.openxmlformats.org/drawingml/2006/chart'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'


def xml(raw):
    if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
        raise ValueError('Document declarations are unsupported in an adopted region.')
    tree = etree.fromstring(raw, etree.XMLParser(resolve_entities=False, no_network=True))
    if tree.getroottree().docinfo.doctype:
        raise ValueError('Document declarations are unsupported in an adopted region.')
    return tree


def serialized(tree):
    return etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)


def rels_name(owner):
    return posixpath.join(posixpath.dirname(owner), '_rels', posixpath.basename(owner) + '.rels')


def relationship_target(owner, value):
    target = posixpath.normpath(posixpath.join(posixpath.dirname(owner), value))
    if target.startswith(('../', '/')) or ':' in target or '\\' in target:
        raise ValueError('Unsafe adopted document relationship.')
    return target


def freeze_chart(tree):
    refs = tree.findall('.//{%s}numRef' % C) + tree.findall('.//{%s}strRef' % C)
    if not refs or not tree.findall('.//{%s}ser' % C):
        raise ValueError('The linked chart has no complete native cached data.')
    for ref in refs:
        numeric = ref.tag == f'{{{C}}}numRef'
        cache = ref.find(f'{{{C}}}' + ('numCache' if numeric else 'strCache'))
        count = cache.find(f'{{{C}}}ptCount') if cache is not None else None
        points = cache.findall(f'{{{C}}}pt') if cache is not None else []
        if count is None or int(count.get('val', '0')) != len(points) or not points or {p.get('idx') for p in points} != {str(i) for i in range(len(points))}:
            raise ValueError('The linked chart cache is incomplete; no missing points can be invented.')
        if any(p.find(f'{{{C}}}v') is None or p.find(f'{{{C}}}v').text is None for p in points):
            raise ValueError('The linked chart cache has missing values.')
        if ref.getparent().tag == f'{{{C}}}tx':
            if numeric or len(points) != 1:
                raise ValueError('A chart series title requires one cached text value.')
            literal = etree.Element(f'{{{C}}}v')
            literal.text = points[0].find(f'{{{C}}}v').text
        else:
            literal = etree.Element(f'{{{C}}}' + ('numLit' if numeric else 'strLit'))
            literal.extend(deepcopy(list(cache)))
        ref.getparent().replace(ref, literal)
    for external in tree.findall('.//{%s}externalData' % C):
        external.getparent().remove(external)


def resolve_theme_colors(tree, theme):
    """Freeze selected colors without replacing the target report's global theme."""
    aliases = {'bg1': 'lt1', 'tx1': 'dk1', 'bg2': 'lt2', 'tx2': 'dk2', 'background1': 'lt1', 'text1': 'dk1', 'background2': 'lt2', 'text2': 'dk2', 'hyperlink': 'hlink', 'followedHyperlink': 'folHlink'}
    def color(key):
        entry = theme.find(f'.//{{{A}}}clrScheme/{{{A}}}{aliases.get(key, key)}') if theme is not None else None
        if entry is None or not len(entry):
            raise ValueError('The adopted region uses an unresolved theme color.')
        value = entry[0].get('lastClr') or entry[0].get('val')
        if value is None or len(value) != 6:
            raise ValueError('The adopted region uses an unsupported theme color.')
        return value
    for item in tree.iter():
        if item.tag == f'{{{A}}}schemeClr':
            item.tag = f'{{{A}}}srgbClr'; item.set('val', color(item.get('val')))
        for theme_attr, direct_attr in [('themeColor', 'val'), ('themeFill', 'fill')]:
            key = item.get(f'{{{W}}}{theme_attr}')
            if key:
                value = color(key)
                for modifier, tint in [('themeTint', True), ('themeShade', False), ('themeFillTint', True), ('themeFillShade', False)]:
                    amount = item.get(f'{{{W}}}{modifier}')
                    if amount:
                        ratio = int(amount, 16) / 255
                        value = ''.join(f'{round(255 - (255 - int(value[i:i+2], 16)) * (1 - ratio)) if tint else round(int(value[i:i+2], 16) * ratio):02X}' for i in (0, 2, 4))
                        del item.attrib[f'{{{W}}}{modifier}']
                item.set(f'{{{W}}}{direct_attr}', value); del item.attrib[f'{{{W}}}{theme_attr}']


class LinkedReportRegion:
    def _parts(self, content):
        with TemporaryDirectory(prefix='connlab-linked-read-') as directory:
            source = Path(directory)/'source.docx'; source.write_bytes(content)
            with ProtectedWordPackageGateway().readable_copy(source) as readable, ZipFile(readable) as archive:
                if len(archive.infolist()) > 3000 or sum(info.file_size for info in archive.infolist()) > 100 * 1024 * 1024:
                    raise ValueError('The source report exceeds the bounded region reader limits.')
                if len(set(archive.namelist())) != len(archive.namelist()):
                    raise ValueError('Duplicate source package entries are unsupported.')
                parts = {info.filename: archive.read(info) for info in archive.infolist()}
        if 'word/document.xml' not in parts:
            raise ValueError('Select a readable DOCX report.')
        return parts

    def inspect(self, content):
        root = xml(self._parts(content)['word/document.xml'])
        return [{'index': index, 'kind': etree.QName(block).localname, 'text': text(block)[:1200],
                 'tables': len(block.findall('.//{%s}tbl' % W)) + (block.tag == f'{{{W}}}tbl'),
                 'charts': len(block.findall('.//{%s}chart' % C))}
                for index, block in enumerate(root.find(f'{{{W}}}body')) if block.tag != f'{{{W}}}sectPr']

    def preview(self, content, selection):
        parts = self._parts(content); root = xml(parts['word/document.xml'])
        body = list(root.find(f'{{{W}}}body'))
        start, end = selection['start'], selection['end']
        if start < 0 or start > end or end >= len(body) or end - start > 100:
            raise ValueError('Select an ordered, bounded source report region.')
        blocks = [deepcopy(block) for block in body[start:end + 1]]
        tags = {etree.QName(node).localname for block in blocks for node in block.iter()}
        # These IDs are scoped to the source document, not carried by r:id
        # relationships. Copying them could bind to unrelated target content.
        if tags & {'footnoteReference', 'endnoteReference', 'commentReference', 'commentRangeStart',
                   'commentRangeEnd', 'bookmarkStart', 'bookmarkEnd', 'hyperlink'}:
            raise ValueError('The selected region contains unsupported document-level references; it was not adopted.')
        if tags & {'sectPr', 'numPr', 'object', 'altChunk', 'fldSimple', 'instrText', 'ins', 'del'}:
            raise ValueError('This region has section/numbering/active or revision content requiring manual review; it was not adopted.')
        if not any(block.tag == f'{{{W}}}tbl' or block.findall('.//{%s}tbl' % W) for block in blocks):
            raise ValueError('A temperature region must include its complete measurement table.')
        ids = {value for block in blocks for node in block.iter() for key, value in node.attrib.items() if key.startswith('{'+R+'}')}
        document_rels = xml(parts['word/_rels/document.xml.rels'])
        selected_rels = [deepcopy(rel) for rel in document_rels if rel.get('Id') in ids]
        if len(selected_rels) != len(ids):
            raise ValueError('Selected report relationships are missing.')
        retained, frozen, visiting = {}, [], set()
        def retain(name):
            if name in retained: return
            if name in visiting or name not in parts:
                raise ValueError('An adopted relationship is cyclic or missing.')
            visiting.add(name)
            raw = parts[name]
            tree = xml(raw) if name.endswith('.xml') else None
            relations = xml(parts[rels_name(name)]) if rels_name(name) in parts else None
            if tree is not None and tree.tag == f'{{{C}}}chartSpace' and relations is not None:
                external_ids = {node.get(f'{{{R}}}id') for node in tree.findall('.//{%s}externalData' % C)}
                externally_linked = [rel for rel in relations if rel.get('TargetMode') == 'External']
                if externally_linked:
                    if not selection.get('freeze_external_charts'):
                        raise ValueError('Confirm frozen native chart caches before adopting a curve linked to an external workbook.')
                    if any(rel.get('Id') not in external_ids or not rel.get('Type', '').endswith('/oleObject') for rel in externally_linked):
                        raise ValueError('Unsupported external chart relationship.')
                    freeze_chart(tree); frozen.append(name)
                    for rel in externally_linked: relations.remove(rel)
            if relations is not None:
                for rel in relations:
                    if rel.get('TargetMode') == 'External':
                        raise ValueError('External content cannot be copied into the adopted region.')
                    relation_kind = rel.get('Type', '').rsplit('/', 1)[-1]
                    if relation_kind not in {'image', 'chart', 'chartStyle', 'chartColorStyle', 'package'}:
                        raise ValueError('Unsupported related content in the selected region.')
                    child = relationship_target(name, rel.get('Target', ''))
                    if relation_kind == 'package':
                        # Retained chart workbooks must be passive OOXML with no external links.
                        if not child.endswith('.xlsx'):
                            raise ValueError('Only passive chart workbooks can be adopted.')
                        if child not in parts:
                            raise ValueError('The adopted chart workbook is missing.')
                        with ZipFile(BytesIO(parts[child])) as book:
                            if len(book.infolist()) > 2000 or sum(entry.file_size for entry in book.infolist()) > 100 * 1024 * 1024 or len(set(book.namelist())) != len(book.namelist()):
                                raise ValueError('The adopted chart workbook exceeds safe package limits.')
                            if any('vba' in entry.lower() or 'externalLinks/' in entry for entry in book.namelist()):
                                raise ValueError('The chart workbook contains active or external data.')
                            for entry in book.namelist():
                                if entry.endswith('.rels') and any(r.get('TargetMode') == 'External' for r in xml(book.read(entry))):
                                    raise ValueError('The chart workbook contains external links.')
                    retain(child)
                retained[rels_name(name)] = serialized(relations)
            retained[name] = serialized(tree) if tree is not None else raw
            visiting.remove(name)
        for relation in selected_rels:
            if relation.get('TargetMode') == 'External' or relation.get('Type', '').rsplit('/', 1)[-1] not in {'image', 'chart'}:
                raise ValueError('The selected region contains an unsupported or external object.')
            retain(relationship_target('word/document.xml', relation.get('Target', '')))
        if not any(name.startswith('word/charts/') and name.endswith('.xml') and xml(raw).tag == f'{{{C}}}chartSpace' for name, raw in retained.items() if name.endswith('.xml')):
            raise ValueError('Select the native temperature curve together with its complete table.')
        retained['[Content_Types].xml'] = parts['[Content_Types].xml']
        retained['word/styles.xml'] = parts['word/styles.xml']
        if 'word/theme/theme1.xml' in parts: retained['word/theme/theme1.xml'] = parts['word/theme/theme1.xml']
        if sum(map(len, retained.values())) > 15 * 1024 * 1024:
            raise ValueError('The adopted region is too large.')
        return {'quantity': 'adopted_temperature', 'unit': '°C', 'blocks': [etree.tostring(block).decode() for block in blocks],
            'parts': {name: b64encode(raw).decode() for name, raw in retained.items()},
            'relationships': [dict(rel.attrib) for rel in selected_rels], 'frozen_chart_count': len(frozen),
            'source_region': {'start': start, 'end': end}, 'source_sha256': sha256(content).hexdigest(),
            'excerpt': '\n'.join(text(block) for block in blocks)}

    def append(self, path, data, tag):
        with ZipFile(path) as archive:
            target = {info.filename: archive.read(info) for info in archive.infolist()}
        source = {name: b64decode(raw) for name, raw in data['parts'].items()}
        blocks = [xml(value.encode()) for value in data['blocks']]
        theme = xml(source['word/theme/theme1.xml']) if 'word/theme/theme1.xml' in source else None
        for name, raw in list(source.items()):
            if name.endswith('.xml') and name not in {'[Content_Types].xml', 'word/styles.xml', 'word/theme/theme1.xml'}:
                part = xml(raw); resolve_theme_colors(part, theme); source[name] = serialized(part)
        for block in blocks: resolve_theme_colors(block, theme)
        prefix = 'word/connlab-adopted/' + sha256(tag.encode()).hexdigest()[:16] + '/'
        root = xml(target['word/document.xml']); body = root.find(f'{{{W}}}body')
        existing = root.xpath('//w:sdt[w:sdtPr/w:tag/@w:val=$tag]', namespaces=NS, tag=tag)
        if len(existing) > 1: raise ValueError('Duplicate adopted-region markers.')
        # Replacing this owned region removes only its prior private package namespace.
        if any(name.startswith(prefix) for name in target) and not existing:
            raise ValueError('An adopted package namespace has no matching owned region.')
        target = {name: raw for name, raw in target.items() if not name.startswith(prefix)}
        token = prefix.rsplit('/', 2)[-2]
        styles = xml(target['word/styles.xml'])
        for style in list(styles):
            if style.get(f'{{{W}}}styleId', '').startswith(token + '_'): styles.remove(style)
        target['word/styles.xml'] = serialized(styles)
        self._styles_and_theme(blocks, source, target, token)
        if existing:
            container = existing[0].find(f'{{{W}}}sdtContent')
            for child in list(container): container.remove(child)
        else:
            section = etree.Element(f'{{{W}}}sdt'); props = etree.SubElement(section, f'{{{W}}}sdtPr')
            etree.SubElement(props, f'{{{W}}}tag').set(f'{{{W}}}val', tag)
            container = etree.SubElement(section, f'{{{W}}}sdtContent')
            index = next((i for i, block in enumerate(body) if 'End of Report' in text(block)), len(body) - 1)
            body.insert(max(index, 0), section)
        rels = xml(target['word/_rels/document.xml.rels'])
        for relation in list(rels):
            if relation.get('TargetMode') != 'External' and posixpath.normpath(posixpath.join('word', relation.get('Target', ''))).startswith(prefix):
                rels.remove(relation)
        used = {rel.get('Id') for rel in rels}
        mapping = {}
        for relation in data['relationships']:
            index = 1
            while f'rIdAdopted{index}' in used: index += 1
            identity = f'rIdAdopted{index}'; used.add(identity); mapping[relation['Id']] = identity
            child = relationship_target('word/document.xml', relation['Target'])
            rels.append(etree.Element(f'{{{P}}}Relationship', Id=identity, Type=relation['Type'],
                Target=posixpath.relpath(prefix + child, 'word')))
        document_ids = [int(node.get('id')) for node in root.iter() if etree.QName(node).localname == 'docPr' and node.get('id', '').isdigit()]
        next_id = max(document_ids, default=0) + 1
        for block in blocks:
            for node in block.iter():
                for key, value in list(node.attrib.items()):
                    if key.startswith('{'+R+'}') and value in mapping: node.set(key, mapping[value])
                if etree.QName(node).localname == 'docPr': node.set('id', str(next_id)); next_id += 1
            container.append(block)
        for line in data.get('adoption_notes', []):
            paragraph = etree.SubElement(container, f'{{{W}}}p'); run = etree.SubElement(paragraph, f'{{{W}}}r')
            etree.SubElement(run, f'{{{W}}}t').text = line
        types = xml(target['[Content_Types].xml']); source_types = xml(source['[Content_Types].xml'])
        for entry in list(types):
            if entry.get('PartName', '').lstrip('/').startswith(prefix): types.remove(entry)
        overrides = {entry.get('PartName').lstrip('/'): entry.get('ContentType') for entry in source_types if entry.tag == f'{{{CT}}}Override'}
        defaults = {entry.get('Extension'): entry.get('ContentType') for entry in source_types if entry.tag == f'{{{CT}}}Default'}
        for name, raw in source.items():
            if name in {'[Content_Types].xml', 'word/styles.xml', 'word/theme/theme1.xml'}: continue
            target[prefix + name] = raw
            if name.endswith('.rels'): continue
            content_type = overrides.get(name, defaults.get(name.rsplit('.', 1)[-1]))
            if not content_type: raise ValueError('An adopted package part has no content type.')
            types.append(etree.Element(f'{{{CT}}}Override', PartName='/' + prefix + name, ContentType=content_type))
        target.update({'word/document.xml': serialized(root), 'word/_rels/document.xml.rels': serialized(rels), '[Content_Types].xml': serialized(types)})
        stream = BytesIO()
        with ZipFile(stream, 'w', ZIP_DEFLATED) as output:
            for name, raw in target.items(): output.writestr(name, raw)
        Path(path).write_bytes(stream.getvalue())

    @staticmethod
    def _styles_and_theme(blocks, source, target, token):
        styles = xml(source['word/styles.xml']); target_styles = xml(target['word/styles.xml'])
        indexed = {style.get(f'{{{W}}}styleId'): style for style in styles.findall(f'{{{W}}}style')}
        theme = xml(source['word/theme/theme1.xml']) if 'word/theme/theme1.xml' in source else None
        defaults = styles.find(f'{{{W}}}docDefaults')
        def explicit_fonts(tree):
            for fonts in tree.findall('.//{%s}rFonts' % W):
                for field in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
                    attr = f'{{{W}}}' + field + ('Theme' if field != 'cs' else 'Theme')
                    themed = fonts.get(attr)
                    if not themed: continue
                    branch = 'majorFont' if themed.startswith('major') else 'minorFont'
                    child = 'ea' if field == 'eastAsia' else 'cs' if field == 'cs' else 'latin'
                    entry = theme.find(f'.//{{{A}}}{branch}/{{{A}}}{child}') if theme is not None else None
                    fallback = defaults.find(f'.//{{{W}}}rFonts') if defaults is not None else None
                    value = (entry.get('typeface') if entry is not None else None) or fonts.get(f'{{{W}}}{field}') or (fallback.get(f'{{{W}}}{field}') if fallback is not None else None)
                    if not value: raise ValueError('The selected region depends on an unresolved theme font.')
                    fonts.set(f'{{{W}}}{field}', value); del fonts.attrib[attr]
        copied = set()
        def copy_style(identity):
            if identity in copied: return
            if identity not in indexed: raise ValueError('A selected paragraph depends on an unavailable source style.')
            copied.add(identity); style = deepcopy(indexed[identity]); style.set(f'{{{W}}}styleId', token + '_' + identity)
            if style.find(f'.//{{{W}}}numPr') is not None:
                raise ValueError('A selected style depends on source numbering; explicit mapping is required.')
            style.attrib.pop(f'{{{W}}}default', None)
            if identity == 'Normal' and defaults is not None:
                for name in ('rPr', 'pPr'):
                    inherited = defaults.find(f'{{{W}}}{name}Default/{{{W}}}{name}')
                    if inherited is None: continue
                    own = style.find(f'{{{W}}}{name}')
                    if own is None: own = etree.SubElement(style, f'{{{W}}}{name}')
                    for child in inherited:
                        if own.find(child.tag) is None: own.append(deepcopy(child))
            for name in ('basedOn', 'link', 'next'):
                reference = style.find(f'{{{W}}}{name}')
                if reference is not None:
                    other = reference.get(f'{{{W}}}val'); copy_style(other); reference.set(f'{{{W}}}val', token + '_' + other)
            explicit_fonts(style); resolve_theme_colors(style, theme); target_styles.append(style)
        for block in blocks:
            paragraphs = [block] if block.tag == f'{{{W}}}p' else []
            paragraphs += block.findall('.//{%s}p' % W)
            for paragraph in paragraphs:
                props = paragraph.find(f'{{{W}}}pPr')
                if props is None: props = etree.Element(f'{{{W}}}pPr'); paragraph.insert(0, props)
                if props.find(f'{{{W}}}pStyle') is None:
                    etree.SubElement(props, f'{{{W}}}pStyle').set(f'{{{W}}}val', 'Normal')
            for name in ('pStyle', 'rStyle', 'tblStyle'):
                for reference in block.findall('.//{%s}%s' % (W, name)):
                    identity = reference.get(f'{{{W}}}val'); copy_style(identity); reference.set(f'{{{W}}}val', token + '_' + identity)
            explicit_fonts(block)
        target['word/styles.xml'] = serialized(target_styles)
