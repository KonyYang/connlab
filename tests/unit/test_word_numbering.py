from __future__ import annotations

from dataclasses import dataclass

from lxml import etree

from backend.infrastructure.office.word_numbering import paragraph_texts_with_numbering


def test_paragraph_texts_with_numbering_materializes_decimal_headings() -> None:
    document = _FakeDocument(
        paragraphs=[
            _paragraph("Requirements", num_id=3, ilvl=0),
            _paragraph("Qualification", num_id=3, ilvl=1),
            _paragraph("Material", num_id=3, ilvl=1),
            _paragraph("Finish", num_id=3, ilvl=1),
            _paragraph("Design and Construction", num_id=3, ilvl=1),
            _paragraph("Examination", num_id=3, ilvl=1),
            _paragraph("Visual inspection according to EIA-364-18."),
        ],
        numbering_xml=_numbering_xml(),
    )

    paragraphs = paragraph_texts_with_numbering(document)

    assert paragraphs[0] == "5.0 Requirements"
    assert paragraphs[1] == "5.1 Qualification"
    assert paragraphs[4] == "5.4 Design and Construction"
    assert paragraphs[5] == "5.5 Examination"
    assert paragraphs[6] == "Visual inspection according to EIA-364-18."


def test_paragraph_texts_with_numbering_ignores_missing_numbering_part() -> None:
    document = _FakeDocumentWithoutNumbering(
        paragraphs=[
            _paragraph("Matrix section", num_id=1, ilvl=0),
            _paragraph("Visual inspection"),
        ],
    )

    paragraphs = paragraph_texts_with_numbering(document)

    assert paragraphs == ["Matrix section", "Visual inspection"]


@dataclass
class _FakeDocument:
    paragraphs: list[object]
    numbering_xml: str

    def __post_init__(self) -> None:
        self.part = _Part(self.numbering_xml)


class _Part:
    def __init__(self, numbering_xml: str) -> None:
        self.numbering_part = _NumberingPart(numbering_xml)


@dataclass
class _FakeDocumentWithoutNumbering:
    paragraphs: list[object]

    def __post_init__(self) -> None:
        self.part = _PartWithoutNumbering()


class _PartWithoutNumbering:
    @property
    def numbering_part(self) -> object:
        raise NotImplementedError


class _NumberingPart:
    def __init__(self, numbering_xml: str) -> None:
        self.element = etree.fromstring(numbering_xml)


class _Value:
    def __init__(self, value: int) -> None:
        self.val = value


class _NumPr:
    def __init__(self, num_id: int, ilvl: int) -> None:
        self.numId = _Value(num_id)
        self.ilvl = _Value(ilvl)


class _PPr:
    def __init__(self, num_id: int, ilvl: int) -> None:
        self.numPr = _NumPr(num_id, ilvl)


class _P:
    def __init__(self, num_id: int | None, ilvl: int | None) -> None:
        self.pPr = _PPr(num_id, ilvl) if num_id is not None and ilvl is not None else None


class _Paragraph:
    def __init__(self, text: str, num_id: int | None = None, ilvl: int | None = None) -> None:
        self.text = text
        self._p = _P(num_id, ilvl)


def _paragraph(text: str, *, num_id: int | None = None, ilvl: int | None = None) -> _Paragraph:
    return _Paragraph(text, num_id, ilvl)


def _numbering_xml() -> str:
    return """\
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:abstractNum w:abstractNumId="6">
    <w:lvl w:ilvl="0">
      <w:start w:val="5"/>
      <w:numFmt w:val="decimal"/>
      <w:lvlText w:val="%1.0"/>
    </w:lvl>
    <w:lvl w:ilvl="1">
      <w:start w:val="1"/>
      <w:numFmt w:val="decimal"/>
      <w:lvlText w:val="%1.%2"/>
    </w:lvl>
  </w:abstractNum>
  <w:num w:numId="3">
    <w:abstractNumId w:val="6"/>
  </w:num>
</w:numbering>
"""
