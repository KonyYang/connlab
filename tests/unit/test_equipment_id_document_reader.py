from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

from docx import Document
import pytest

from backend.infrastructure.office.equipment_id_document_reader import (
    EquipmentIdDocumentReader,
)


def test_reads_paragraphs_and_table_cells_in_order_and_deduplicates(tmp_path: Path) -> None:
    source = tmp_path / "EquipmentID.docx"
    document = Document()
    document.add_paragraph("DG-Q-0033")
    document.add_paragraph("Customer fixture L-0002")
    document.add_paragraph("dg-q-0033")
    table = document.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "DG-Q-0103"
    table.cell(0, 1).text = "Customer fixture L-0002"
    document.save(source)

    result = EquipmentIdDocumentReader().read(source)

    assert result.source_path == source
    assert result.references == (
        "DG-Q-0033",
        "Customer fixture L-0002",
        "DG-Q-0103",
    )


def test_rejects_an_empty_equipment_id_document(tmp_path: Path) -> None:
    source = tmp_path / "EquipmentID.docx"
    Document().save(source)

    try:
        EquipmentIdDocumentReader().read(source)
    except ValueError as exc:
        assert "does not contain equipment references" in str(exc)
    else:
        raise AssertionError("Expected an empty EquipmentID.docx to be rejected")


def test_reads_a_password_protected_equipment_document_through_readable_copy(
    tmp_path: Path,
) -> None:
    protected = tmp_path / "EquipmentID.docx"
    protected.write_bytes(b"encrypted")
    readable = tmp_path / "readable.docx"
    document = Document()
    document.add_paragraph("DG-Q-0033")
    document.save(readable)
    calls: list[Path] = []

    class _PackageGateway:
        @contextmanager
        def readable_copy(self, source: Path):
            calls.append(source)
            yield readable

    result = EquipmentIdDocumentReader(
        protected_package_gateway=_PackageGateway(),
    ).read(protected)

    assert calls == [protected]
    assert result.references == ("DG-Q-0033",)


def test_saves_missing_pasted_selection_as_complete_unique_docx(tmp_path: Path) -> None:
    target = tmp_path / "EquipmentID.docx"
    reader = EquipmentIdDocumentReader()
    reader.save_missing(target, references_text="DG-Q-0033, DG-L-0002\ndg-q-0033；DG-Q-0103")
    assert reader.read(target).references == ("DG-Q-0033", "DG-L-0002", "DG-Q-0103")
    original = target.read_bytes()
    with pytest.raises(FileExistsError):
        reader.save_missing(target, references_text="DG-Q-0999")
    assert target.read_bytes() == original


def test_invalid_upload_does_not_create_selection_file(tmp_path: Path) -> None:
    target = tmp_path / "EquipmentID.docx"
    with pytest.raises(ValueError, match="read"):
        EquipmentIdDocumentReader().save_missing(target, content=b"not a docx")
    assert not target.exists()


def test_published_selection_never_replaces_a_file_created_during_import(tmp_path: Path, monkeypatch) -> None:
    import os
    target = tmp_path / "EquipmentID.docx"
    original_link = os.link
    def raced_link(source, destination):
        target.write_bytes(b"other engineer's selection")
        return original_link(source, destination)
    monkeypatch.setattr(os, "link", raced_link)
    with pytest.raises(FileExistsError):
        EquipmentIdDocumentReader().save_missing(target, references_text="DG-Q-0033")
    assert target.read_bytes() == b"other engineer's selection"
    assert list(tmp_path.iterdir()) == [target]


def test_rejects_redirected_parent_before_creating_any_selection(tmp_path: Path, monkeypatch) -> None:
    from types import SimpleNamespace
    import stat
    original_lstat = Path.lstat
    def redirected(path, *args, **kwargs):
        if path == tmp_path:
            return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT)
        return original_lstat(path, *args, **kwargs)
    monkeypatch.setattr(Path, "lstat", redirected)
    with pytest.raises(OSError, match="redirect"):
        EquipmentIdDocumentReader().save_missing(tmp_path / "EquipmentID.docx", references_text="DG-Q-0033")
    assert list(tmp_path.iterdir()) == []


def test_imports_complete_docx_and_splits_multiple_ids_in_paragraphs(tmp_path: Path) -> None:
    import io
    document = Document()
    document.add_paragraph("DG-Q-0033, DG-L-0002\nDG-Q-0033")
    stream = io.BytesIO()
    document.save(stream)
    target = tmp_path / "EquipmentID.docx"
    result = EquipmentIdDocumentReader().save_missing(target, content=stream.getvalue())
    assert result.references == ("DG-Q-0033", "DG-L-0002")
    assert target.read_bytes() == stream.getvalue()
