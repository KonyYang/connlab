"""Project-level schedule authority models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ProjectScheduleRevision:
    """One immutable-by-policy confirmed Project Schedule revision."""

    revision_id: str
    project_id: str
    revision_sequence: int
    state: str
    fingerprint: str
    matrix_input_fingerprint: str
    based_on_confirmed_matrix_id: str | None
    based_on_confirmed_matrix_revision: int | None
    based_on_basic_information_version: int | None
    sample_received_date: str
    post_test_buffer_days: str
    test_start_date: str
    test_complete_date: str
    estimated_completion_date: str
    confirmed_by: str
    confirmed_at: str
    superseded_at: str | None = None
    superseded_reason: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectScheduleSuggestion:
    post_test_buffer_days: str
    test_start_date: str
    test_complete_date: str
    estimated_completion_date: str


@dataclass(frozen=True, slots=True)
class ProjectScheduleWorkspace:
    status: str
    project_id: str
    sample_received_date: str
    critical_group_id: str | None
    critical_group_days: str
    suggestion: ProjectScheduleSuggestion
    confirmed_revision: ProjectScheduleRevision | None
