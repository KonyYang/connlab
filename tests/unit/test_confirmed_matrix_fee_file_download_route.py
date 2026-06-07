from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import HTTPException

from backend.api.routes_confirmed_matrix_fee_evaluation_export import (
    _validate_fee_file_download_path,
)


def test_fee_file_download_path_guard_accepts_xls_inside_download_dir(
    tmp_path: Path,
) -> None:
    download_dir = tmp_path / "generated_fee_files"
    download_dir.mkdir()
    output_path = download_dir / "Fee.xls"
    output_path.write_bytes(b"xls")

    assert _validate_fee_file_download_path(output_path, download_dir) == output_path.resolve()


def test_fee_file_download_path_guard_rejects_path_outside_download_dir(
    tmp_path: Path,
) -> None:
    download_dir = tmp_path / "generated_fee_files"
    download_dir.mkdir()
    outside = tmp_path / "Fee.xls"
    outside.write_bytes(b"xls")

    with pytest.raises(HTTPException) as exc_info:
        _validate_fee_file_download_path(outside, download_dir)

    assert exc_info.value.status_code == 500
    assert "outside generated_fee_files" in str(exc_info.value.detail)


def test_fee_file_download_path_guard_rejects_non_xls_inside_download_dir(
    tmp_path: Path,
) -> None:
    download_dir = tmp_path / "generated_fee_files"
    download_dir.mkdir()
    output_path = download_dir / "Fee.xlsx"
    output_path.write_bytes(b"xlsx")

    with pytest.raises(HTTPException) as exc_info:
        _validate_fee_file_download_path(output_path, download_dir)

    assert exc_info.value.status_code == 500
    assert "expected a .xls workbook" in str(exc_info.value.detail)
