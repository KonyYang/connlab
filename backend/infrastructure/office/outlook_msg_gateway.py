"""Outlook `.msg` gateway for source import and minimal metadata."""

from __future__ import annotations

import re
import shutil
import base64
import hashlib
import mimetypes
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import olefile

from backend.infrastructure.office.models import (
    ImportedMailAttachment,
    ImportedMailPackage,
    OfficeFileKind,
)


class OutlookMsgImportError(RuntimeError):
    """Raised when an Outlook `.msg` source cannot be imported safely."""


class OutlookMsgMetadataError(OutlookMsgImportError):
    """Raised when metadata cannot be read after the source is preserved."""

    def __init__(self, message: str, *, stored_path: Path) -> None:
        """Create a metadata error that exposes the preserved source path."""
        super().__init__(message)
        self.stored_path = stored_path


class OutlookMsgAttachmentError(OutlookMsgImportError):
    """Raised when attachments cannot be extracted after the source is preserved."""

    def __init__(self, message: str, *, stored_path: Path) -> None:
        """Create an attachment error that exposes the preserved source path."""
        super().__init__(message)
        self.stored_path = stored_path


@dataclass(frozen=True, slots=True)
class _ParsedMsgMetadata:
    """Best-effort minimal metadata extracted from a `.msg` source."""

    subject: str | None
    sender_name: str | None
    sender_email: str | None
    recipients: list[str]
    cc: list[str]
    sent_at: datetime | None
    body_text: str | None


@dataclass(frozen=True, slots=True)
class _ParsedAttachment:
    """Attachment extracted from a supported fixture representation."""

    original_name: str
    content: bytes


class OutlookMsgGateway:
    """Boundary for reading Outlook `.msg` files without automating Outlook."""

    def import_outlook_msg(self, source_path: Path, target_dir: Path) -> ImportedMailPackage:
        """Copy a `.msg` source and read minimal metadata when possible."""
        source = Path(source_path)
        if source.suffix.lower() != ".msg":
            raise OutlookMsgImportError(f"Only .msg files can be imported: {source}")
        if not source.is_file():
            raise FileNotFoundError(f"Outlook .msg source does not exist: {source}")

        stored_path = _copy_source_file(source, Path(target_dir))
        metadata = _parse_ole_metadata(stored_path) or _parse_minimal_metadata(stored_path)
        if not _has_minimal_metadata(metadata):
            raise OutlookMsgMetadataError(
                "Outlook .msg source was preserved, but minimal metadata could not be read. "
                "Use a real Outlook .msg file or add a dedicated parser in TASK_027C.",
                stored_path=stored_path,
            )

        return ImportedMailPackage(
            source_original_name=source.name,
            source_stored_path=stored_path,
            subject=metadata.subject,
            sender_name=metadata.sender_name,
            sender_email=metadata.sender_email,
            recipients=metadata.recipients,
            cc=metadata.cc,
            sent_at=metadata.sent_at,
            body_text=metadata.body_text,
            attachments=_extract_ole_attachments(stored_path, Path(target_dir))
            or _extract_attachments(stored_path, Path(target_dir)),
        )


def _copy_source_file(source_path: Path, target_dir: Path) -> Path:
    """Copy the source `.msg` file into the controlled source directory."""
    source_dir = target_dir / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    destination = _unique_destination(source_dir, _safe_filename(source_path.name))
    shutil.copy2(source_path, destination)
    return destination


def _unique_destination(directory: Path, filename: str) -> Path:
    """Return a non-overwriting destination path in a directory."""
    candidate = directory / filename
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    index = 2
    while True:
        next_candidate = directory / f"{stem}_{index}{suffix}"
        if not next_candidate.exists():
            return next_candidate
        index += 1


def _safe_filename(filename: str) -> str:
    """Return a Windows-safe file name without path separators."""
    cleaned = Path(filename).name.replace("/", "_").replace("\\", "_")
    cleaned = re.sub(r"[^A-Za-z0-9._ -]+", "_", cleaned).strip(" .")
    return cleaned or "source.msg"


