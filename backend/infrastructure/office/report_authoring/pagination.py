"""Bounded paragraph/row pagination protection, not a document-wide formatter."""
import re
from lxml import etree
from backend.infrastructure.office.report_authoring.word_copy import NS, text


def _node(name):
    return etree.Element(f'{{{NS["w"]}}}{name}')


def protect_table_starts(root, *, customer=False):
    """Only identified table openings change; explicit page breaks and later rows remain."""
    tables, groups = set(), []
    for paragraph in root.xpath('//w:body//w:p', namespaces=NS):
        label = ' '.join(text(paragraph).split())
        is_group = bool(re.fullmatch(r'Group\s+.+?\s+Test Results', label, re.I))
        if not is_group and not (customer and re.match(r'Temperature (?:Rise Measurements|rise — Group)', label, re.I)):
            continue
        following, blanks = paragraph.getnext(), []
        while following is not None and following.tag == _node('p').tag and not text(following).strip() and not following.xpath('.//w:drawing|.//w:pict', namespaces=NS):
            blanks.append(following); following = following.getnext()
        if following is not None and following.tag == _node('tbl').tag and _known_table(following, customer=customer):
            tables.add(following)
            for item in [paragraph, *blanks]:
                _pagination_flag(item, 'pPr', 'keepNext', True)
            if is_group:
                groups.append(label)
    if customer:
        tables.update(table for table in root.xpath('//w:body//w:tbl', namespaces=NS) if _known_table(table, customer=True))
    for table in tables:
        rows = table.findall('w:tr', NS)
        _pagination_flag(rows[0], 'trPr', 'tblHeader', True)
        for row in rows[:2]:
            _pagination_flag(row, 'trPr', 'cantSplit', True)
        for paragraph in rows[0].xpath('./w:tc/w:p', namespaces=NS):
            _pagination_flag(paragraph, 'pPr', 'keepNext', True)
        # Do not chain the whole table or override any later data-row rule.
        for paragraph in rows[1].xpath('./w:tc/w:p', namespaces=NS):
            _pagination_flag(paragraph, 'pPr', 'keepNext', False)
    return groups


def _known_table(table, *, customer):
    rows = table.findall('w:tr', NS)
    if len(rows) < 2:
        return False
    headers = {' '.join(text(cell).split()).casefold() for cell in rows[0].findall('w:tc', NS)}
    return ({'result', 'comment'} <= headers or (customer and (
        {'test method', 'requirement'} <= headers or {'description', 'part #'} <= headers
        or rows[0].find('w:trPr/w:tblHeader', NS) is not None)))


def _pagination_flag(element, container_name, name, enabled):
    container = element.find('w:'+container_name, NS)
    if container is None:
        container = _node(container_name); element.insert(0, container)
    flag = container.find('w:'+name, NS)
    if flag is None:
        flag = _node(name)
        if container_name == 'pPr':
            index = 1 if len(container) and container[0].tag == _node('pStyle').tag else 0
        elif name == 'cantSplit':
            before = {'trHeight', 'tblHeader', 'tblCellSpacing', 'jc', 'hidden'}
            index = next((i for i, child in enumerate(container) if etree.QName(child).localname in before), len(container))
        else:
            before = {'tblCellSpacing', 'jc', 'hidden'}
            index = next((i for i, child in enumerate(container) if etree.QName(child).localname in before), len(container))
        container.insert(index, flag)
    flag.set(f'{{{NS["w"]}}}val', '1' if enabled else '0')
