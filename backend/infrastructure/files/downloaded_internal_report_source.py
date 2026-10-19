"""Read only a matching Internal Report draft in the local OS Downloads folder."""
import ctypes
from hashlib import sha256
import os
from pathlib import Path
import re
from uuid import UUID
from zipfile import BadZipFile

from docx.opc.exceptions import PackageNotFoundError
from lxml.etree import XMLSyntaxError

from backend.application.current_report_update_service import CurrentReportArtifact
from backend.application.customer_report_source_resolver import DownloadedInternalReportUnavailable
from backend.infrastructure.office.word_document_gateway import WordDocumentGateway


def user_downloads_directory() -> Path:
    if os.name != "nt":
        return Path.home() / "Downloads"
    from ctypes import wintypes
    folder_id = (ctypes.c_byte * 16).from_buffer_copy(UUID("374DE290-123F-4565-9164-39C4925E467B").bytes_le)
    pointer = ctypes.c_void_p()
    shell = ctypes.WinDLL("shell32", use_last_error=True)
    shell.SHGetKnownFolderPath.argtypes = [ctypes.c_void_p, wintypes.DWORD, wintypes.HANDLE, ctypes.POINTER(ctypes.c_void_p)]
    shell.SHGetKnownFolderPath.restype = ctypes.c_long
    result = shell.SHGetKnownFolderPath(ctypes.byref(folder_id), 0, None, ctypes.byref(pointer))
    if result != 0:
        raise DownloadedInternalReportUnavailable("Downloads is unavailable. Select an Internal Report file.")
    try:
        return Path(ctypes.wstring_at(pointer))
    finally:
        ole = ctypes.WinDLL("ole32")
        ole.CoTaskMemFree.argtypes = [ctypes.c_void_p]
        ole.CoTaskMemFree(pointer)


def _redirected(path: Path) -> bool:
    return any(item.is_symlink() or (item.exists() and getattr(item.stat(), "st_file_attributes", 0) & 0x400)
               for item in (path, *path.parents))


class DownloadedInternalReportDrafts:
    def __init__(self, root: Path | None = None):
        self._root = root

    def latest(self, dl_number: str) -> CurrentReportArtifact | None:
        try:
            root = self._root if self._root is not None else user_downloads_directory()
            if not root.is_dir():
                return None
            if _redirected(root):
                raise DownloadedInternalReportUnavailable("Downloads redirects to another location. Select an Internal Report file.")
            pattern = re.compile(re.escape(dl_number) + r"\s+.+Report.*[ _-]Draft(?: \((\d+)\))?\.docx$", re.IGNORECASE)
            candidates = []
            for path in root.iterdir():
                match = pattern.fullmatch(path.name)
                if match and path.is_file() and not _redirected(path):
                    candidates.append((path.stat().st_mtime_ns, int(match[1] or 0), path))
            if not candidates:
                return None
            candidates.sort(key=lambda item: (item[0], item[1], item[2].name.casefold()), reverse=True)
            latest = candidates[0]
            path = latest[2]
            fingerprint = sha256(path.read_bytes()).hexdigest()
            for stamp, copy_number, other in candidates[1:]:
                if (stamp, copy_number) != latest[:2]:
                    break
                if sha256(other.read_bytes()).hexdigest() != fingerprint:
                    raise DownloadedInternalReportUnavailable("Several latest drafts match this project. Select an Internal Report file.")
            snapshot = WordDocumentGateway().read_word_document(path)
            header_ids = {value.casefold() for value in re.findall(r"\bDL-[A-Za-z0-9-]+", "\n".join(snapshot.headers))}
            if header_ids != {dl_number.casefold()} or not any(
                re.search(r"(?<![A-Z0-9])E-3707(?![A-Z0-9])", footer, re.IGNORECASE)
                for footer in snapshot.footers
            ):
                raise DownloadedInternalReportUnavailable("The latest draft is not this project's Internal Report. Select the correct file.")
            if _redirected(path) or sha256(path.read_bytes()).hexdigest() != fingerprint:
                raise DownloadedInternalReportUnavailable("The downloaded draft changed while checking it. Try again.")
            return CurrentReportArtifact("ready", "managed_draft", path.name, path, fingerprint, None, folder_path=root)
        except DownloadedInternalReportUnavailable:
            raise
        except (OSError, ValueError, RuntimeError, BadZipFile, PackageNotFoundError, XMLSyntaxError, KeyError) as exc:
            raise DownloadedInternalReportUnavailable("The latest downloaded draft cannot be read. Select an Internal Report file.") from exc
