"""Drop only orphaned package parts owned by an explicitly replaced Word region."""
import posixpath
from urllib.parse import unquote
from lxml import etree

R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'


def _owner(name):
    if name == '_rels/.rels':
        return ''
    directory, leaf = name.rsplit('/_rels/', 1)
    return directory + '/' + leaf.removesuffix('.rels')


def _target(owner, relationship):
    if relationship.get('TargetMode') == 'External':
        return None
    target = unquote(relationship.get('Target', ''))
    return posixpath.normpath(target.lstrip('/') if target.startswith('/') else posixpath.join(posixpath.dirname(owner), target))


def remove_replaced_region_parts(parts, removed_ids):
    """Retain shared media and all unrelated parts; no global cleanup or filesystem paths."""
    updated = dict(parts)
    name = 'word/_rels/document.xml.rels'
    if name not in parts or not removed_ids:
        return updated
    document = etree.fromstring(parts['word/document.xml'])
    used_ids = {value for item in document.iter() for key, value in item.attrib.items() if key.startswith('{'+R+'}')}
    relationships = etree.fromstring(parts[name])
    candidates, changed = [], False
    for relationship in list(relationships):
        identity = relationship.get('Id')
        if identity in removed_ids and identity not in used_ids:
            candidate = _target('word/document.xml', relationship)
            if candidate:
                candidates.append(candidate)
            relationships.remove(relationship)
            changed = True
    if changed:
        updated[name] = etree.tostring(relationships, xml_declaration=True, encoding='UTF-8', standalone=True)
    deleted = set()
    while candidates:
        candidate = candidates.pop()
        if candidate not in updated or not candidate.startswith(('word/media/', 'word/charts/', 'word/embeddings/')):
            continue
        referenced = False
        for rel_name, content in updated.items():
            if not rel_name.endswith('.rels'):
                continue
            owner = _owner(rel_name)
            if any(_target(owner, item) == candidate for item in etree.fromstring(content)):
                referenced = True
                break
        if referenced:
            continue
        del updated[candidate]
        deleted.add(candidate)
        own_rels = posixpath.join(posixpath.dirname(candidate), '_rels', posixpath.basename(candidate)+'.rels')
        if own_rels in updated:
            candidates.extend(target for item in etree.fromstring(updated.pop(own_rels)) if (target := _target(candidate, item)))
    if deleted and '[Content_Types].xml' in updated:
        content_types = etree.fromstring(updated['[Content_Types].xml'])
        for entry in list(content_types):
            if entry.get('PartName', '').lstrip('/') in deleted:
                content_types.remove(entry)
        updated['[Content_Types].xml'] = etree.tostring(content_types, xml_declaration=True, encoding='UTF-8', standalone=True)
    return updated
