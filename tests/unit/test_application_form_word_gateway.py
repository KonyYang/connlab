from __future__ import annotations

from zipfile import ZipFile

from backend.infrastructure.office import application_form_word_gateway as gateway
from backend.infrastructure.office.application_form_header_ltr_xml import (
    normalize_header_ltr_layout,
)


def test_body_value_readback_requires_exact_visible_value() -> None:
    assert gateway._body_value_matches("DL-2026-05-011", "DL-2026-05-011")
    assert not gateway._body_value_matches(
        "Lab Test Request Number: DL-2026-05-011",
        "DL-2026-05-011",
    )


def test_date_field_readback_accepts_word_date_control_display_format() -> None:
    assert gateway._field_value_matches("received_date", "6/20/2026", "20 Jun 2026")
    assert gateway._field_value_matches(
        "estimated_completion_date",
        "6/20/2026",
        "2026-06-20",
    )
    assert not gateway._field_value_matches("sample_condition", "6/20/2026", "20 Jun 2026")


def test_header_value_readback_requires_extracted_exact_value() -> None:
    assert gateway._header_value_matches("DL-2026-05-011", "DL-2026-05-011")
    assert not gateway._header_value_matches(
        "Lab Test Request Number: DL-2026-05-011 Page",
        "DL-2026-05-011",
    )


def test_header_ltr_replaces_existing_ltr_paragraph() -> None:
    cell = _FakeHeaderCell(
        ["Lab Test Request Number:", "DL-OLD", "Page 1 / 2"],
    )

    gateway._replace_header_ltr_value(cell, "DL-2026-05-011")

    assert cell.paragraph_texts() == [
        "Lab Test Request Number:",
        "",
        "DL-2026-05-011",
        "Page 1 / 2",
    ]
    assert gateway._header_ltr_visible_value(cell) == "DL-2026-05-011"


def test_header_ltr_fills_blank_value_paragraph() -> None:
    cell = _FakeHeaderCell(["Lab Test Request Number:", "", "Page 1 / 2"])

    gateway._replace_header_ltr_value(cell, "DL-2026-05-011")

    assert cell.paragraph_texts() == [
        "Lab Test Request Number:",
        "",
        "DL-2026-05-011",
        "Page 1 / 2",
    ]


def test_header_ltr_collapses_blank_then_existing_ltr_to_value_paragraph() -> None:
    cell = _FakeHeaderCell(["Lab Test Request Number:", "", "DL-OLD", "Page 1 / 2"])

    gateway._replace_header_ltr_value(cell, "DL-2026-05-011")

    assert cell.paragraph_texts() == [
        "Lab Test Request Number:",
        "",
        "DL-2026-05-011",
        "Page 1 / 2",
    ]
    assert gateway._header_ltr_visible_value(cell) == "DL-2026-05-011"


def test_header_ltr_removes_blank_paragraphs_after_page() -> None:
    cell = _FakeHeaderCell(
        ["Lab Test Request Number:", "DL-OLD", "Page 1 / 2", "", ""],
    )

    gateway._replace_header_ltr_value(cell, "DL-2026-05-011")

    assert cell.paragraph_texts() == [
        "Lab Test Request Number:",
        "",
        "DL-2026-05-011",
        "Page 1 / 2",
    ]


def test_header_table_ltr_normalizes_when_value_is_already_current() -> None:
    cell = _FakeHeaderCell(
        ["Lab Test Request Number:", "DL-2026-05-011", "", "Page 1 / 2", ""],
    )
    table = _FakeHeaderTable(cell)

    result = gateway._write_header_table_ltr(
        table,
        "DL-2026-05-011",
        "header[1:1].table[1]",
    )

    assert result is not None
    assert result.old_value == "DL-2026-05-011"
    assert result.new_value == "DL-2026-05-011"
    assert cell.paragraph_texts() == [
        "Lab Test Request Number:",
        "",
        "DL-2026-05-011",
        "Page 1 / 2",
    ]


def test_header_ltr_inserts_missing_value_before_page() -> None:
    cell = _FakeHeaderCell(["Lab Test Request Number:", "Page 1 / 2"])

    gateway._replace_header_ltr_value(cell, "DL-2026-05-011")

    assert cell.paragraph_texts() == [
        "Lab Test Request Number:",
        "",
        "DL-2026-05-011",
        "Page 1 / 2",
    ]


