from __future__ import annotations

from dataclasses import replace

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.application.confirmed_matrix_fee_draft_models import (
    BuildConfirmedMatrixFeeDraftCommand,
)
from backend.application.confirmed_matrix_fee_draft_service import (
    ConfirmedMatrixFeeDraftService,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftPersistenceService,
    SaveFeeEvaluationPricingDraftCommand,
)
from backend.application.fee_evaluation_pricing_draft_automatic_build import (
    build_current_pricing_defaults,
)
from backend.application.fee_evaluation_pricing_draft_v2_contract import (
    decode_pricing_draft_payload,
)
from backend.application.matrix_fee_rebase_promotion_values import (
    edited_values_from_fee_draft,
)
from backend.infrastructure.storage.database import Base
from backend.infrastructure.storage.repositories.fee_evaluation_pricing_draft_edit import (
    FeeEvaluationPricingDraftEditRepository,
)
from tests.unit.test_confirmed_matrix_fee_cr_specified_current_authority import (
    _Store,
    _target,
    _two_group_plan,
    _two_group_snapshot,
)


def test_changed_cr_authority_runs_attested_reviewed_rebase_and_current_v2_reload(
    tmp_path,
) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'cr-pricing-draft.sqlite3'}", future=True)
    Base.metadata.create_all(engine)
    snapshot = _two_group_snapshot()
    adapter = _MutablePlanAdapter(_plan(revision=1, second_readings="8"))
    provider = _AuthorityProvider(
        ConfirmedMatrixFeeDraftService(
            confirmed_store=_Store(snapshot),
            contact_measurement_adapter=adapter,
        )
    )

    with Session(engine) as session:
        service = _persistence_service(session, provider)
        old_draft = provider.service.build_draft(
            BuildConfirmedMatrixFeeDraftCommand(project_id="p1")
        )
        old_defaults = edited_values_from_fee_draft(old_draft)
        old_group_two = _group_row(old_defaults, "g2")
        edited = replace(
            old_defaults,
            rows=tuple(
                replace(row, unit_price="99", discount="15%", notes="operator note")
                if row is old_group_two
                else row
                for row in old_defaults.rows
            ),
        )
        saved = service.save(
            SaveFeeEvaluationPricingDraftCommand(project_id="p1", edited_values=edited)
        ).saved_snapshot
        assert saved is not None
        assert saved.generation == 1
        assert decode_pricing_draft_payload(
            saved.payload_json or ""
        ).automatic_defaults_attestation is not None
        session.commit()

    adapter.plan = _plan(revision=2, second_readings="12")
    with Session(engine) as session:
        service = _persistence_service(session, provider)
        decoded = decode_pricing_draft_payload(saved.payload_json or "")
        current_build = build_current_pricing_defaults("p1", provider)
        assert decoded.automatic_defaults_attestation is not None
        assert all(
            row.safe_for_rebase
            for row in decoded.automatic_defaults_attestation.row_safety
        ), decoded.automatic_defaults_attestation.row_safety
        assert all(row.safe_for_rebase for row in current_build.row_safety), (
            current_build.row_safety
        )
        assert (
            decoded.automatic_defaults_attestation.ordered_row_identities
            == current_build.ordered_row_identities
        )
        before = _repository(session).get_by_context(
            project_id="p1",
            confirmed_matrix_id="m1",
            confirmed_revision=1,
            fee_rule_version_id=saved.fee_rule_version_id,
        )
        candidate = service.load("p1")
        after_load = _repository(session).get_by_context(
            project_id="p1",
            confirmed_matrix_id="m1",
            confirmed_revision=1,
            fee_rule_version_id=saved.fee_rule_version_id,
        )

        assert candidate.status == "rebase_required"
        assert candidate.saved_snapshot is not None
        assert before is not None and after_load is not None
        assert after_load.payload_json == before.payload_json
        assert after_load.generation == 1
        reviewed_row = _group_row(candidate.saved_snapshot.edited_values, "g2")
        assert (reviewed_row.units, reviewed_row.testing_fee) == ("36", "180")
        assert (reviewed_row.unit_price, reviewed_row.discount) == ("99", "15%")

        reviewed = service.save(
            SaveFeeEvaluationPricingDraftCommand(
                project_id="p1",
                edited_values=candidate.saved_snapshot.edited_values,
                expected_pricing_draft_edit_id=saved.draft_edit_id,
                expected_generation=saved.generation,
                expected_payload_fingerprint=saved.payload_fingerprint,
                expected_updated_at=saved.updated_at,
            )
        )
        assert reviewed.status == "current_v2"
        assert reviewed.saved_snapshot is not None
        assert reviewed.saved_snapshot.generation == 2
        session.commit()

    with Session(engine) as session:
        reloaded = _persistence_service(session, provider).load("p1")

    assert reloaded.status == "current_v2"
    assert reloaded.saved_snapshot is not None
    assert reloaded.saved_snapshot.source_context is not None
    assert reloaded.saved_snapshot.source_context.measurement_plan_revision_id == "cr-rev-2"
    final_row = _group_row(reloaded.saved_snapshot.edited_values, "g2")
    assert (final_row.units, final_row.testing_fee) == ("36", "180")
    assert (final_row.unit_price, final_row.discount) == ("99", "15%")


