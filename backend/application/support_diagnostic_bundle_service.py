"""Build a privacy-bounded support bundle from packaged runtime diagnostics."""

from __future__ import annotations

import io
import json
import platform
import sys
import zipfile
from backend.shared.operation_diagnostics import safe_text, safe_value
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


_RELEASE_FIELDS = (
    "release_name",
    "version",
    "git_commit",
    "built_at_utc",
    "server_sha256",
)


@dataclass(frozen=True)
class DiagnosticBundle:
    filename: str
    content: bytes


class SupportDiagnosticBundleService:
    """Export only allow-listed logs and release metadata, never business data."""

    def __init__(
        self,
        *,
        logs_dir: Path,
        release_manifest_path: Path | None = None,
    ) -> None:
        self._logs_dir = logs_dir
        self._release_manifest_path = release_manifest_path

    def build_bundle(self) -> DiagnosticBundle:
        created_at = datetime.now(UTC)
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(
                "manifest.json",
                json.dumps(
                    {
                        "created_at_utc": created_at.isoformat(),
                        "runtime": {
                            "platform": platform.platform(),
                            "python": platform.python_version(),
                            "frozen": bool(getattr(sys, "frozen", False)),
                        },
                        "release": self._read_safe_release_metadata(),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
            )
            for log_path in self._allowed_log_paths():
                try:
                    text = log_path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                archive.writestr(f"logs/{log_path.name}", _redact_log_text(text))

        timestamp = created_at.strftime("%Y%m%d_%H%M%S")
        return DiagnosticBundle(
            filename=f"ConnLab_Diagnostics_{timestamp}.zip",
            content=payload.getvalue(),
        )

    def _allowed_log_paths(self) -> list[Path]:
        if not self._logs_dir.is_dir():
            return []
        try:
            candidates = list(self._logs_dir.iterdir())
        except OSError:
            return []
        return sorted(
            (
                path
                for path in candidates
                if path.is_file()
                and (
                    path.name == "connlab.log"
                    or path.name.removeprefix("connlab.log.").isdigit()
                )
            ),
            key=lambda path: path.name,
        )

    def _read_safe_release_metadata(self) -> dict[str, str]:
        path = self._release_manifest_path
        if path is None or not path.is_file():
            return {}
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return {}
        if not isinstance(raw, dict):
            return {}
        return {
            key: str(raw[key])[:256]
            for key in _RELEASE_FIELDS
            if key in raw and raw[key] is not None
        }


def _redact_log_text(text: str) -> str:
    # Redact individual lines/quoted paths, preserving following diagnostic fields.
    lines = []
    for line in text.splitlines():
        prefix, marker, payload = line.partition("{")
        try:
            record = json.loads(marker + payload)
        except (ValueError, TypeError):
            lines.append(safe_text(line))
        else:
            lines.append(safe_text(prefix) + json.dumps(safe_value(record), ensure_ascii=False))
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")