def _parse_minimal_metadata(path: Path) -> _ParsedMsgMetadata:
    """Read minimal mail metadata from a preserved `.msg` source."""
    text = _decode_best_effort(path.read_bytes())
    headers, body = _split_headers_and_body(text)
    sender_name, sender_email = _parse_sender(headers.get("from"))
    return _ParsedMsgMetadata(
        subject=headers.get("subject"),
        sender_name=sender_name,
        sender_email=sender_email,
        recipients=_split_recipients(headers.get("to")),
        cc=_split_recipients(headers.get("cc")),
        sent_at=_parse_datetime(headers.get("sent") or headers.get("date")),
        body_text=body or headers.get("body"),
    )


def _parse_ole_metadata(path: Path) -> _ParsedMsgMetadata | None:
    """Read root-level Outlook MAPI metadata from an OLE `.msg` file."""
    if not olefile.isOleFile(str(path)):
        return None
    with olefile.OleFileIO(str(path)) as ole:
        sender_name, sender_email = _parse_sender(
            _read_msg_text_property(ole, "0C1A")
            or _read_msg_text_property(ole, "0C1F")
        )
        explicit_sender_email = _read_msg_text_property(ole, "0C1F")
        return _ParsedMsgMetadata(
            subject=_read_msg_text_property(ole, "0037"),
            sender_name=sender_name,
            sender_email=explicit_sender_email or sender_email,
            recipients=_split_recipients(_read_msg_text_property(ole, "0E04")),
            cc=_split_recipients(_read_msg_text_property(ole, "0E03")),
            sent_at=None,
            body_text=_read_msg_text_property(ole, "1000"),
        )


def _extract_attachments(path: Path, target_dir: Path) -> list[ImportedMailAttachment]:
    """Extract attachments from supported fixture-style `.msg` content."""
    text = _decode_best_effort(path.read_bytes())
    parsed_attachments = _parse_fixture_attachments(text, stored_path=path)
    attachment_dir = target_dir / "attachments"
    attachments: list[ImportedMailAttachment] = []
    for parsed in parsed_attachments:
        attachment_dir.mkdir(parents=True, exist_ok=True)
        stored_path = _unique_destination(attachment_dir, _safe_filename(parsed.original_name))
        stored_path.write_bytes(parsed.content)
        extension = stored_path.suffix.lower().lstrip(".")
        kind = _kind_from_extension(extension)
        attachments.append(
            ImportedMailAttachment(
                original_name=parsed.original_name,
                stored_path=stored_path,
                extension=extension,
                kind=kind,
                mime_type=mimetypes.guess_type(stored_path.name)[0]
                or _fallback_mime_type(kind),
                size_bytes=stored_path.stat().st_size,
                sha256=hashlib.sha256(parsed.content).hexdigest(),
            )
        )
    return attachments


def _extract_ole_attachments(path: Path, target_dir: Path) -> list[ImportedMailAttachment]:
    """Extract file attachments from an OLE Outlook `.msg` file."""
    if not olefile.isOleFile(str(path)):
        return []
    with olefile.OleFileIO(str(path)) as ole:
        attachments: list[ImportedMailAttachment] = []
        for storage in _attachment_storages(ole):
            file_name = (
                _read_msg_text_property(ole, "3707", storage)
                or _read_msg_text_property(ole, "3704", storage)
                or _read_msg_text_property(ole, "3001", storage)
            )
            data = _read_msg_binary_property(ole, "3701", storage)
            if not file_name or data is None:
                continue
            attachments.append(
                _write_attachment(
                    target_dir=target_dir,
                    original_name=file_name,
                    content=data,
                    content_id=_read_msg_text_property(ole, "3712", storage),
                    mime_type_hint=_read_msg_text_property(ole, "370E", storage),
                )
            )
        return attachments