def test_unsafe_current_cr_target_blocks_without_persistence_write(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'unsafe-cr-draft.sqlite3'}", future=True)
    Base.metadata.create_all(engine)
    snapshot = _two_group_snapshot()
    adapter = _MutablePlanAdapter(_plan(revision=1, second_readings="8"))
    provider = _AuthorityProvider(
        ConfirmedMatrixFeeDraftService(
            confirmed_store=_Store(snapshot),
            contact_measurement_adapter=adapter,
        )
    )
    with Session(engine) as session:
        service = _persistence_service(session, provider)
        defaults = edited_values_from_fee_draft(
            provider.service.build_draft(
                BuildConfirmedMatrixFeeDraftCommand(project_id="p1")
            )
        )
        saved = service.save(
            SaveFeeEvaluationPricingDraftCommand(project_id="p1", edited_values=defaults)
        ).saved_snapshot
        assert saved is not None
        session.commit()

    adapter.plan = replace(_plan(revision=2, second_readings="12"), targets=())
    with Session(engine) as session:
        service = _persistence_service(session, provider)
        before = _repository(session).get_by_context(
            project_id="p1",
            confirmed_matrix_id="m1",
            confirmed_revision=1,
            fee_rule_version_id=saved.fee_rule_version_id,
        )
        result = service.load("p1")
        after = _repository(session).get_by_context(
            project_id="p1",
            confirmed_matrix_id="m1",
            confirmed_revision=1,
            fee_rule_version_id=saved.fee_rule_version_id,
        )

    assert result.status == "blocked"
    assert result.saved_snapshot is None
    assert before is not None and after is not None
    assert (after.generation, after.payload_json) == (before.generation, before.payload_json)


class _MutablePlanAdapter:
    def __init__(self, plan) -> None:
        self.plan = plan

    def get_effective(self, project_id: str):
        assert project_id == "p1"
        return self.plan


class _AuthorityProvider:
    def __init__(self, service: ConfirmedMatrixFeeDraftService) -> None:
        self.service = service

    def build_authority_result(self, command):
        return self.service.build_authority_result(command)


class _ForbiddenBasicFill:
    def build(self, command):
        raise AssertionError("single authority build must supply Matrix basic-fill")


def _persistence_service(session: Session, provider: _AuthorityProvider):
    return FeeEvaluationPricingDraftPersistenceService(
        basic_fill_service=_ForbiddenBasicFill(),
        draft_store=_repository(session),
        automatic_defaults_provider=provider,
    )


def _repository(session: Session) -> FeeEvaluationPricingDraftEditRepository:
    return FeeEvaluationPricingDraftEditRepository(session)


def _plan(*, revision: int, second_readings: str):
    plan = _two_group_plan()
    return replace(
        plan,
        revision_id=f"cr-rev-{revision}",
        revision_sequence=revision,
        targets=(
            _target("g1", "r1", "8"),
            _target("g2", "r2", second_readings),
        ),
    )


def _group_row(values, group_id: str):
    return next(row for row in values.rows if row.confirmed_group_id == group_id)
