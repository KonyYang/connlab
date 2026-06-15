"""Pending Matrix-to-Fee rebase application values and lifecycle service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import Callable, Protocol, Literal
from uuid import uuid4

from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportValues,
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedManualRow,
    edited_row_identity,
)
from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    BuildMatrixBasicFeeTemplateCommand,
    ConfirmedMatrixFeeTemplateBasicFillService,
    MatrixBasicFillLine,
)
from backend.application.matrix_fee_draft_rebase_service import (
    MatrixFeeDraftRebaseService,
    MatrixFeeInactiveRemovedRow,
    MatrixFeeRebaseLineage,
    MatrixFeeRebaseResult,
    MatrixFeeRebaseSourceRow,
    MatrixFeeRebaseSummary,
    MatrixFeeRebaseTargetGroup,
    MatrixFeeRebaseTargetRow,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftStore,
)
from backend.domain.project_matrix_draft_models import ProjectMatrixDraftSnapshot
from backend.modules.test_plan.matrix_step_sequence_validation import parse_step_tokens

MatrixFeePendingRebaseStatus = Literal["not_required", "current", "failed"]


@dataclass(frozen=True, slots=True)
class MatrixFeePendingRebaseSnapshot:
    """Persisted pending Fee rebase payload for one Matrix draft/rule context."""

    pending_rebase_id: str
    project_id: str
    project_matrix_draft_id: str
    base_confirmed_matrix_id: str
    base_confirmed_revision: int
    fee_rule_version_id: str
    matrix_draft_payload_signature: str
    generation: int
    payload_json: str
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class RebaseAfterMatrixAutosaveCommand:
    """Input for one best-effort pending Fee rebase after Matrix autosave."""

    project_id: str
    active_confirmed_matrix_id: str | None
    active_confirmed_revision: int | None
    saved_matrix_draft: ProjectMatrixDraftSnapshot | None
    saved_payload_signature: str | None
    fee_rule_version_id: str
    generation: int | None = None


@dataclass(frozen=True, slots=True)
class DeletePendingRebaseForMatrixDraftCommand:
    """Input for deleting pending Fee rebases after Matrix draft cancel."""

    project_matrix_draft_id: str


@dataclass(frozen=True, slots=True)
class MatrixFeePendingRebaseResult:
    """Best-effort pending rebase result attached to Matrix autosave."""

    status: MatrixFeePendingRebaseStatus
    summary: MatrixFeeRebaseSummary | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class MatrixFeePendingRebaseDeleteResult:
    """Result of deleting pending rebase rows for a Matrix draft."""

    deleted_count: int


class MatrixFeePendingRebaseStore(Protocol):
    """Persistence operations required by the pending rebase service."""

    def upsert_current(
        self, snapshot: MatrixFeePendingRebaseSnapshot
    ) -> MatrixFeePendingRebaseSnapshot:
        """Create or replace the current pending rebase."""

    def delete_by_matrix_draft(self, project_matrix_draft_id: str) -> int:
        """Delete pending rebase rows for one Matrix draft."""


class MatrixFeePendingRebaseDraftStore(Protocol):
    """Draft lookup used for write-before-save race guards."""

    def get(self, project_matrix_draft_id: str) -> ProjectMatrixDraftSnapshot | None:
        """Return current Matrix draft snapshot, if it still exists."""


class MatrixFeePendingRebaseBuilder(Protocol):
    """Build TASK_315A rebase output for one saved Matrix autosave."""

    def build_and_rebase(
        self, command: RebaseAfterMatrixAutosaveCommand
    ) -> MatrixFeeRebaseResult:
        """Return a pure Matrix-to-Fee rebase result."""


class MatrixFeePendingRebaseService:
    """Persist pending Fee rebase output produced after Matrix autosave."""

    def __init__(
        self,
        *,
        draft_store: MatrixFeePendingRebaseDraftStore,
        pending_store: MatrixFeePendingRebaseStore,
        rebase_builder: MatrixFeePendingRebaseBuilder,
        draft_signature_builder: Callable[[ProjectMatrixDraftSnapshot], str],
    ) -> None:
        self._draft_store = draft_store
        self._pending_store = pending_store
        self._rebase_builder = rebase_builder
        self._draft_signature_builder = draft_signature_builder

    def rebase_after_matrix_autosave(
        self,
        command: RebaseAfterMatrixAutosaveCommand,
    ) -> MatrixFeePendingRebaseResult:
        """Run best-effort pending rebase and never fail Matrix autosave."""
        if not _has_required_context(command):
            return MatrixFeePendingRebaseResult(status="not_required")
        assert command.saved_matrix_draft is not None
        if not _draft_matches_active_matrix(command.saved_matrix_draft, command):
            return MatrixFeePendingRebaseResult(status="not_required")
        try:
            rebase_result = self._rebase_builder.build_and_rebase(command)
            current_draft = self._draft_store.get(
                command.saved_matrix_draft.record.project_matrix_draft_id
            )
            if current_draft is None:
                return MatrixFeePendingRebaseResult(status="not_required")
            if not _draft_matches_active_matrix(current_draft, command):
                return MatrixFeePendingRebaseResult(status="not_required")
            current_signature = self._draft_signature_builder(current_draft)
            if current_signature != command.saved_payload_signature:
                return MatrixFeePendingRebaseResult(status="not_required")

            now = datetime.now(timezone.utc).isoformat()
            snapshot = MatrixFeePendingRebaseSnapshot(
                pending_rebase_id=uuid4().hex,
                project_id=command.project_id,
                project_matrix_draft_id=(
                    command.saved_matrix_draft.record.project_matrix_draft_id
                ),
                base_confirmed_matrix_id=str(command.active_confirmed_matrix_id),
                base_confirmed_revision=int(command.active_confirmed_revision or 0),
                fee_rule_version_id=command.fee_rule_version_id,
                matrix_draft_payload_signature=str(command.saved_payload_signature),
                generation=command.generation or _time_generation(),
                payload_json=pending_rebase_payload_to_json(rebase_result),
                created_at=now,
                updated_at=now,
            )
            saved = self._pending_store.upsert_current(snapshot)
            if (
                saved.pending_rebase_id != snapshot.pending_rebase_id
                or saved.generation != snapshot.generation
            ):
                return MatrixFeePendingRebaseResult(status="not_required")
            return MatrixFeePendingRebaseResult(
                status="current",
                summary=rebase_result.summary,
            )
        except Exception as exc:  # noqa: BLE001 - non-fatal lifecycle boundary.
            return MatrixFeePendingRebaseResult(
                status="failed",
                error=f"Fee rebase failed after Matrix autosave: {exc}",
            )

    def delete_for_matrix_draft(
        self,
        command: DeletePendingRebaseForMatrixDraftCommand,
    ) -> MatrixFeePendingRebaseDeleteResult:
        """Delete pending rebases for a Matrix draft."""
        deleted = self._pending_store.delete_by_matrix_draft(
            command.project_matrix_draft_id
        )
        return MatrixFeePendingRebaseDeleteResult(deleted_count=deleted)


class DefaultMatrixFeePendingRebaseBuilder:
    """Build TASK_315A inputs from current Fee context and saved Matrix draft."""

    def __init__(
        self,
        *,
        basic_fill_service: ConfirmedMatrixFeeTemplateBasicFillService,
        pricing_draft_store: FeeEvaluationPricingDraftStore,
        rebase_service: MatrixFeeDraftRebaseService | None = None,
    ) -> None:
        self._basic_fill_service = basic_fill_service
        self._pricing_draft_store = pricing_draft_store
        self._rebase = rebase_service or MatrixFeeDraftRebaseService()

    def build_and_rebase(
        self, command: RebaseAfterMatrixAutosaveCommand
    ) -> MatrixFeeRebaseResult:
        if command.saved_matrix_draft is None:
            raise ValueError("Saved Matrix draft is required for pending rebase.")
        basic_fill = self._basic_fill_service.build(
            BuildMatrixBasicFeeTemplateCommand(project_id=command.project_id)
        )
        if (
            basic_fill.header.confirmed_matrix_id != command.active_confirmed_matrix_id
            or basic_fill.header.confirmed_revision != command.active_confirmed_revision
        ):
            raise ValueError("Active Matrix changed before pending Fee rebase.")
        pricing_draft = self._pricing_draft_store.get_by_context(
            project_id=command.project_id,
            confirmed_matrix_id=basic_fill.header.confirmed_matrix_id,
            confirmed_revision=basic_fill.header.confirmed_revision,
            fee_rule_version_id=command.fee_rule_version_id,
        )
        source_values = pricing_draft.edited_values if pricing_draft is not None else None
        return self._rebase.rebase(
            source_rows=(
                _source_rows_from_basic_fill(
                    basic_fill.groups,
                    source_values=source_values,
                )
                if source_values is not None
                else ()
            ),
            target_rows=_target_rows_from_matrix_draft(command.saved_matrix_draft),
            source_manual_rows=source_values.manual_rows if source_values is not None else (),
            target_groups=_target_groups_from_matrix_draft(command.saved_matrix_draft),
        )


def _source_rows_from_basic_fill(
    groups,
    *,
    source_values: FeeEvaluationEditedExportValues | None,
) -> tuple[MatrixFeeRebaseSourceRow, ...]:
    edited_by_identity = (
        {edited_row_identity(row): row for row in source_values.rows}
        if source_values is not None
        else {}
    )
    rows: list[MatrixFeeRebaseSourceRow] = []
    for group in groups:
        for line in group.lines:
            default_row = _default_row_from_basic_fill_line(line)
            rows.append(
                MatrixFeeRebaseSourceRow(
                    lineage=MatrixFeeRebaseLineage(
                        group_key=group.group_key,
                        group_label=group.group_label,
                        confirmed_group_id=line.confirmed_group_id,
                        confirmed_row_id=line.confirmed_row_id,
                        source_row_snapshot_id=line.source_row_id,
                        draft_row_id=None,
                        step_token=line.step_tokens[0] if line.step_tokens else "",
                        step_index=line.step_index,
                        test_item=line.test_item,
                    ),
                    edited_row=edited_by_identity.get(
                        edited_row_identity(default_row),
                        default_row,
                    ),
                )
            )
    return tuple(rows)


def _target_groups_from_matrix_draft(
    draft: ProjectMatrixDraftSnapshot,
) -> tuple[MatrixFeeRebaseTargetGroup, ...]:
    return tuple(
        MatrixFeeRebaseTargetGroup(
            confirmed_group_id=group.draft_group_id,
            group_key=group.group_key,
            group_label=group.group_label,
        )
        for group in sorted(draft.groups, key=lambda item: item.group_order)
        if group.is_selected
    )


def _target_rows_from_matrix_draft(
    draft: ProjectMatrixDraftSnapshot,
) -> tuple[MatrixFeeRebaseTargetRow, ...]:
    selected_groups = {
        group.draft_group_id: group
        for group in draft.groups
        if group.is_selected
    }
    rows_by_id = {row.draft_row_id: row for row in draft.rows if not row.is_sample_row}
    target_rows: list[MatrixFeeRebaseTargetRow] = []
    for cell in sorted(draft.cells, key=lambda item: item.draft_cell_id):
        group = selected_groups.get(cell.draft_group_id)
        row = rows_by_id.get(cell.draft_row_id)
        if group is None or row is None:
            continue
        parsed_tokens, _warnings = parse_step_tokens(cell.cell_value)
        tokens = tuple(token.raw_token for token in parsed_tokens)
        if not tokens:
            continue
        for step_index, step_token in enumerate(tokens):
            lineage = MatrixFeeRebaseLineage(
                group_key=group.group_key,
                group_label=group.group_label,
                confirmed_group_id=group.draft_group_id,
                confirmed_row_id=row.draft_row_id,
                source_row_snapshot_id=row.source_row_snapshot_id,
                draft_row_id=row.draft_row_id,
                step_token=step_token,
                step_index=step_index,
                test_item=row.test_item,
                source_section=row.source_section,
                method=row.method,
                condition=row.condition,
                requirement=row.requirement,
            )
            target_rows.append(
                MatrixFeeRebaseTargetRow(
                    lineage=lineage,
                    default_row=_default_row_from_target_lineage(lineage),
                )
            )
    return tuple(target_rows)


def _default_row_from_basic_fill_line(line: MatrixBasicFillLine) -> FeeEvaluationEditedExportRow:
    return FeeEvaluationEditedExportRow(
        source_line_id=line.line_id,
        confirmed_group_id=line.confirmed_group_id,
        confirmed_row_id=line.confirmed_row_id,
        step_token=line.step_tokens[0] if line.step_tokens else "",
        step_index=line.step_index,
        spend_time="0",
        unit_price="0",
        unit_type="Pending",
        units="1",
        base_fee="0",
        discount="0%",
        testing_fee="0",
        notes="",
    )


def _default_row_from_target_lineage(
    lineage: MatrixFeeRebaseLineage,
) -> FeeEvaluationEditedExportRow:
    return FeeEvaluationEditedExportRow(
        source_line_id=(
            f"{lineage.confirmed_group_id}:{lineage.confirmed_row_id}:"
            f"{lineage.step_token}:{lineage.step_index}"
        ),
        confirmed_group_id=lineage.confirmed_group_id,
        confirmed_row_id=lineage.confirmed_row_id,
        step_token=lineage.step_token,
        step_index=lineage.step_index,
        spend_time="0",
        unit_price="0",
        unit_type="Pending",
        units="1",
        base_fee="0",
        discount="0%",
        testing_fee="0",
        notes="",
    )


def pending_rebase_payload_to_json(result: MatrixFeeRebaseResult) -> str:
    """Serialize a pending rebase result as self-contained JSON."""
    payload = {
        "active_rows": [_row_to_dict(row) for row in result.active_rows],
        "inactive_removed_rows": [
            _inactive_removed_row_to_dict(row)
            for row in result.inactive_removed_rows
        ],
        "manual_rows": [_manual_row_to_dict(row) for row in result.manual_rows],
        "summary": {
            "preserved_count": result.summary.preserved_count,
            "added_count": result.summary.added_count,
            "removed_count": result.summary.removed_count,
            "preserved_manual_count": result.summary.preserved_manual_count,
            "removed_manual_count": result.summary.removed_manual_count,
        },
        "warnings": list(result.warnings),
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def pending_rebase_payload_from_json(payload_json: str) -> MatrixFeeRebaseResult:
    """Deserialize one persisted pending Matrix-to-Fee rebase payload."""
    payload = json.loads(payload_json)
    summary = payload.get("summary") or {}
    return MatrixFeeRebaseResult(
        active_rows=tuple(_row_from_dict(row) for row in payload.get("active_rows", [])),
        inactive_removed_rows=tuple(
            _inactive_removed_row_from_dict(row)
            for row in payload.get("inactive_removed_rows", [])
        ),
        manual_rows=tuple(
            _manual_row_from_dict(row) for row in payload.get("manual_rows", [])
        ),
        summary=MatrixFeeRebaseSummary(
            preserved_count=int(summary.get("preserved_count", 0)),
            added_count=int(summary.get("added_count", 0)),
            removed_count=int(summary.get("removed_count", 0)),
            preserved_manual_count=int(summary.get("preserved_manual_count", 0)),
            removed_manual_count=int(summary.get("removed_manual_count", 0)),
        ),
        warnings=tuple(str(item) for item in payload.get("warnings", [])),
    )


def _has_required_context(command: RebaseAfterMatrixAutosaveCommand) -> bool:
    return (
        command.saved_matrix_draft is not None
        and bool(command.saved_payload_signature)
        and bool(command.active_confirmed_matrix_id)
        and command.active_confirmed_revision is not None
        and bool(command.fee_rule_version_id)
    )


def _draft_matches_active_matrix(
    draft: ProjectMatrixDraftSnapshot,
    command: RebaseAfterMatrixAutosaveCommand,
) -> bool:
    return draft.record.base_confirmed_matrix_id == command.active_confirmed_matrix_id


def _time_generation() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1_000_000)


def _row_to_dict(row: FeeEvaluationEditedExportRow) -> dict[str, object]:
    return {
        "source_line_id": row.source_line_id,
        "confirmed_group_id": row.confirmed_group_id,
        "confirmed_row_id": row.confirmed_row_id,
        "step_token": row.step_token,
        "step_index": row.step_index,
        "spend_time": row.spend_time,
        "unit_price": row.unit_price,
        "unit_type": row.unit_type,
        "units": row.units,
        "base_fee": row.base_fee,
        "discount": row.discount,
        "testing_fee": row.testing_fee,
        "notes": row.notes,
    }


def _manual_row_to_dict(row: FeeEvaluationEditedManualRow) -> dict[str, object]:
    return {
        "row_kind": row.row_kind,
        "spend_time": row.spend_time,
        "unit_price": row.unit_price,
        "unit_type": row.unit_type,
        "units": row.units,
        "base_fee": row.base_fee,
        "discount": row.discount,
        "testing_fee": row.testing_fee,
        "notes": row.notes,
        "confirmed_group_id": row.confirmed_group_id,
        "group_key": row.group_key,
        "group_label": row.group_label,
    }


def _inactive_removed_row_to_dict(
    row: MatrixFeeInactiveRemovedRow,
) -> dict[str, object]:
    return {
        "previous_row": _row_to_dict(row.previous_row),
        "previous_group_key": row.previous_group_key,
        "previous_group_label": row.previous_group_label,
        "previous_row_signature": row.previous_row_signature,
        "inactive_reason": row.inactive_reason,
    }


def _row_from_dict(payload: dict[str, object]) -> FeeEvaluationEditedExportRow:
    return FeeEvaluationEditedExportRow(
        source_line_id=str(payload.get("source_line_id", "")),
        confirmed_group_id=str(payload.get("confirmed_group_id", "")),
        confirmed_row_id=str(payload.get("confirmed_row_id", "")),
        step_token=str(payload.get("step_token", "")),
        step_index=int(payload.get("step_index", 0)),
        spend_time=str(payload.get("spend_time", "")),
        unit_price=str(payload.get("unit_price", "")),
        unit_type=str(payload.get("unit_type", "")),
        units=str(payload.get("units", "")),
        base_fee=str(payload.get("base_fee", "")),
        discount=str(payload.get("discount", "")),
        testing_fee=str(payload.get("testing_fee", "")),
        notes=str(payload.get("notes", "")),
    )


def _manual_row_from_dict(payload: dict[str, object]) -> FeeEvaluationEditedManualRow:
    return FeeEvaluationEditedManualRow(
        row_kind=str(payload.get("row_kind", "")),
        spend_time=str(payload.get("spend_time", "")),
        unit_price=str(payload.get("unit_price", "")),
        unit_type=str(payload.get("unit_type", "")),
        units=str(payload.get("units", "")),
        base_fee=str(payload.get("base_fee", "")),
        discount=str(payload.get("discount", "")),
        testing_fee=str(payload.get("testing_fee", "")),
        notes=str(payload.get("notes", "")),
        confirmed_group_id=str(payload.get("confirmed_group_id", "")),
        group_key=str(payload.get("group_key", "")),
        group_label=str(payload.get("group_label", "")),
    )


def _inactive_removed_row_from_dict(
    payload: dict[str, object],
) -> MatrixFeeInactiveRemovedRow:
    previous = payload.get("previous_row")
    if not isinstance(previous, dict):
        previous = {}
    return MatrixFeeInactiveRemovedRow(
        previous_row=_row_from_dict(previous),
        previous_group_key=str(payload.get("previous_group_key", "")),
        previous_group_label=str(payload.get("previous_group_label", "")),
        previous_row_signature=str(payload.get("previous_row_signature", "")),
        inactive_reason=str(payload.get("inactive_reason", "removed_from_matrix")),
    )
