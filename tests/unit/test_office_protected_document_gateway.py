from __future__ import annotations

from pathlib import Path

import pytest

from backend.infrastructure.office.office_protected_document_gateway import (
    ProtectedWordPackageGateway,
)


class _Protector:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def encrypt_and_verify(self, **kwargs) -> None:
        self.calls.append(kwargs)
        Path(kwargs["output_path"]).write_bytes(b"protected-result")


def test_plain_word_package_stages_without_office_automation(tmp_path: Path) -> None:
    source = tmp_path / "plain.docx"
    source.write_bytes(b"plain-package")
    destination = tmp_path / "editable.docx"
    decrypt_calls: list[tuple[Path, Path, str]] = []
    gateway = ProtectedWordPackageGateway(
        protected_detector=lambda _path: False,
        decryptor=lambda source, output, password: decrypt_calls.append(
            (source, output, password)
        ),
    )

    state = gateway.stage_editable_copy(source, destination)

    assert state.was_password_protected is False
    assert destination.read_bytes() == b"plain-package"
    assert decrypt_calls == []


def test_protected_word_package_is_decrypted_and_reprotected_without_exposing_password(
    tmp_path: Path,
) -> None:
    source = tmp_path / "protected.docx"
    source.write_bytes(b"encrypted-package")
    destination = tmp_path / "editable.docx"
    decrypt_calls: list[tuple[Path, Path, str]] = []
    protector = _Protector()

    def decrypt(source_path: Path, output_path: Path, password: str) -> None:
        decrypt_calls.append((source_path, output_path, password))
        output_path.write_bytes(b"editable-package")

    gateway = ProtectedWordPackageGateway(
        protected_detector=lambda _path: True,
        decryptor=decrypt,
        protector=protector,
    )

    state = gateway.stage_editable_copy(source, destination)
    destination.write_bytes(b"updated-package")
    gateway.restore_password_protection(destination, state)

    assert state.was_password_protected is True
    assert decrypt_calls == [(source, destination, "DGLAB")]
    assert destination.read_bytes() == b"protected-result"
    assert len(protector.calls) == 1
    assert protector.calls[0]["password"] == "DGLAB"
    assert protector.calls[0]["office_kind"] == "word"
    assert protector.calls[0]["source_path"] != protector.calls[0]["output_path"]


def test_readable_copy_removes_decrypted_temporary_file(tmp_path: Path) -> None:
    source = tmp_path / "protected.docx"
    source.write_bytes(b"encrypted-package")

    def decrypt(_source: Path, output: Path, _password: str) -> None:
        output.write_bytes(b"editable-package")

    gateway = ProtectedWordPackageGateway(
        protected_detector=lambda _path: True,
        decryptor=decrypt,
    )

    with gateway.readable_copy(source) as readable:
        assert readable.read_bytes() == b"editable-package"
        temporary = readable

    assert not temporary.exists()


def test_failed_decryption_removes_partial_copy_and_redacts_password(
    tmp_path: Path,
) -> None:
    source = tmp_path / "protected.docx"
    source.write_bytes(b"encrypted-package")
    destination = tmp_path / "editable.docx"

    def fail_decrypt(_source: Path, output: Path, password: str) -> None:
        output.write_bytes(b"partial-plain-text")
        raise RuntimeError(f"bad password {password}")

    gateway = ProtectedWordPackageGateway(
        protected_detector=lambda _path: True,
        decryptor=fail_decrypt,
    )

    with pytest.raises(Exception) as error:
        gateway.stage_editable_copy(source, destination)

    assert not destination.exists()
    assert "DGLAB" not in str(error.value)
    assert error.value.__cause__ is None
