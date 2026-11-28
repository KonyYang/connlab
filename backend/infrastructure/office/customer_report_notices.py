"""Read the conversion gateway's visible, highlighted review list from a finished Word file."""
from zipfile import ZipFile
from lxml import etree
from backend.infrastructure.office.customer_report_document_gateway import _REVIEW_TITLE
from backend.infrastructure.office.office_protected_document_gateway import ProtectedWordPackageGateway


def read_customer_notices(path):
    w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    with ProtectedWordPackageGateway().readable_copy(path) as plain, ZipFile(plain) as archive:
        root = etree.fromstring(archive.read("word/document.xml"), etree.XMLParser(resolve_entities=False, no_network=True))
    paragraphs = root.find(w + "body")
    if not len(paragraphs) or "".join(paragraphs[0].itertext(w + "t")) != _REVIEW_TITLE:
        return []
    notices = []
    for p in list(paragraphs)[1:]:
        if p.tag != w + "p" or p.find(".//" + w + "highlight") is None:
            break
        notices.append("".join(p.itertext(w + "t")))
    return notices
