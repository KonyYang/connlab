"""Password-protect Office files through file-level or owned COM automation."""

from __future__ import annotations

from pathlib import Path
import struct
from typing import Callable

from backend.infrastructure.office.office_lifecycle import OfficeAutomationUnavailable


class OfficeFilePasswordError(RuntimeError):
    """Raised when Office cannot create or verify a protected output."""


class OfficeFilePasswordGateway:
    """Create password-protected Office copies without retaining COM ownership."""

    def __init__(
        self,
        *,
        dispatch: Callable[[str], object] | None = None,
        com_runtime: object | None = None,
        output_verifier: Callable[[Path, str], None] | None = None,
    ) -> None:
        self._dispatch = dispatch
        self._com_runtime = com_runtime
        self._output_verifier = output_verifier or _verify_password_protected_output

    def encrypt_and_verify(
        self,
        *,
        source_path: Path,
        output_path: Path,
        password: str,
        office_kind: str,
    ) -> None:
        """Write a protected output, then verify its encryption markers.

        ``password`` is deliberately applied to both Office open/read and
        edit/write protection wherever the file format exposes both fields.
        This keeps standalone Tools copies aligned with Project Workbench
        encryption; PowerPoint exposes one file password, which governs both
        opening and subsequent editing.
        """
        source = Path(source_path)
        output = Path(output_path)
        if not source.is_file():
            raise FileNotFoundError(f"Office source file does not exist: {source.name}")
        if not password:
            raise ValueError("An Office open and edit password is required.")
        expected_kind = _kind_from_suffix(source.suffix.lower())
        if expected_kind != office_kind:
            raise ValueError(f"Unsupported or mismatched Office file type: {source.suffix}")
        if office_kind == "word" and source.suffix.lower() == ".docx":
            try:
                _encrypt_ooxml_package(source, output, password)
                self._output_verifier(output, "word")
            except Exception as exc:
                output.unlink(missing_ok=True)
                if isinstance(exc, (FileNotFoundError, ValueError, OfficeFilePasswordError)):
                    raise
                raise OfficeFilePasswordError(_safe_office_error(exc)) from None
            return
        dispatch, com_runtime = self._automation()
        com_runtime.CoInitialize()
        try:
            if office_kind == "word":
                self._encrypt_word(dispatch, source, output, password)
            elif office_kind == "excel":
                self._encrypt_excel(dispatch, source, output, password)
            elif office_kind == "powerpoint":
                self._encrypt_powerpoint(dispatch, source, output, password)
            else:  # pragma: no cover - guarded by expected_kind
                raise ValueError(f"Unsupported Office kind: {office_kind}")
        except Exception as exc:
            if output.exists():
                output.unlink()
            if isinstance(exc, (FileNotFoundError, ValueError, OfficeFilePasswordError)):
                raise
            raise OfficeFilePasswordError(_safe_office_error(exc)) from None
        finally:
            com_runtime.CoUninitialize()

    def _automation(self) -> tuple[Callable[[str], object], object]:
        if self._dispatch is not None and self._com_runtime is not None:
            return self._dispatch, self._com_runtime
        try:
            import pythoncom  # type: ignore[import-not-found]
            import win32com.client  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - depends on Windows release host
            raise OfficeAutomationUnavailable(
                "Office file encryption requires pywin32 and desktop Microsoft Office."
            ) from exc
        return win32com.client.DispatchEx, pythoncom

    def _encrypt_word(
        self,
        dispatch: Callable[[str], object],
        source: Path,
        output: Path,
        password: str,
    ) -> None:
        app = dispatch("Word.Application")
        document = None
        verification = None
        try:
            app.Visible = False
            app.DisplayAlerts = 0
            document = app.Documents.Open(
                FileName=str(source),
                PasswordDocument=password,
                WritePasswordDocument=password,
                ReadOnly=False,
                AddToRecentFiles=False,
                Visible=False,
            )
            file_format = document.SaveFormat
            document.Password = password
            document.WritePassword = password
            document.SaveAs2(
                FileName=str(output),
                FileFormat=file_format,
                AddToRecentFiles=False,
                ReadOnlyRecommended=False,
            )
            document.Close(SaveChanges=False)
            document = None
            self._output_verifier(output, "word")
        finally:
            _close_owned_office_resources(
                app,
                (
                    (verification, lambda value: value.Close(SaveChanges=False)),
                    (document, lambda value: value.Close(SaveChanges=False)),
                ),
            )

    def _encrypt_excel(
        self,
        dispatch: Callable[[str], object],
        source: Path,
        output: Path,
        password: str,
    ) -> None:
        app = dispatch("Excel.Application")
        workbook = None
        verification = None
        try:
            app.Visible = False
            app.DisplayAlerts = False
            app.EnableEvents = False
            workbook = app.Workbooks.Open(
                Filename=str(source),
                UpdateLinks=0,
                ReadOnly=False,
                Password=password,
                IgnoreReadOnlyRecommended=True,
                AddToMru=False,
            )
            file_format = workbook.FileFormat
            workbook.SaveAs(
                Filename=str(output),
                FileFormat=file_format,
                Password=password,
                WriteResPassword=password,
                ReadOnlyRecommended=False,
                CreateBackup=False,
                AddToMru=False,
            )
            workbook.Close(SaveChanges=False)
            workbook = None
            self._output_verifier(output, "excel")
        finally:
            _close_owned_office_resources(
                app,
                (
                    (verification, lambda value: value.Close(SaveChanges=False)),
                    (workbook, lambda value: value.Close(SaveChanges=False)),
                ),
            )

    def _encrypt_powerpoint(
        self,
        dispatch: Callable[[str], object],
        source: Path,
        output: Path,
        password: str,
    ) -> None:
        app = dispatch("PowerPoint.Application")
        presentation = None
        try:
            presentation = app.Presentations.Open(
                FileName=f"{source.resolve()}::{password}",
                ReadOnly=False,
                Untitled=False,
                WithWindow=False,
            )
            presentation.Password = password
            presentation.SaveAs(str(output))
            presentation.Close()
            presentation = None
            self._output_verifier(output, "powerpoint")
        finally:
            _close_owned_office_resources(
                app,
                ((presentation, lambda value: value.Close()),),
            )


