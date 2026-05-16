"""Minimal runtime projection DTO-like structures for TASK_201."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MatrixRowTechnicalContext:
    """Technical context projected from one Matrix row."""

    test_item_label: str
    section: str
    method: str
    condition: str
    requirement: str


@dataclass(frozen=True, slots=True)
class ProjectionState:
    """Optional projection dimensions used by runtime read-model projections."""

    lifecycle: str | None = None
    evidence: str | None = None
    report_sync: str | None = None
    stale: str | None = None
    attention: str | None = None


@dataclass(frozen=True, slots=True)
class TokenReference:
    """Stable token reference derived from authority, group, and parsed token."""

    project_reference: str
    matrix_reference: str
    group_identity: str
    group_label: str
    raw_token: str
    sequence_number: int
    suffix_note: str | None
    stable_reference: str


@dataclass(frozen=True, slots=True)
class InteractiveStepTokenProjection:
    """Minimal Interactive Step Token projection DTO-like object."""

    project_reference: str
    matrix_reference: str
    group_identity: str
    group_label: str
    raw_token: str
    sequence_number: int
    suffix_note: str | None
    token_reference: str
    test_item_label: str
    section: str
    method: str
    condition: str
    requirement: str
    lifecycle_projection: str | None
    evidence_projection: str | None
    report_sync_projection: str | None
    stale_projection: str | None
    attention_projection: str | None


@dataclass(frozen=True, slots=True)
class ProjectionAggregationSummary:
    """Deterministic counts of already-supplied projection dimensions."""

    lifecycle_counts: tuple[tuple[str | None, int], ...] = ()
    evidence_counts: tuple[tuple[str | None, int], ...] = ()
    report_sync_counts: tuple[tuple[str | None, int], ...] = ()
    stale_counts: tuple[tuple[str | None, int], ...] = ()
    attention_counts: tuple[tuple[str | None, int], ...] = ()


@dataclass(frozen=True, slots=True)
class GroupRuntimeProjection:
    """Group-level runtime projection summary."""

    group_identity: str
    group_label: str
    total_tokens: int
    unique_sequences: int
    aggregation_summary: ProjectionAggregationSummary


@dataclass(frozen=True, slots=True)
class RuntimeProjectionSummary:
    """Top-level runtime projection summary for a token set."""

    total_tokens: int
    group_count: int
    groups: tuple[GroupRuntimeProjection, ...]


DEFAULT_FAKE_PROJECTION_STATE = ProjectionState(
    lifecycle="not_started",
    evidence="unknown",
    report_sync="unknown",
    stale="unknown",
    attention="none",
)
