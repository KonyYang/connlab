from __future__ import annotations

from pathlib import Path

import pytest

from backend.infrastructure.office import MsgCompatibilityStatus, probe_msg_samples


ROOT = Path(__file__).resolve().parents[2]


def test_msg_compatibility_probe_reports_missing_fixtures(tmp_path: Path) -> None:
    """TASK_027C documents that real validation is blocked without samples."""
    results = probe_msg_samples([], tmp_path / "intake")

    assert len(results) == 1
    assert results[0].status is MsgCompatibilityStatus.BLOCKED_MISSING_FIXTURES
    assert results[0].source_path is None


def test_msg_compatibility_probe_reports_supported_fixture(tmp_path: Path) -> None:
    """Supported fixture-style `.msg` samples are classified as supported."""
    sample = tmp_path / "supported.msg"
    sample.write_text(
        "\n".join(
            [
                "Subject: Supported sample",
                "From: Jane Engineer <jane@example.com>",
                "Attachment: request.docx; content=fixture",
            ]
        ),
        encoding="utf-8",
    )

    results = probe_msg_samples([sample], tmp_path / "intake")

    assert results[0].status is MsgCompatibilityStatus.SUPPORTED
    assert results[0].preserved_source_path is not None
    assert results[0].preserved_source_path.is_file()
    assert "1 attachment" in results[0].message


def test_msg_compatibility_probe_reports_unsupported_sample(tmp_path: Path) -> None:
    """Unsupported `.msg` samples fail clearly and preserve copied sources."""
    sample = tmp_path / "unsupported.msg"
    sample.write_bytes(b"\x00\x01opaque")

    results = probe_msg_samples([sample], tmp_path / "intake")

    assert results[0].status is MsgCompatibilityStatus.UNSUPPORTED
    assert results[0].preserved_source_path is not None
    assert results[0].preserved_source_path.is_file()


def test_real_msg_samples_are_supported_when_available(tmp_path: Path) -> None:
    """User-provided real `.msg` samples are compatibility checked without content output."""
    sample_dir = ROOT / "tests" / "fixtures" / "msg_samples"
    samples = sorted(sample_dir.glob("*.msg"))
    if not samples:
        pytest.skip("No real .msg samples are available in this workspace.")

    results = probe_msg_samples(samples, tmp_path / "intake")

    assert len(results) == len(samples)
    assert {result.status for result in results} == {MsgCompatibilityStatus.SUPPORTED}
    assert all(result.preserved_source_path for result in results)
