"""Compatibility probes for Outlook `.msg` samples."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from backend.infrastructure.office.office_facade import OfficeFacade


class MsgCompatibilityStatus(StrEnum):
    """Compatibility result status for `.msg` sample probes."""

    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    BLOCKED_MISSING_FIXTURES = "blocked_missing_fixtures"


@dataclass(frozen=True, slots=True)
class MsgCompatibilityResult:
    """One compatibility probe result for an Outlook `.msg` source."""

    status: MsgCompatibilityStatus
    source_path: Path | None
    message: str
    preserved_source_path: Path | None = None


def probe_msg_samples(
    sample_paths: list[Path],
    target_root: Path,
    *,
    office_facade: OfficeFacade | None = None,
) -> list[MsgCompatibilityResult]:
    """Probe `.msg` samples and classify support without Outlook automation."""
    if not sample_paths:
        return [
            MsgCompatibilityResult(
                status=MsgCompatibilityStatus.BLOCKED_MISSING_FIXTURES,
                source_path=None,
                message="No real .msg fixtures are available for compatibility validation.",
            )
        ]

    facade = office_facade or OfficeFacade()
    results: list[MsgCompatibilityResult] = []
    for source_path in sample_paths:
        target_dir = target_root / source_path.stem
        try:
            package = facade.import_outlook_msg(source_path, target_dir)
        except Exception as exc:
            results.append(
                MsgCompatibilityResult(
                    status=MsgCompatibilityStatus.UNSUPPORTED,
                    source_path=source_path,
                    message=str(exc),
                    preserved_source_path=getattr(exc, "stored_path", None),
                )
            )
            continue
        results.append(
            MsgCompatibilityResult(
                status=MsgCompatibilityStatus.SUPPORTED,
                source_path=source_path,
                message=(
                    f"Read metadata and extracted {len(package.attachments)} attachment(s)."
                ),
                preserved_source_path=package.source_stored_path,
            )
        )
    return results
