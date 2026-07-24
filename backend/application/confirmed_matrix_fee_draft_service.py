"""Build read-only Fee Evaluation drafts from active Confirmed Matrix authority."""

from __future__ import annotations

from decimal import Decimal

from backend.application.confirmed_matrix_fee_draft_models import (
    BuildConfirmedMatrixFeeDraftCommand,
    ConfirmedMatrixAuthorityStore,
    FeeEvaluationDraft,
    FeeEvaluationGroup,
    FeeEvaluationHeader,
    FeeEvaluationLineItem,
    FeeEvaluationWarning,
)
from backend.application.confirmed_matrix_fee_draft_build_result import (
    ConfirmedMatrixFeeAuthorityBuildResult,
)
from backend.application.confirmed_matrix_fee_draft_build_support import (
    draft_status as _draft_status,
    now_iso as _now_iso,
    root_warnings as _root_warnings,
)
from backend.application.confirmed_matrix_fee_manual_defaults import (
    build_report_preparation_line,
)
from backend.application.confirmed_matrix_fee_draft_line_builder import (
    ConfirmedMatrixFeeDraftError,
    build_groups,
)
from backend.application.contact_point_profile_confirmed_consumer_adapter import (
    ContactPointProfileConfirmedConsumerAdapter,
)
from backend.application.contact_measurement_plan_confirmed_consumer_adapter import (
    ContactMeasurementPlanConfirmedConsumerAdapter,
)
from backend.modules.fee_evaluation import FeeRuleLibrary, load_active_fee_rule_library


class ConfirmedMatrixFeeDraftNotFoundError(LookupError):
    """Raised when no active confirmed Matrix authority exists for a project."""


class ConfirmedMatrixFeeDraftService:
    """Build read-only Fee Evaluation drafts from active Confirmed Matrix authority."""

    def __init__(
        self,
        *,
        confirmed_store: ConfirmedMatrixAuthorityStore,
        rule_library: FeeRuleLibrary | None = None,
        contact_measurement_adapter: ContactMeasurementPlanConfirmedConsumerAdapter | None = None,
        contact_point_profile_adapter: ContactPointProfileConfirmedConsumerAdapter | None = None,
    ) -> None:
        self._confirmed = confirmed_store
        self._rule_library = rule_library
        self._contact_measurement_adapter = contact_measurement_adapter
        self._contact_point_profile_adapter = contact_point_profile_adapter

    def build_draft(self, command: BuildConfirmedMatrixFeeDraftCommand) -> FeeEvaluationDraft:
        """Return one Fee Evaluation draft preview for a project."""
        return self.build_authority_result(command).draft

    def build_authority_result(
        self,
        command: BuildConfirmedMatrixFeeDraftCommand,
    ) -> ConfirmedMatrixFeeAuthorityBuildResult:
        """Return the draft and every authority fact read by this build."""
        snapshot = self._confirmed.get_active_by_project(command.project_id)
        if snapshot is None:
            raise ConfirmedMatrixFeeDraftNotFoundError("Active confirmed matrix not found.")
        library = self._rule_library or load_active_fee_rule_library()
        warnings = _root_warnings(snapshot)
        effective_contact_plan = (
            self._contact_measurement_adapter.get_effective(command.project_id)
            if self._contact_measurement_adapter is not None
            else None
        )
        effective_point_profile = (
            self._contact_point_profile_adapter.get_effective(command.project_id)
            if self._contact_point_profile_adapter is not None
            else None
        )
        groups = build_groups(
            snapshot=snapshot,
            library=library,
            effective_contact_plan=effective_contact_plan,
            effective_point_profile=effective_point_profile,
        )
        manual_line_items = (
            build_report_preparation_line(
                snapshot=snapshot,
                rule_version_id=library.version.version_id,
            ),
        )
        line_items = tuple(
            item
            for group in groups
            for item in (*group.manual_line_items, *group.line_items)
        ) + manual_line_items
        review_required_count = sum(1 for item in line_items if item.review_required)
        calculated_values = [item.testing_fee for item in line_items if item.testing_fee is not None]
        total_fee = (
            sum(calculated_values, Decimal("0"))
            if calculated_values and review_required_count == 0 and not warnings
            else None
        )
        draft = FeeEvaluationDraft(
            header=FeeEvaluationHeader(
                project_id=snapshot.version.project_id,
                confirmed_matrix_id=snapshot.version.confirmed_matrix_id,
                confirmed_revision=snapshot.version.confirmed_revision,
                pricing_rule_version_id=library.version.version_id,
                pricing_source_file_name=library.version.source_file_name,
                pricing_source_hash=library.version.source_hash,
                pricing_effective_from=snapshot.version.sample_received_date,
                generated_at=_now_iso(),
            ),
            draft_status=_draft_status(groups, warnings),
            total_fee=total_fee,
            review_required_count=review_required_count + len(warnings),
            groups=groups,
            manual_line_items=manual_line_items,
            warnings=tuple(warnings),
        )
        return ConfirmedMatrixFeeAuthorityBuildResult(
            draft=draft,
            confirmed_matrix=snapshot,
            rule_library=library,
            effective_measurement_plan=effective_contact_plan,
            effective_point_profile=effective_point_profile,
        )
