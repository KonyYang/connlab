"""Application service for controlled Section 2 Word write-back."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Protocol

from backend.application.section2_completion_preview_service import (
    Section2CompletionPreviewCommand,
    Section2CompletionPreviewError,
    Section2CompletionPreviewNotFoundError,
    Section2CompletionPreviewService,
    Section2DraftStore,
    Section2ProjectStore,
)
from backend.infrastructure.office import (
    OfficeFacade,
    WordSection2FieldChange,
    WordSection2WriteResult,
)


class Section2WriteBackError(ValueError):
    """Raised when a Section 2 write-back request is invalid."""


class Section2WriteBackNotFoundError(LookupError):
    """Raised when write-back input data cannot be found."""


class Section2WordWriter(Protocol):
    """Office operation needed by the Section 2 write-back service."""

    def write_word_section2_fields(
        self,
        source_path: Path,
        fields: dict[str, str],
    ) -> WordSection2WriteResult:
        """Write Section 2 fields into a Word document."""


@dataclass(frozen=True, slots=True)
class Section2WriteBackCommand:
    """Input for controlled Section 2 write-back."""

    project_id: str
    draft_id: str
    target_application_form_path: Path
    received_date: date
    lab: str | None = None
    assigned_personnel: str | None = None
    sample_condition: str | None = None
    sample_preparation_days: int = 1
    test_group_scheduling_buffer_days: int = 1
    report_drafting_days: int = 3
    review_days: int = 1
    operator: str | None = None


@dataclass(frozen=True, slots=True)
class Section2WriteBackResult:
    """Result of controlled Section 2 write-back."""

    project_id: str
    draft_id: str
    target_application_form_path: Path
    backup_path: Path
    changed_fields: tuple[WordSection2FieldChange, ...]
    unchanged_fields: tuple[WordSection2FieldChange, ...]
    warnings: tuple[str, ...]
    written_at: str
    operator: str | None


class Section2WriteBackService:
    """Write approved Section 2 preview values into a `.docx` application form."""

    def __init__(
        self,
        *,
        project_store: Section2ProjectStore,
        draft_store: Section2DraftStore,
        office: Section2WordWriter | None = None,
    ) -> None:
        """Create the service with repository ports and an Office boundary."""
        self._preview_service = Section2CompletionPreviewService(
            project_store=project_store,
            draft_store=draft_store,
        )
        self._office = office or OfficeFacade()

    def write_back(self, command: Section2WriteBackCommand) -> Section2WriteBackResult:
        """Back up and write approved Section 2 values into the target form."""
        target = _validate_target_path(command.target_application_form_path)
        preview = _preview_or_raise(self._preview_service, command)
        fields = {
            "lab": preview.lab or "",
            "assigned_personnel": preview.assigned_personnel or "",
            "received_date": preview.received_date.isoformat(),
            "estimated_completion_date": preview.estimated_completion_date.isoformat(),
            "sample_condition": preview.sample_condition or "",
        }
        backup_path = _backup_path(target)
        shutil.copy2(target, backup_path)
        try:
            write_result = self._office.write_word_section2_fields(target, fields)
        except Exception as exc:
            raise Section2WriteBackError(str(exc)) from exc
        return Section2WriteBackResult(
            project_id=command.project_id,
            draft_id=command.draft_id,
            target_application_form_path=target,
            backup_path=backup_path,
            changed_fields=write_result.changed_fields,
            unchanged_fields=write_result.unchanged_fields,
            warnings=tuple(preview.warnings) + tuple(write_result.warnings),
            written_at=datetime.now(UTC).isoformat(),
            operator=_optional_text(command.operator),
        )


def _preview_or_raise(
    preview_service: Section2CompletionPreviewService,
    command: Section2WriteBackCommand,
):
    """Compute Section 2 preview and map preview exceptions to write-back errors."""
    try:
        return preview_service.preview(
            Section2CompletionPreviewCommand(
                project_id=command.project_id,
                draft_id=command.draft_id,
                received_date=command.received_date,
                lab=command.lab,
                assigned_personnel=command.assigned_personnel,
                sample_condition=command.sample_condition,
                sample_preparation_days=command.sample_preparation_days,
                test_group_scheduling_buffer_days=(
                    command.test_group_scheduling_buffer_days
                ),
                report_drafting_days=command.report_drafting_days,
                review_days=command.review_days,
            )
        )
    except Section2CompletionPreviewNotFoundError as exc:
        raise Section2WriteBackNotFoundError(str(exc)) from exc
    except Section2CompletionPreviewError as exc:
        raise Section2WriteBackError(str(exc)) from exc


def _validate_target_path(path: Path) -> Path:
    """Validate the target application form path."""
    target = Path(path)
    if target.suffix.lower() != ".docx":
        raise Section2WriteBackError(f"Only .docx write-back is supported: {target}")
    if not target.is_file():
        raise Section2WriteBackNotFoundError(
            f"Application form target does not exist: {target}"
        )
    return target


def _backup_path(target: Path) -> Path:
    """Return a unique backup path next to the target file."""
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    candidate = target.with_name(f"{target.name}.bak-{stamp}")
    index = 1
    while candidate.exists():
        candidate = target.with_name(f"{target.name}.bak-{stamp}-{index}")
        index += 1
    return candidate


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None
