"""DOCX XML cleanup for Application Form header LTR layout."""

from __future__ import annotations

import tempfile
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{W_NS}}}"

_WORD_NAMESPACES = {
    "w": W_NS,
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "wp14": "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "w16se": "http://schemas.microsoft.com/office/word/2015/wordml/symex",
    "w16cid": "http://schemas.microsoft.com/office/word/2016/wordml/cid",
    "w16": "http://schemas.microsoft.com/office/word/2018/wordml",
    "w16cex": "http://schemas.microsoft.com/office/word/2018/wordml/cex",
    "w16sdtdh": "http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash",
    "w16sdtfl": "http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock",
    "w16du": "http://schemas.microsoft.com/office/word/2023/wordml/word16du",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "v": "urn:schemas-microsoft-com:vml",
    "o": "urn:schemas-microsoft-com:office:office",
}

for _prefix, _namespace in _WORD_NAMESPACES.items():
    ET.register_namespace(_prefix, _namespace)


def normalize_header_ltr_layout(path: Path, value: str) -> bool:
    """Force request-form header cells to label, blank, LTR, page layout."""
    changed = False
    with tempfile.NamedTemporaryFile(delete=False, dir=path.parent, suffix=".docx") as temp:
        temp_path = Path(temp.name)
    try:
        with ZipFile(path, "r") as source, ZipFile(temp_path, "w") as target:
            for item in source.infolist():
                content = source.read(item.filename)
                if item.filename.startswith("word/header") and item.filename.endswith(".xml"):
                    updated = _normalize_header_xml(content, value)
                    if updated != content:
                        content = updated
                        changed = True
                target.writestr(item, content)
        if changed:
            temp_path.replace(path)
        else:
            temp_path.unlink(missing_ok=True)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
    return changed


def _normalize_header_xml(content: bytes, value: str) -> bytes:
    root = ET.fromstring(content)
    changed = False
    for cell in root.findall(f".//{W}tc"):
        if "Lab Test Request Number" not in _element_text(cell):
            continue
        if _normalize_cell(cell, value):
            changed = True
    if not changed:
        return content
    return _ensure_ignorable_namespace_declarations(
        ET.tostring(root, encoding="utf-8", xml_declaration=True),
    )


def _normalize_cell(cell: ET.Element, value: str) -> bool:
    paragraphs = [child for child in list(cell) if child.tag == f"{W}p"]
    bounds = _header_bounds(paragraphs)
    if bounds is None:
        return False
    label_index, page_index = bounds
    label = paragraphs[label_index]
    page = paragraphs[page_index]
    blank = _blank_paragraph(paragraphs[label_index + 1 : page_index])
    value_paragraph = _value_paragraph(paragraphs[label_index + 1 : page_index])
    _set_paragraph_text(value_paragraph, value)

    children = list(cell)
    label_child_index = children.index(label)
    page_child_index = children.index(page)
    replacement = [blank, value_paragraph, page]
    for child in children[label_child_index + 1 : page_child_index + 1]:
        cell.remove(child)
    insert_at = label_child_index + 1
    for offset, child in enumerate(replacement):
        cell.insert(insert_at + offset, child)

    for child in list(cell)[insert_at + len(replacement) :]:
        if child.tag == f"{W}p" and not _element_text(child).strip():
            cell.remove(child)
    return True


def _header_bounds(paragraphs: list[ET.Element]) -> tuple[int, int] | None:
    label_index = None
    for index, paragraph in enumerate(paragraphs):
        text = _element_text(paragraph).strip()
        if label_index is None and "Lab Test Request Number" in text:
            label_index = index
            continue
        if label_index is not None and text.startswith("Page"):
            return label_index, index
    return None


def _blank_paragraph(candidates: list[ET.Element]) -> ET.Element:
    for paragraph in candidates:
        if not _element_text(paragraph).strip():
            blank = deepcopy(paragraph)
            _set_paragraph_text(blank, "")
            return blank
    return ET.Element(f"{W}p")


def _value_paragraph(candidates: list[ET.Element]) -> ET.Element:
    for paragraph in candidates:
        if _element_text(paragraph).strip():
            return deepcopy(paragraph)
    return ET.Element(f"{W}p")


def _set_paragraph_text(paragraph: ET.Element, value: str) -> None:
    paragraph_property = paragraph.find(f"{W}pPr")
    paragraph.clear()
    if paragraph_property is not None:
        paragraph.append(deepcopy(paragraph_property))
    run = ET.SubElement(paragraph, f"{W}r")
    text = ET.SubElement(run, f"{W}t")
    text.text = value


def _element_text(element: ET.Element) -> str:
    return "".join(text.text or "" for text in element.findall(f".//{W}t"))


def _ensure_ignorable_namespace_declarations(content: bytes) -> bytes:
    text = content.decode("utf-8")
    marker = "mc:Ignorable=\""
    if marker not in text:
        return content
    prefixes = text.split(marker, 1)[1].split("\"", 1)[0].split()
    missing = [
        prefix
        for prefix in prefixes
        if f"xmlns:{prefix}=" not in text and prefix in _WORD_NAMESPACES
    ]
    if not missing:
        return content
    declarations = "".join(
        f' xmlns:{prefix}="{_WORD_NAMESPACES[prefix]}"' for prefix in missing
    )
    declaration_end = text.find("?>")
    search_from = declaration_end + 2 if declaration_end != -1 else 0
    root_start = text.find("<", search_from)
    root_end = text.find(">", root_start)
    if root_end == -1:
        return content
    return (text[:root_end] + declarations + text[root_end:]).encode("utf-8")