def test_header_ltr_blocks_without_page_paragraph() -> None:
    cell = _FakeHeaderCell(["Lab Test Request Number:", "DL-OLD"])

    try:
        gateway._replace_header_ltr_value(cell, "DL-2026-05-011")
    except ValueError as exc:
        assert "safe replacement point" in str(exc)
    else:
        raise AssertionError("Expected unsafe header blocker.")


def test_header_ltr_blocks_ambiguous_intermediate_paragraphs() -> None:
    cell = _FakeHeaderCell(
        ["Lab Test Request Number:", "DL-OLD", "extra text", "Page 1 / 2"],
    )

    try:
        gateway._replace_header_ltr_value(cell, "DL-2026-05-011")
    except ValueError as exc:
        assert "ambiguous" in str(exc)
    else:
        raise AssertionError("Expected ambiguous header blocker.")


def test_header_ltr_xml_normalization_forces_fixed_layout(tmp_path) -> None:
    path = tmp_path / "request.docx"
    header_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:tbl><w:tr><w:tc>"
        "<w:p><w:r><w:t>Lab Test Request Number:</w:t></w:r></w:p>"
        "<w:p/>"
        "<w:p><w:r><w:t>DL-OLD</w:t></w:r></w:p>"
        "<w:p><w:r><w:t>Page 1 / 2</w:t></w:r></w:p>"
        "<w:p/>"
        "</w:tc></w:tr></w:tbl>"
        "</w:hdr>"
    )
    with ZipFile(path, "w") as package:
        package.writestr("word/header1.xml", header_xml)
        package.writestr("word/document.xml", "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\"/>")

    assert normalize_header_ltr_layout(path, "DL-2026-05-011")

    with ZipFile(path) as package:
        content = package.read("word/header1.xml").decode("utf-8")

    import xml.etree.ElementTree as ET
    ET.fromstring(content)
    assert content.count("<w:p") == 4
    assert "Lab Test Request Number:" in content
    assert "DL-2026-05-011" in content
    assert "DL-OLD" not in content


def test_header_ltr_xml_normalization_preserves_word_namespace_prefixes(tmp_path) -> None:
    path = tmp_path / "request.docx"
    header_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:hdr xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
        'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
        'xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'mc:Ignorable="w14 w15 w16se w16cid w16 w16cex w16sdtdh w16sdtfl w16du wp14">'
        '<w:tbl><w:tr><w:tc>'
        "<w:p><w:r><w:t>Lab Test Request Number:</w:t></w:r></w:p>"
        "<w:p><w:r><w:t>DL-OLD</w:t></w:r></w:p>"
        "<w:p><w:r><w:t>Page 1 / 2</w:t></w:r></w:p>"
        "</w:tc></w:tr></w:tbl>"
        "</w:hdr>"
    )
    with ZipFile(path, "w") as package:
        package.writestr("word/header1.xml", header_xml)
        package.writestr("word/document.xml", "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\"/>")

    assert normalize_header_ltr_layout(path, "DL-2026-05-011")

    with ZipFile(path) as package:
        content = package.read("word/header1.xml").decode("utf-8")

    import xml.etree.ElementTree as ET
    ET.fromstring(content)
    assert 'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"' in content
    assert 'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"' in content
    assert 'xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"' in content
    assert 'mc:Ignorable="w14 w15 w16se w16cid w16 w16cex w16sdtdh w16sdtfl w16du wp14"' in content
    for prefix in ("w15", "w16se", "w16cid", "w16", "w16cex", "w16sdtdh", "w16sdtfl", "w16du"):
        assert f"xmlns:{prefix}=" in content
    assert "xmlns:ns" not in content


def test_header_ltr_xml_normalization_repairs_auto_namespace_prefixes(tmp_path) -> None:
    path = tmp_path / "request.docx"
    header_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<w:hdr xmlns:ns1="http://schemas.openxmlformats.org/markup-compatibility/2006" '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'ns1:Ignorable="w14 wp14">'
        '<w:tbl><w:tr><w:tc>'
        "<w:p><w:r><w:t>Lab Test Request Number:</w:t></w:r></w:p>"
        "<w:p/>"
        "<w:p><w:r><w:t>DL-2026-05-011</w:t></w:r></w:p>"
        "<w:p><w:r><w:t>Page 1 / 2</w:t></w:r></w:p>"
        "</w:tc></w:tr></w:tbl>"
        "</w:hdr>"
    )
    with ZipFile(path, "w") as package:
        package.writestr("word/header1.xml", header_xml)
        package.writestr("word/document.xml", "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\"/>")

    assert normalize_header_ltr_layout(path, "DL-2026-05-011")

    with ZipFile(path) as package:
        content = package.read("word/header1.xml").decode("utf-8")

    import xml.etree.ElementTree as ET
    ET.fromstring(content)
    assert 'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"' in content
    assert 'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"' in content
    assert 'xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"' in content
    assert 'mc:Ignorable="w14 wp14"' in content
    assert "xmlns:ns" not in content


