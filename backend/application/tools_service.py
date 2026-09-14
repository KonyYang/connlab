"""Project-independent document tools with safe, non-overwriting outputs."""

from __future__ import annotations

import os
from pathlib import Path
import re
from typing import Callable, Protocol
from uuid import uuid4
from zipfile import BadZipFile, ZipFile

from backend.modules.ltr import LtrNumberError, excel_password_for_dl_number
from backend.shared.office_document_password import OFFICE_DOCUMENT_PASSWORD


class ToolsError(ValueError):
    """Raised when a standalone tool cannot safely process its input."""


class CustomerReportWriterPort(Protocol):
    def generate_customer_report(
        self,
        *,
        source_path: Path,
        template_path: Path,
        output_path: Path,
        progress: Callable[[str], None] | None = None,
    ) -> Path: ...


class OfficeProtectionPort(Protocol):
    def encrypt_and_verify(
        self,
        *,
        source_path: Path,
        output_path: Path,
        password: str,
        office_kind: str,
    ) -> None: ...


class ToolsService:
    """Coordinate standalone file tools without project authority or path writes."""

    def __init__(
        self,
        *,
        customer_report_writer: CustomerReportWriterPort,
        office_protector: OfficeProtectionPort,
    ) -> None:
        self._customer_report_writer = customer_report_writer
        self._office_protector = office_protector

    def generate_customer_report(
        self,
        *,
        source_path: Path,
        template_path: Path,
        output_path: Path,
        progress: Callable[[str], None] | None = None,
    ) -> Path:
        """Convert one compatible Internal Report into a new customer report."""
        source = Path(source_path)
        template = Path(template_path)
        output = Path(output_path)
        if progress is not None:
            progress("validating")
        self._validate_internal_report(source)
        if template.suffix.casefold() != ".docx" or not template.is_file():
            raise ToolsError("The approved customer-report template is unavailable.")
        if output.resolve() in {source.resolve(), template.resolve()}:
            raise ToolsError("The customer report output must be a new file.")
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            raise ToolsError("A customer report with this name already exists.")
        try:
            written = self._customer_report_writer.generate_customer_report(
                source_path=source,
                template_path=template,
                output_path=output,
                progress=progress,
            )
        except ToolsError:
            raise
        except Exception as exc:
            raise ToolsError(f"Unable to generate customer report: {exc}") from exc
        if Path(written).resolve() != output.resolve() or not output.is_file():
            output.unlink(missing_ok=True)
            raise ToolsError("Customer report generation did not produce the expected file.")
        return output

    def encrypt_copy(
        self,
        *,
        source_path: Path,
        output_path: Path,
        password: str | None = None,
    ) -> Path:
        """Create and verify an encrypted copy while leaving the source untouched.

        Excel copies follow the Project Workbench rule: the source filename
        must begin with a standard DL number, and its ``YYYYMMNNN`` plus any
        letter-led suffix becomes the open/edit password.
        """
        source = Path(source_path)
        output = Path(output_path)
        office_kind = _office_kind(source)
        password = _resolve_encryption_password(source.name, office_kind, password)
        if output.resolve() == source.resolve():
            raise ToolsError("The encrypted output must be a separate copy.")
        if not password:
            raise ToolsError("An encryption password is required.")
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            raise ToolsError("An encrypted copy with this name already exists.")
        stage = output.with_name(f".connlab-tools-{uuid4().hex}{output.suffix}")
        try:
            self._office_protector.encrypt_and_verify(
                source_path=source,
                output_path=stage,
                password=password,
                office_kind=office_kind,
            )
            if not stage.is_file() or stage.stat().st_size <= 0:
                raise ToolsError("The encryption adapter did not produce a verified file.")
            os.replace(stage, output)
        except ToolsError:
            raise
        except Exception as exc:
            raise ToolsError(f"Unable to encrypt the file: {exc}") from exc
        finally:
            stage.unlink(missing_ok=True)
        return output

    @staticmethod
    def _validate_internal_report(source: Path) -> None:
        if source.suffix.casefold() != ".docx" or not source.is_file():
            raise ToolsError("Only a ConnLab Internal Report .docx file can be converted.")
        try:
            with ZipFile(source) as package:
                names = set(package.namelist())
                if "word/document.xml" not in names:
                    raise ToolsError("The selected Word file is missing its document body.")
                xml_parts = [
                    package.read(name).decode("utf-8", errors="ignore")
                    for name in names
                    if name.startswith("word/") and name.endswith(".xml")
                ]
        except (BadZipFile, OSError, KeyError) as exc:
            raise ToolsError("The selected file is not a readable Word document.") from exc
        text = re.sub(r"<[^>]+>", " ", " ".join(xml_parts))
        text = re.sub(r"\s+", " ", text).casefold()
        if "laboratory test report" not in text:
            raise ToolsError(
                "The selected document is not recognized as a ConnLab Internal Report; "
                "the 'LABORATORY TEST REPORT' marker is missing."
            )


def _office_kind(source: Path) -> str:
    if not source.is_file():
        raise ToolsError("The selected file is no longer available.")
    kinds = {
        ".doc": "word",
        ".docx": "word",
        ".xls": "excel",
        ".xlsx": "excel",
        ".pptx": "powerpoint",
    }
    kind = kinds.get(source.suffix.casefold())
    if kind is None:
        raise ToolsError("Only Word, Excel, and PowerPoint files can be encrypted.")
    return kind


_EXCEL_DL_FILENAME_PREFIX = re.compile(
    r"^(DL-\d{4}-\d{2}-\d{3}(?:[A-Z][A-Z0-9]*)?)(?=$|[^A-Z0-9])",
    re.IGNORECASE,
)


def _resolve_encryption_password(
    file_name: str,
    office_kind: str,
    requested_password: str | None,
) -> str:
    """Resolve the shared Office password policy for one standalone copy."""
    if office_kind != "excel":
        return requested_password or OFFICE_DOCUMENT_PASSWORD
    match = _EXCEL_DL_FILENAME_PREFIX.match(Path(file_name).stem)
    if match is None:
        raise ToolsError(
            "Excel files must start with DL-YYYY-MM-NNN before the first separator."
        )
    try:
        derived = excel_password_for_dl_number(match.group(1))
    except LtrNumberError as exc:  # pragma: no cover - regex and parser share the rule
        raise ToolsError(
            "Excel files must start with DL-YYYY-MM-NNN before the first separator."
        ) from exc
    if requested_password is not None and requested_password != derived:
        raise ToolsError(
            "Excel encryption passwords are derived from the filename and cannot be overridden."
        )
    return derived
