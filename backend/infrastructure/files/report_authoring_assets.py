"""Immutable application-owned evidence copies; never accept a client filesystem path."""
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import re
from zipfile import ZipFile, BadZipFile
from docx import Document
from contextlib import contextmanager
from lxml import etree
import tempfile
from backend.infrastructure.office.office_protected_document_gateway import ProtectedWordPackageGateway, OfficeProtectedDocumentError


class ReportAuthoringAssets:
    def __init__(self, root: Path):
        self.root = root

    def path(self, project_id, source):
        return self.root / sha256(project_id.encode()).hexdigest() / (source.sha256 + Path(source.file_name).suffix.lower())

    def read(self, project_id, source):
        path = self.path(project_id, source)
        self._check_path(path)
        content = path.read_bytes()
        if len(content) != source.size_bytes or sha256(content).hexdigest() != source.sha256:
            raise ValueError("The retained evidence copy changed. Upload and review a new source.")
        return content

    def retain(self, project_id, source, content):
        path = self.path(project_id, source)
        self._check_path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._check_path(path)
        try:
            with path.open("xb") as stream:
                stream.write(content)
        except FileExistsError:
            self.read(project_id, source)
        return path

    @staticmethod
    def _check_path(path):
        for item in (path, *path.parents):
            if item.is_symlink() or (item.exists() and getattr(item.stat(), "st_file_attributes", 0) & 0x400):
                raise ValueError("Report storage contains a redirected path. Use local application storage.")


@contextmanager
def readable_word_bytes(content):
    with tempfile.TemporaryDirectory(prefix="connlab-report-evidence-") as directory:
        source = Path(directory) / "source.docx"
        source.write_bytes(content)
        try:
            with ProtectedWordPackageGateway().readable_copy(source) as readable:
                yield readable.read_bytes()
        except OfficeProtectedDocumentError as exc:
            raise ValueError("The protected report cannot be opened with the configured report password.") from exc


def inspect_upload(file_name: str, content: bytes, role: str, project_dl: str) -> str:
    if not file_name or len(file_name) > 255 or any(char in file_name for char in '\\/:\x00') or file_name in {".", ".."}:
        raise ValueError("Choose a file with a plain filename.")
    if not content or len(content) > 50 * 1024 * 1024:
        raise ValueError("Choose a non-empty source smaller than 50 MB.")
    suffix = Path(file_name).suffix.lower()
    allowed = {".docx", ".xlsx", ".csv", ".pdf", ".png", ".jpg", ".jpeg", ".txt"}
    if suffix not in allowed:
        raise ValueError("Use DOCX, XLSX, CSV, PDF, PNG, JPEG or text evidence.")
    if role == 'photo' and suffix not in {'.png', '.jpg', '.jpeg'}:
        raise ValueError('Retain a PNG or JPEG file for photo-slot replacement.')
    if role in {'temperature', 'cr', 'mechanical'} and suffix not in {'.xlsx', '.csv'}:
        raise ValueError('Use XLSX or CSV measurement sources. Retain other formats as supporting evidence.')
    if suffix == ".docx":
        with readable_word_bytes(content) as readable:
            return _inspect_office(readable, suffix, role, project_dl)
    if suffix == ".xlsx":
        _inspect_office(content, suffix, role, project_dl)
    if role in {"original", "layout_reference"}:
        raise ValueError("The report original or approved layout must be a DOCX file.")
    return ""


def _inspect_office(content, suffix, role, project_dl):
    if suffix in {".docx", ".xlsx"}:
        try:
            with ZipFile(BytesIO(content)) as archive:
                if len(archive.infolist()) > 5000 or sum(item.file_size for item in archive.infolist()) > 200 * 1024 * 1024:
                    raise ValueError("The source expands beyond the supported document size.")
                if len(set(archive.namelist())) != len(archive.namelist()):
                    raise ValueError('The source has duplicate package parts; use a valid Office file.')
                for name in archive.namelist():
                    if name.endswith(('.xml', '.rels')):
                        root = etree.fromstring(archive.read(name), parser=etree.XMLParser(resolve_entities=False, no_network=True))
                        if root.getroottree().docinfo.doctype:
                            raise ValueError('Document type declarations are unsupported in report evidence.')
        except (BadZipFile, etree.XMLSyntaxError) as exc:
            raise ValueError("The Office source is unreadable. Choose a valid file.") from exc
    if role not in {"original", "layout_reference"}:
        return ""
    if suffix != ".docx":
        raise ValueError("The report original or approved layout must be a DOCX file.")
    try:
        document = Document(BytesIO(content))
        headers = "\n".join("".join(section.header._element.xpath(".//w:t/text()")) for section in document.sections)
        footers = "\n".join("".join(section.footer._element.xpath(".//w:t/text()")) for section in document.sections)
        ids = {value.upper() for value in re.findall(r"\bDL-[A-Za-z0-9-]+", headers)}
        if len(ids) > 1 or (role == "original" and len(ids) != 1) or not re.search(r"(?<![A-Z0-9])E-3707(?![A-Z0-9])", footers, re.I):
            raise ValueError("Choose an E-3707 Internal Report with one DL identity, or explicitly select a blank approved template as a layout reference.")
        report_dl = next(iter(ids), "")
        if role == "original" and (not project_dl or report_dl != project_dl.upper()):
            raise ValueError("This original belongs to another project. Select it explicitly as a layout reference instead.")
        return report_dl
    except (KeyError, OSError, BadZipFile) as exc:
        raise ValueError("The Internal Report cannot be read.") from exc