def _attachment_storages(ole: olefile.OleFileIO) -> list[tuple[str, ...]]:
    """Return unique top-level attachment storage paths."""
    storages: set[tuple[str, ...]] = set()
    for stream in ole.listdir(streams=True, storages=False):
        for index, part in enumerate(stream):
            if part.startswith("__attach_version1.0_"):
                storages.add(tuple(stream[: index + 1]))
                break
    return sorted(storages)


def _write_attachment(
    *,
    target_dir: Path,
    original_name: str,
    content: bytes,
    content_id: str | None = None,
    mime_type_hint: str | None = None,
) -> ImportedMailAttachment:
    """Write one attachment into the controlled attachment directory."""
    attachment_dir = target_dir / "attachments"
    attachment_dir.mkdir(parents=True, exist_ok=True)
    stored_path = _unique_destination(attachment_dir, _safe_filename(original_name))
    stored_path.write_bytes(content)
    extension = stored_path.suffix.lower().lstrip(".")
    kind = _kind_from_extension(extension)
    return ImportedMailAttachment(
        original_name=original_name,
        stored_path=stored_path,
        extension=extension,
        kind=kind,
        mime_type=mime_type_hint or mimetypes.guess_type(stored_path.name)[0]
        or _fallback_mime_type(kind),
        size_bytes=stored_path.stat().st_size,
        sha256=hashlib.sha256(content).hexdigest(),
        content_id=content_id,
    )


def _parse_fixture_attachments(text: str, *, stored_path: Path) -> list[_ParsedAttachment]:
    """Parse deterministic attachment fixtures from decoded text."""
    attachments: list[_ParsedAttachment] = []
    for line in text.replace("\r\n", "\n").split("\n"):
        cleaned = line.strip("\x00 ").strip()
        if not cleaned.lower().startswith("attachment:"):
            continue
        match = re.match(r"^attachment:\s*(?P<name>[^;]+?)(?:\s*;\s*content=(?P<content>.*))?$", cleaned, re.I)
        if not match or match.group("content") is None:
            raise OutlookMsgAttachmentError(
                "Outlook .msg source was preserved, but an attachment entry was malformed.",
                stored_path=stored_path,
            )
        name = match.group("name").strip()
        content = _decode_attachment_content(match.group("content"), stored_path=stored_path)
        attachments.append(_ParsedAttachment(original_name=name, content=content))
    return attachments


def _decode_attachment_content(value: str, *, stored_path: Path) -> bytes:
    """Decode a fixture attachment body from plain text or base64."""
    content = value.strip()
    if content.lower().startswith("base64:"):
        try:
            return base64.b64decode(content.split(":", 1)[1], validate=True)
        except ValueError as exc:
            raise OutlookMsgAttachmentError(
                "Outlook .msg source was preserved, but attachment base64 content is invalid.",
                stored_path=stored_path,
            ) from exc
    return content.encode("utf-8")


def _decode_best_effort(data: bytes) -> str:
    """Decode text from synthetic or simple `.msg` samples without Outlook."""
    for encoding in ("utf-8-sig", "utf-16-le", "latin-1"):
        try:
            decoded = data.decode(encoding, errors="strict")
        except (LookupError, UnicodeDecodeError):
            continue
        if _looks_like_mail_fixture(decoded):
            return decoded
    return data.decode("latin-1", errors="ignore")


def _looks_like_mail_fixture(value: str) -> bool:
    """Return true when decoded text contains simple mail fixture fields."""
    return bool(re.search(r"^(subject|from|to|cc|sent|date|body|attachment)\s*:", value, re.I | re.M))


def _read_msg_text_property(
    ole: olefile.OleFileIO,
    property_id: str,
    storage: tuple[str, ...] = (),
) -> str | None:
    """Read a Unicode or ANSI MAPI text property from an OLE stream."""
    for suffix, encoding in (("001F", "utf-16-le"), ("001E", "latin-1")):
        value = _read_stream(ole, (*storage, f"__substg1.0_{property_id}{suffix}"))
        if value is None:
            continue
        decoded = value.decode(encoding, errors="ignore").replace("\x00", "").strip()
        if decoded:
            return decoded
    return None


