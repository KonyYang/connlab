"""Support types for Project Folder Application Form write-back."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from time import perf_counter
from typing import Protocol

from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationSnapshot,
)
from backend.domain import ApplicationForm, ProjectOutputSource, ProjectOutputStatus

APPLICATION_FORM_OUTPUT_MODE = "application-form-output:lab_section_v1"


class ReusableApplicationFormArtifactStore(Protocol):
    """Reusable Application Form artifact lookup/cache dependency."""

    def find_current_artifact(
        self,
        *,
        project_id: str,
        source_context_signature: str,
        final_target_path: Path,
    ) -> Path | None:
        """Return a verified reusable filled Application Form artifact."""

    def save_current_artifact(
        self,
        *,
        project_id: str,
        source_context_signature: str,
        source_path: Path,
        source_sha256: str,
    ) -> None:
        """Persist a verified filled Application Form artifact for future reuse."""


class NullReusableApplicationFormArtifactStore:
    """Default no-op Application Form artifact cache."""

    def find_current_artifact(
        self,
        *,
        project_id: str,
        source_context_signature: str,
        final_target_path: Path,
    ) -> Path | None:
        """Return no reusable artifact."""
        return None

    def save_current_artifact(
        self,
        *,
        project_id: str,
        source_context_signature: str,
        source_path: Path,
        source_sha256: str,
    ) -> None:
        """Do not persist reusable artifacts."""


@dataclass(frozen=True, slots=True)
class ApplicationFormWriteBackTiming:
    """One Application Form write-back timing entry."""

    label: str
    elapsed_ms: int


def source_context_signature(
    form: ApplicationForm,
    basic_information: ConfirmedBasicInformationSnapshot,
    *,
    source_sha256: str | None,
) -> str:
    """Return the strict reusable Application Form output context."""
    source_token = source_sha256 or "unknown"
    return (
        f"application-form:{form.form_id}@source:{source_token}"
        f"|{basic_information.context_signature}"
        f"|{APPLICATION_FORM_OUTPUT_MODE}"
    )


def append_timing(
    timings: list[ApplicationFormWriteBackTiming],
    label: str,
    start: float,
) -> None:
    """Append one elapsed Application Form write-back timing."""
    timings.append(
        ApplicationFormWriteBackTiming(
            label=label,
            elapsed_ms=int(round((perf_counter() - start) * 1000)),
        )
    )


def office_timings(write_result: object) -> tuple[ApplicationFormWriteBackTiming, ...]:
    """Return infrastructure Office timings from a write result."""
    snapshot = getattr(write_result, "timings", None)
    stages = getattr(snapshot, "stages", tuple()) if snapshot is not None else tuple()
    return tuple(
        ApplicationFormWriteBackTiming(
            label=f"office.{getattr(stage, 'name')}",
            elapsed_ms=int(round(float(getattr(stage, "seconds")) * 1000)),
        )
        for stage in stages
    )


def is_current_target_reusable(
    item: object | None,
    target: Path,
    context_signature: str,
) -> bool:
    """Return whether the current target already matches the write-back context."""
    if item is None:
        return False
    if getattr(item, "status", None) is not ProjectOutputStatus.CURRENT:
        return False
    if getattr(item, "source", None) is not ProjectOutputSource.SYSTEM_GENERATED:
        return False
    if getattr(item, "source_context_signature", None) != context_signature:
        return False
    stored_sha = getattr(item, "output_sha256", None)
    return bool(stored_sha and target.is_file() and sha256_file(target) == stored_sha)


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest for one file."""
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
