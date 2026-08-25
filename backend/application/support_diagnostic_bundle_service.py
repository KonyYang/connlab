"""Build a privacy-bounded support bundle from packaged runtime diagnostics."""

from __future__ import annotations

import io
import json
import platform
import re
import sys
import zipfile
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
_WINDOWS_PATH_TO_LINE_END = re.compile(r"(?im)(?:[a-z]:[\\/]|\\\\).*$")
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(password|passwd|token|api[_-]?key|secret)\s*[=:]\s*([^\s,;]+)"
)
_JSON_SECRET_ASSIGNMENT = re.compile(
    r'''(?i)(["'])(password|passwd|token|api[_-]?key|secret)\1\s*:\s*(["'])[^"'\r\n]*\3'''
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
    redacted = _JSON_SECRET_ASSIGNMENT.sub(
        lambda match: f'{match.group(1)}{match.group(2)}{match.group(1)}:'
        f'{match.group(3)}<REDACTED>{match.group(3)}',
        text,
    )
    redacted = _SECRET_ASSIGNMENT.sub(
        lambda match: f"{match.group(1)}=<REDACTED>", redacted
    )
    return _WINDOWS_PATH_TO_LINE_END.sub("<LOCAL_PATH>", redacted)
