from __future__ import annotations

import base64
import hashlib
from pathlib import Path

import pytest

from backend.infrastructure.office import OfficeFacade, OfficeFileKind
from backend.infrastructure.office.outlook_msg_gateway import OutlookMsgAttachmentError


def test_outlook_msg_gateway_extracts_fixture_attachments(tmp_path: Path) -> None:
    """TASK_027B extracts supported fixture attachments into intake storage."""
    pdf_bytes = b"%PDF fixture"
    source = tmp_path / "package.msg"
    source.write_text(
        "\n".join(
            [
                "Subject: Request with attachments",
                "From: Jane Engineer <jane@example.com>",
                f"Attachment: request.docx; content=base64:{base64.b64encode(b'docx bytes').decode()}",
                f"Attachment: spec.pdf; content=base64:{base64.b64encode(pdf_bytes).decode()}",
                "Attachment: image003.jpg; content=inline-image",
            ]
        ),
        encoding="utf-8",
    )

    package = OfficeFacade().import_outlook_msg(source, tmp_path / "intake" / "pkg-1")

    assert len(package.attachments) == 3
    assert [attachment.original_name for attachment in package.attachments] == [
        "request.docx",
        "spec.pdf",
        "image003.jpg",
    ]
    assert [attachment.kind for attachment in package.attachments] == [
        OfficeFileKind.DOCX,
        OfficeFileKind.PDF,
        OfficeFileKind.IMAGE,
    ]
    assert all(attachment.stored_path.is_file() for attachment in package.attachments)
    assert all(attachment.stored_path.parent.name == "attachments" for attachment in package.attachments)
    assert package.attachments[1].sha256 == hashlib.sha256(pdf_bytes).hexdigest()
    assert package.attachments[1].size_bytes == len(pdf_bytes)


def test_outlook_msg_gateway_preserves_source_when_attachment_is_malformed(
    tmp_path: Path,
) -> None:
    """Malformed attachment entries fail clearly and keep the copied source."""
    source = tmp_path / "malformed.msg"
    source.write_text(
        "\n".join(
            [
                "Subject: Bad attachment",
                "Attachment: request.docx",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(OutlookMsgAttachmentError) as exc_info:
        OfficeFacade().import_outlook_msg(source, tmp_path / "intake" / "pkg-2")

    assert exc_info.value.stored_path.is_file()
    assert "attachment entry was malformed" in str(exc_info.value)
    assert not (tmp_path / "intake" / "pkg-2" / "attachments").exists()


def test_outlook_msg_gateway_rejects_invalid_attachment_base64(tmp_path: Path) -> None:
    """Invalid attachment base64 fails without deleting the preserved source."""
    source = tmp_path / "invalid-base64.msg"
    source.write_text(
        "\n".join(
            [
                "Subject: Bad base64",
                "Attachment: request.docx; content=base64:not-valid",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(OutlookMsgAttachmentError) as exc_info:
        OfficeFacade().import_outlook_msg(source, tmp_path / "intake" / "pkg-3")

    assert exc_info.value.stored_path.is_file()
    assert "base64 content is invalid" in str(exc_info.value)


def test_outlook_msg_gateway_uses_unique_attachment_file_names(tmp_path: Path) -> None:
    """Duplicate attachment names do not overwrite earlier extracted files."""
    source = tmp_path / "duplicate-attachments.msg"
    source.write_text(
        "\n".join(
            [
                "Subject: Duplicate attachments",
                "Attachment: request.docx; content=first",
                "Attachment: request.docx; content=second",
            ]
        ),
        encoding="utf-8",
    )

    package = OfficeFacade().import_outlook_msg(source, tmp_path / "intake" / "pkg-4")

    assert [attachment.stored_path.name for attachment in package.attachments] == [
        "request.docx",
        "request_2.docx",
    ]
    assert package.attachments[0].stored_path.read_text(encoding="utf-8") == "first"
    assert package.attachments[1].stored_path.read_text(encoding="utf-8") == "second"


def test_outlook_msg_gateway_preserves_embedded_msg_payload(tmp_path: Path) -> None:
    """Real Outlook `.msg` attachments keep their stored payload, not a summary stub."""
    source = Path("tests/fixtures/msg_samples/msg_samplesreal_request_with_msg.msg")

    package = OfficeFacade().import_outlook_msg(source, tmp_path / "intake" / "pkg-5")

    msg_attachments = [attachment for attachment in package.attachments if attachment.extension == "msg"]
    assert len(msg_attachments) == 1
    assert msg_attachments[0].size_bytes > 10_000
    assert msg_attachments[0].stored_path.stat().st_size == msg_attachments[0].size_bytes
