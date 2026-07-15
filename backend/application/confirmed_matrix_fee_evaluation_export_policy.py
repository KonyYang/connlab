"""Small path and operator policy helpers for Fee Evaluation exports."""

from __future__ import annotations

import getpass
from pathlib import Path


def resolve_prepared_by(*, prepared_by: str | None = None, connlab_user: str | None = None, user_getter=getpass.getuser) -> tuple[str | None, tuple[str, ...]]:
    explicit = _text(prepared_by)
    if explicit:
        return explicit, ()
    configured = _text(connlab_user)
    if configured:
        return configured, ()
    try:
        local_user = _text(user_getter())
    except OSError:
        local_user = None
    return (local_user, ()) if local_user else (None, ("Prepared by could not be resolved from the current user.",))


def require_template(path: Path) -> Path:
    candidate = Path(path)
    if candidate.suffix.lower() not in {".xls", ".xlsx"}:
        raise ValueError(f"Unsupported fee template type: {candidate}")
    if not candidate.is_file():
        raise FileNotFoundError(f"Template does not exist: {candidate}")
    return candidate


def require_output_dir(path: Path | None) -> Path:
    if path is None:
        raise ValueError("output_dir is required for fee evaluation export.")
    candidate = Path(path)
    if not candidate.is_dir():
        raise FileNotFoundError(f"Output directory does not exist: {candidate}")
    return candidate


def _text(value: str | None) -> str | None:
    normalized = (value or "").strip()
    return normalized or None
