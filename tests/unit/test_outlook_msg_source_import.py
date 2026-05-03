from __future__ import annotations

from pathlib import Path

import pytest

from backend.infrastructure.office import OfficeFacade, OutlookMsgImportError
from backend.infrastructure.office.outlook_msg_gateway import (
    OutlookMsgMetadataError,
    _parse_datetime,
    _preferred_sender_email,
)


def test_outlook_msg_gateway_copies_source_and_reads_minimal_metadata(
    tmp_path: Path,
) -> None:
    """TASK_027A imports a `.msg` source and reads minimal mail metadata."""
    source = tmp_path / "Customer Request.msg"
    source.write_text(
        "\n".join(
            [
                "Subject: Connector qualification request",
                "From: Jane Engineer <jane@example.com>",
                "To: lab@example.com; qa@example.com",
                "Cc: manager@example.com",
                "Sent: 2026-04-27T09:30:00",
                "Body: Please review the attached request package.",
                "",
                "The application form will be selected by the operator.",
            ]
        ),
        encoding="utf-8",
    )

    package = OfficeFacade().import_outlook_msg(source, tmp_path / "intake" / "pkg-1")

    assert package.source_original_name == "Customer Request.msg"
    assert package.source_stored_path.is_file()
    assert package.source_stored_path.parent.name == "source"
    assert package.subject == "Connector qualification request"
    assert package.sender_name == "Jane Engineer"
    assert package.sender_email == "jane@example.com"
    assert package.recipients == ["lab@example.com", "qa@example.com"]
    assert package.cc == ["manager@example.com"]
    assert package.sent_at is not None
    assert "attached request package" in (package.body_text or "")
    assert package.attachments == []


def test_outlook_msg_gateway_preserves_source_when_metadata_parse_fails(
    tmp_path: Path,
) -> None:
    """Metadata failures keep the copied source and return an actionable error."""
    source = tmp_path / "opaque.msg"
    source.write_bytes(b"\x00\x01\x02\x03not enough metadata")

    with pytest.raises(OutlookMsgMetadataError) as exc_info:
        OfficeFacade().import_outlook_msg(source, tmp_path / "intake" / "pkg-2")

    assert exc_info.value.stored_path.is_file()
    assert exc_info.value.stored_path.read_bytes() == source.read_bytes()
    assert "minimal metadata could not be read" in str(exc_info.value)


def test_outlook_msg_gateway_rejects_non_msg_sources(tmp_path: Path) -> None:
    """Only `.msg` sources are accepted by the Outlook gateway."""
    source = tmp_path / "request.txt"
    source.write_text("Subject: not a msg", encoding="utf-8")

    with pytest.raises(OutlookMsgImportError):
        OfficeFacade().import_outlook_msg(source, tmp_path / "intake" / "pkg-3")

    assert not (tmp_path / "intake" / "pkg-3" / "source").exists()


def test_outlook_msg_gateway_does_not_overwrite_existing_sources(tmp_path: Path) -> None:
    """Repeated imports preserve both source files under unique names."""
    source = tmp_path / "duplicate.msg"
    source.write_text("Subject: First", encoding="utf-8")
    target = tmp_path / "intake" / "pkg-4"

    first = OfficeFacade().import_outlook_msg(source, target)
    source.write_text("Subject: Second", encoding="utf-8")
    second = OfficeFacade().import_outlook_msg(source, target)

    assert first.source_stored_path.name == "duplicate.msg"
    assert second.source_stored_path.name == "duplicate_2.msg"
    assert first.source_stored_path.read_text(encoding="utf-8") == "Subject: First"
    assert second.source_stored_path.read_text(encoding="utf-8") == "Subject: Second"


def test_exchange_sender_prefers_smtp_over_x500_address() -> None:
    """Exchange X.500 sender paths must not be shown as the From email."""
    sender = _preferred_sender_email(
        "Neo.Xu@fci.com",
        "/O=FRAGROUP/OU=EXCHANGE ADMINISTRATIVE GROUP/CN=RECIPIENTS/CN=QIU, PETER78F",
    )

    assert sender == "Neo.Xu@fci.com"


def test_outlook_rfc_date_header_is_parsed() -> None:
    """Real Outlook transport headers often use RFC-style date strings."""
    parsed = _parse_datetime("Fri, 11 Oct 2024 16:38:00 +0800")

    assert parsed is not None
    assert parsed.isoformat() == "2024-10-11T16:38:00+08:00"