def test_label_matching_is_exact_after_normalization() -> None:
    aliases = ("requested testing", "tests to be performed")

    assert gateway.label_matches_aliases("Tests to be Performed:", aliases)
    assert not gateway.label_matches_aliases(
        "Requested Testing Completion Date",
        aliases,
    )


def test_business_unit_location_fallback_is_limited_to_known_six_column_shape() -> None:
    table = _FakeTable(
        [
            ["Business Unit:", "Mobility", "", "Project #:", "DL-1", "Dongguan"],
        ],
    )

    result = gateway._find_location_in_business_unit_table(table, table_index=2)

    assert result is not None
    cell, label, address = result
    assert label == "Business Unit row site"
    assert address == "table[2].cell[1,6]"
    assert gateway._com_clean(cell.Range.Text) == "Dongguan"


def test_business_unit_location_fallback_rejects_unknown_table_shape() -> None:
    table = _FakeTable([["Business Unit:", "Mobility", "Dongguan"]])

    assert gateway._find_location_in_business_unit_table(table, table_index=1) is None


class _FakeCount:
    def __init__(self, count: int) -> None:
        self.Count = count


class _FakeRange:
    def __init__(self, text: str, owner=None) -> None:
        self.Text = f"{text}\r\x07"
        self._owner = owner

    def Delete(self) -> None:
        if self._owner is not None:
            self._owner.delete()

    def InsertBefore(self, text: str) -> None:
        if self._owner is None:
            return
        parts = text.rstrip("\r").split("\r")
        for part in parts:
            self._owner.collection.insert_before(self._owner, part)


class _FakeCell:
    def __init__(self, text: str) -> None:
        self.Range = _FakeRange(text)


class _FakeTable:
    def __init__(self, rows: list[list[str]]) -> None:
        self._rows = rows
        self.Rows = _FakeCount(len(rows))
        self.Columns = _FakeCount(max((len(row) for row in rows), default=0))

    def Cell(self, row: int, column: int) -> _FakeCell:
        return _FakeCell(self._rows[row - 1][column - 1])


class _FakeParagraph:
    def __init__(self, collection: "_FakeParagraphCollection", text: str) -> None:
        self.collection = collection
        self.Range = _FakeRange(text, self)

    def delete(self) -> None:
        self.collection.delete(self)


class _FakeParagraphCollection:
    def __init__(self, texts: list[str]) -> None:
        self._items = [_FakeParagraph(self, text) for text in texts]

    @property
    def Count(self) -> int:
        return len(self._items)

    def Item(self, index: int) -> _FakeParagraph:
        return self._items[index - 1]

    def delete(self, paragraph: _FakeParagraph) -> None:
        self._items.remove(paragraph)

    def insert_before(self, paragraph: _FakeParagraph, text: str) -> None:
        index = self._items.index(paragraph)
        self._items.insert(index, _FakeParagraph(self, text))

    def texts(self) -> list[str]:
        return [gateway._com_clean(item.Range.Text) for item in self._items]


class _FakeHeaderRange:
    def __init__(self, texts: list[str]) -> None:
        self.Paragraphs = _FakeParagraphCollection(texts)

    @property
    def Text(self) -> str:
        return "\r".join(self.Paragraphs.texts())


class _FakeHeaderCell:
    def __init__(self, texts: list[str]) -> None:
        self.Range = _FakeHeaderRange(texts)

    def paragraph_texts(self) -> list[str]:
        return self.Range.Paragraphs.texts()


class _FakeHeaderTable:
    def __init__(self, header_cell: _FakeHeaderCell) -> None:
        self._header_cell = header_cell
        self.Rows = _FakeCount(1)
        self.Columns = _FakeCount(3)

    def Cell(self, row: int, column: int):
        if row == 1 and column == 3:
            return self._header_cell
        return _FakeCell("")