def _read_msg_binary_property(
    ole: olefile.OleFileIO,
    property_id: str,
    storage: tuple[str, ...],
) -> bytes | None:
    """Read a binary MAPI property from an OLE stream."""
    return _read_stream(ole, (*storage, f"__substg1.0_{property_id}0102"))


def _read_stream(ole: olefile.OleFileIO, stream_path: tuple[str, ...]) -> bytes | None:
    """Read an OLE stream if it exists."""
    if not ole.exists(stream_path):
        return None
    with ole.openstream(stream_path) as stream:
        return stream.read()


def _kind_from_extension(extension: str) -> OfficeFileKind:
    """Map an attachment extension to a coarse Office file kind."""
    if extension == "docx":
        return OfficeFileKind.DOCX
    if extension == "doc":
        return OfficeFileKind.DOC
    if extension == "xlsx":
        return OfficeFileKind.XLSX
    if extension == "xls":
        return OfficeFileKind.XLS
    if extension == "pdf":
        return OfficeFileKind.PDF
    if extension in {"jpg", "jpeg", "png", "gif", "bmp", "tif", "tiff"}:
        return OfficeFileKind.IMAGE
    if extension == "msg":
        return OfficeFileKind.OUTLOOK_MSG
    return OfficeFileKind.UNKNOWN


def _fallback_mime_type(kind: OfficeFileKind) -> str:
    """Return a stable fallback MIME type for a file kind."""
    fallback = {
        OfficeFileKind.DOCX: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        OfficeFileKind.DOC: "application/msword",
        OfficeFileKind.XLSX: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        OfficeFileKind.XLS: "application/vnd.ms-excel",
        OfficeFileKind.PDF: "application/pdf",
        OfficeFileKind.IMAGE: "image/*",
        OfficeFileKind.OUTLOOK_MSG: "application/vnd.ms-outlook",
        OfficeFileKind.UNKNOWN: "application/octet-stream",
    }
    return fallback[kind]


def _split_headers_and_body(text: str) -> tuple[dict[str, str], str | None]:
    """Extract simple RFC-like headers and body text from decoded content."""
    headers: dict[str, str] = {}
    lines = [line.strip("\x00 ") for line in text.replace("\r\n", "\n").split("\n")]
    body_lines: list[str] = []
    body_started = False
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            if headers:
                body_started = True
            continue
        if body_started:
            body_lines.append(cleaned)
            continue
        match = re.match(r"^(subject|from|to|cc|sent|date|body)\s*:\s*(.+)$", cleaned, re.I)
        if match:
            key = match.group(1).lower()
            value = match.group(2).strip()
            headers.setdefault(key, value)
            if key == "body":
                body_started = True
                body_lines.append(value)
            continue
    body = "\n".join(body_lines).strip() or None
    return headers, body


def _parse_sender(value: str | None) -> tuple[str | None, str | None]:
    """Parse a simple sender display name and email address."""
    if not value:
        return None, None
    match = re.match(r"^(?P<name>.*?)\s*<(?P<email>[^>]+)>$", value)
    if match:
        return match.group("name").strip() or None, match.group("email").strip()
    if "@" in value:
        return None, value.strip()
    return value.strip(), None


def _split_recipients(value: str | None) -> list[str]:
    """Split recipients separated by semicolons or commas."""
    if not value:
        return []
    return [item.strip() for item in re.split(r"[;,]", value) if item.strip()]


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse an ISO-like mail datetime when present."""
    if not value:
        return None
    normalized = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _has_minimal_metadata(metadata: _ParsedMsgMetadata) -> bool:
    """Return true when at least one meaningful mail field was read."""
    return any(
        [
            metadata.subject,
            metadata.sender_name,
            metadata.sender_email,
            metadata.recipients,
            metadata.cc,
            metadata.sent_at,
            metadata.body_text,
        ]
    )