def _kind_from_suffix(suffix: str) -> str | None:
    if suffix in {".doc", ".docx"}:
        return "word"
    if suffix in {".xls", ".xlsx"}:
        return "excel"
    if suffix == ".pptx":
        return "powerpoint"
    return None


def _encrypt_ooxml_package(
    source: Path,
    output: Path,
    password: str,
) -> None:
    """Encrypt one OOXML package without starting an interactive Office process."""
    import msoffcrypto

    with source.open("rb") as source_stream:
        package = msoffcrypto.OfficeFile(source_stream)
        with output.open("wb") as output_stream:
            package.encrypt(password, output_stream)


def _verify_password_protected_output(path: Path, office_kind: str) -> None:
    """Verify Office's documented encryption marker without reopening a password dialog."""
    try:
        import olefile
    except ImportError as exc:  # pragma: no cover - declared runtime dependency
        raise OfficeFilePasswordError("Encrypted PowerPoint verification requires olefile.") from exc
    if not path.is_file() or not olefile.isOleFile(str(path)):
        raise OfficeFilePasswordError("Office output is not a password-protected container.")
    with olefile.OleFileIO(str(path)) as compound:
        streams = {"/".join(parts) for parts in compound.listdir()}
        suffix = path.suffix.lower()
        if suffix in {".docx", ".xlsx", ".pptx"}:
            protected = "EncryptionInfo" in streams and "EncryptedPackage" in streams
        elif suffix == ".doc" and compound.exists("WordDocument"):
            fib_base = compound.openstream("WordDocument").read(12)
            protected = len(fib_base) >= 12 and bool(int.from_bytes(fib_base[10:12], "little") & 0x0100)
        elif suffix == ".xls":
            workbook_stream = "Workbook" if compound.exists("Workbook") else "Book"
            protected = compound.exists(workbook_stream) and _xls_stream_has_filepass(
                compound.openstream(workbook_stream).read()
            )
        else:
            protected = False
    if not protected:
        raise OfficeFilePasswordError(
            f"{office_kind.title()} output does not contain Office password-encryption data."
        )


def _xls_stream_has_filepass(data: bytes) -> bool:
    offset = 0
    while offset + 4 <= len(data):
        record_type, record_size = struct.unpack_from("<HH", data, offset)
        if record_type == 0x002F:
            return True
        offset += 4 + record_size
    return False


def _safe_office_error(exc: Exception) -> str:
    del exc
    return (
        "Microsoft Office could not encrypt and verify the file. "
        "Close the file in Microsoft Office and try again."
    )


def _close_owned_office_resources(
    app: object,
    resources: tuple[tuple[object | None, Callable[[object], None]], ...],
) -> None:
    failures: list[Exception] = []
    for resource, close in resources:
        if resource is None:
            continue
        try:
            close(resource)
        except Exception as exc:
            failures.append(exc)
    try:
        app.Quit()
    except Exception as exc:
        failures.append(exc)
    if failures:
        raise failures[0]
