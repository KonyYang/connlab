"""Safe access to password-protected Word packages owned by ConnLab workflows."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import tempfile
from typing import Callable, Iterator, Protocol
from uuid import uuid4
import zipfile

from backend.infrastructure.office.office_file_password_gateway import (
    OfficeFilePasswordGateway,
)
from backend.shared.office_document_password import OFFICE_DOCUMENT_PASSWORD


class OfficeProtectedDocumentError(RuntimeError):
    """Raised when a protected Office document cannot be safely materialized."""


class OfficeFileProtectorPort(Protocol):
    """Password-protection operation required when restoring an edited package."""

    def encrypt_and_verify(
        self,
        *,
        source_path: Path,
        output_path: Path,
        password: str,
        office_kind: str,
    ) -> None:
        """Write and verify a protected Office file."""


@dataclass(frozen=True, slots=True)
class WordPackageProtectionState:
    """Protection state captured before a caller edits a Word package."""

    was_password_protected: bool


class ProtectedWordPackageGateway:
    """Expose temporary readable/editable `.docx` packages without leaking passwords."""

    def __init__(
        self,
        *,
        password: str = OFFICE_DOCUMENT_PASSWORD,
        protected_detector: Callable[[Path], bool] | None = None,
        decryptor: Callable[[Path, Path, str], None] | None = None,
        protector: OfficeFileProtectorPort | None = None,
    ) -> None:
        self._password = password
        self._protected_detector = protected_detector or _is_password_protected_docx
        self._decryptor = decryptor or _decrypt_word_document
        self._protector = protector or OfficeFilePasswordGateway()

    @contextmanager
    def readable_copy(self, source_path: Path) -> Iterator[Path]:
        """Yield a python-docx-readable path and remove any decrypted copy afterward."""
        source = _validated_docx(source_path)
        if not self._protected_detector(source):
            yield source
            return
        with tempfile.TemporaryDirectory(prefix="connlab-word-") as directory:
            readable = Path(directory) / "document.docx"
            self._materialize_decrypted(source, readable)
            if not readable.is_file():
                raise OfficeProtectedDocumentError(
                    "The protected Word document did not produce a readable copy."
                )
            yield readable

    def stage_editable_copy(
        self,
        source_path: Path,
        output_path: Path,
    ) -> WordPackageProtectionState:
        """Create one caller-owned editable copy and return the source protection state."""
        source = _validated_docx(source_path)
        output = Path(output_path)
        protected = self._protected_detector(source)
        if protected:
            self._materialize_decrypted(source, output)
        else:
            shutil.copy2(source, output)
        if not output.is_file():
            raise OfficeProtectedDocumentError(
                "The protected Word document did not produce an editable copy."
            )
        return WordPackageProtectionState(was_password_protected=protected)

    def _materialize_decrypted(self, source: Path, output: Path) -> None:
        try:
            self._decryptor(source, output, self._password)
        except OfficeProtectedDocumentError:
            output.unlink(missing_ok=True)
            raise
        except Exception:
            output.unlink(missing_ok=True)
            raise OfficeProtectedDocumentError(
                "The password-protected Word document could not be decrypted."
            ) from None

    def restore_password_protection(
        self,
        editable_path: Path,
        state: WordPackageProtectionState,
    ) -> None:
        """Restore the original password-protection state after a successful edit."""
        if not state.was_password_protected:
            return
        editable = _validated_docx(editable_path)
        protected = editable.with_name(
            f".connlab-protected-{uuid4().hex}{editable.suffix}"
        )
        try:
            self._protector.encrypt_and_verify(
                source_path=editable,
                output_path=protected,
                password=self._password,
                office_kind="word",
            )
            if not protected.is_file():
                raise OfficeProtectedDocumentError(
                    "The Word document password protection was not restored."
                )
            os.replace(protected, editable)
        finally:
            protected.unlink(missing_ok=True)


def _validated_docx(path: Path) -> Path:
    resolved = Path(path)
    if resolved.suffix.casefold() != ".docx" or not resolved.is_file():
        raise FileNotFoundError(f"Word document does not exist: {resolved}")
    return resolved


def _is_password_protected_docx(path: Path) -> bool:
    if zipfile.is_zipfile(path):
        return False
    try:
        import olefile
    except ImportError as exc:  # pragma: no cover - declared runtime dependency
        raise OfficeProtectedDocumentError(
            "Protected Word document inspection requires olefile."
        ) from exc
    if not olefile.isOleFile(str(path)):
        return False
    with olefile.OleFileIO(str(path)) as compound:
        streams = {"/".join(parts) for parts in compound.listdir()}
    return "EncryptionInfo" in streams and "EncryptedPackage" in streams


def _decrypt_word_document(source: Path, output: Path, password: str) -> None:
    try:
        import msoffcrypto

        with source.open("rb") as source_stream:
            package = msoffcrypto.OfficeFile(source_stream)
            package.load_key(password=password, verify_password=True)
            with output.open("wb") as output_stream:
                package.decrypt(output_stream)
    except Exception:
        raise OfficeProtectedDocumentError(
            "The password-protected Word document could not be decrypted."
        ) from None
