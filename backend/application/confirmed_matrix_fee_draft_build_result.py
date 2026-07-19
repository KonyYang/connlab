"""Private authority facts captured by one confirmed Matrix Fee build."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.application.confirmed_matrix_fee_draft_models import FeeEvaluationDraft
    from backend.application.contact_measurement_plan_confirmed_consumer_adapter import (
        EffectiveContactMeasurementPlan,
    )
    from backend.application.contact_point_profile_confirmed_consumer_adapter import (
        EffectiveConfirmedPointProfile,
    )
    from backend.domain import ConfirmedMatrixSnapshot
    from backend.modules.fee_evaluation import FeeRuleLibrary


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixFeeAuthorityBuildResult:
    """One immutable set of facts read while building a Fee draft."""

    draft: FeeEvaluationDraft
    confirmed_matrix: ConfirmedMatrixSnapshot
    rule_library: FeeRuleLibrary
    effective_measurement_plan: EffectiveContactMeasurementPlan | None
    effective_point_profile: EffectiveConfirmedPointProfile | None
