from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.application.confirmed_matrix_fee_draft_models import (
    BuildConfirmedMatrixFeeDraftCommand,
)
from backend.application.confirmed_matrix_fee_draft_service import (
    ConfirmedMatrixFeeDraftService,
)
from backend.application.contact_point_profile_confirmed_consumer_adapter import (
    EffectiveConfirmedPointProfile,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftConflictError,
    FeeEvaluationPricingDraftPersistenceService,
    SaveFeeEvaluationPricingDraftCommand,
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
from tests.unit.test_fee_pricing_draft_automatic_build_safety import (
    _authority_result as _cr_authority_result,
    _cr_line,
    _snapshot as _cr_snapshot,
)
from tests.unit.test_fee_evaluation_pricing_draft_persistence_service import (
    _ConfirmedStore,
    _DraftStore,
    _snapshot,
)
from tests.unit.test_confirmed_matrix_fee_cr_specified_current_authority import (
    _Store as _ConfirmedCrStore,
    _two_group_snapshot,
)


def test_explicit_save_persists_attestation_from_one_authority_build() -> None:
    provider, values = _provider_and_values()
    store = _DraftStore()
    service = FeeEvaluationPricingDraftPersistenceService(
        basic_fill_service=_ForbiddenBasicFill(),
        draft_store=store,
        automatic_defaults_provider=provider,
        point_profile_provider=_ForbiddenProvider(),
        measurement_plan_provider=_ForbiddenProvider(),
    )

    result = service.save(
        SaveFeeEvaluationPricingDraftCommand(project_id="P1", edited_values=values)
    )

    assert result.status == "current_v2"
    assert provider.calls == 1
    assert result.saved_snapshot is not None
    decoded = decode_pricing_draft_payload(result.saved_snapshot.payload_json or "")
    assert decoded.automatic_defaults_attestation is not None
    assert decoded.automatic_defaults_attestation.attested_generation == 1


def test_load_revalidates_current_v2_with_one_authority_build() -> None:
    provider, values = _provider_and_values()
    store = _DraftStore()
    service = FeeEvaluationPricingDraftPersistenceService(
        basic_fill_service=_ForbiddenBasicFill(),
        draft_store=store,
        automatic_defaults_provider=provider,
        point_profile_provider=_ForbiddenProvider(),
        measurement_plan_provider=_ForbiddenProvider(),
    )
    service.save(SaveFeeEvaluationPricingDraftCommand(project_id="P1", edited_values=values))
    provider.calls = 0

    result = service.load("P1")

    assert result.status == "current_v2"
    assert provider.calls == 1
    assert result.saved_snapshot is not None


def test_changed_cr_plan_rebases_and_reviewed_save_becomes_current_v2() -> None:
    prior = _cr_build(plan_id="plan-1", revision=1, units="40", testing_fee="400")
    current = _cr_build(plan_id="plan-2", revision=2, units="36", testing_fee="180")
    provider = _MutableProvider(prior)
    store = _DraftStore()
    service = FeeEvaluationPricingDraftPersistenceService(
        basic_fill_service=_ForbiddenBasicFill(),
        draft_store=store,
        automatic_defaults_provider=provider,
    )
    defaults = edited_values_from_fee_draft(prior.draft)
    edited = replace(
        defaults,
        rows=(replace(defaults.rows[0], unit_price="12", discount="5%"),),
    )
    saved = service.save(
        SaveFeeEvaluationPricingDraftCommand(project_id="P1", edited_values=edited)
    ).saved_snapshot
    assert saved is not None
    provider.result = current
    provider.calls = 0

    candidate = service.load("P1")

    assert candidate.status == "rebase_required"
    assert provider.calls == 1
    assert candidate.saved_snapshot is not None
    row = candidate.saved_snapshot.edited_values.rows[0]
    assert (row.units, row.testing_fee) == ("36", "180")
    assert (row.unit_price, row.discount) == ("12", "5%")

    reviewed = service.save(
        SaveFeeEvaluationPricingDraftCommand(
            project_id="P1",
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
    assert reviewed.saved_snapshot.source_context.measurement_plan_revision_id == "plan-2"


def test_changed_point_profile_cr_coverage_rebases_fee_units() -> None:
    profile = _confirmed_profile(cr_readings="4", fingerprint="profile-fp-1")
    profile_adapter = _MutableProfileAdapter(profile)
    provider = _CountingProvider(
        ConfirmedMatrixFeeDraftService(
            confirmed_store=_ConfirmedCrStore(_two_group_snapshot()),
            contact_point_profile_adapter=profile_adapter,
        )
    )
    store = _DraftStore()
    persistence = FeeEvaluationPricingDraftPersistenceService(
        basic_fill_service=_ForbiddenBasicFill(),
        draft_store=store,
        automatic_defaults_provider=provider,
    )
    prior_values = edited_values_from_fee_draft(
        provider.service.build_draft(
            BuildConfirmedMatrixFeeDraftCommand(project_id="p1")
        )
    )
    saved = persistence.save(
        SaveFeeEvaluationPricingDraftCommand(
            project_id="p1",
            edited_values=prior_values,
        )
    ).saved_snapshot
    assert saved is not None
    profile_adapter.profile = _confirmed_profile(
        cr_readings="6",
        fingerprint="profile-fp-2",
    )

    candidate = persistence.load("p1")

    assert candidate.status == "rebase_required"
    assert candidate.saved_snapshot is not None
    assert [row.units for row in candidate.saved_snapshot.edited_values.rows] == [
        "30",
        "18",
    ]
    reviewed = persistence.save(
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
    assert reviewed.saved_snapshot.source_context is not None
    assert reviewed.saved_snapshot.source_context.point_profile_fingerprint == "profile-fp-2"


def test_reviewed_save_stale_cas_is_typed_and_does_not_overwrite(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'pricing-draft.sqlite3'}", future=True)
    Base.metadata.create_all(engine)
    prior = _cr_build(plan_id="plan-1", revision=1, units="40", testing_fee="400")
    current = _cr_build(plan_id="plan-2", revision=2, units="36", testing_fee="180")
    provider = _MutableProvider(prior)
    with Session(engine) as session:
        service = _repository_service(session, provider)
        defaults = edited_values_from_fee_draft(prior.draft)
        saved = service.save(
            SaveFeeEvaluationPricingDraftCommand(project_id="P1", edited_values=defaults)
        ).saved_snapshot
        assert saved is not None
        session.commit()

    provider.result = current
    with Session(engine) as winner_session, Session(engine) as stale_session:
        winner_service = _repository_service(winner_session, provider)
        stale_service = _repository_service(stale_session, provider)
        winner_candidate = winner_service.load("P1")
        stale_candidate = stale_service.load("P1")
        assert winner_candidate.status == stale_candidate.status == "rebase_required"
        assert winner_candidate.saved_snapshot is not None
        assert stale_candidate.saved_snapshot is not None
        winner = winner_service.save(
            _reviewed_command(saved, winner_candidate.saved_snapshot.edited_values)
        ).saved_snapshot
        assert winner is not None
        winner_session.commit()

        with pytest.raises(FeeEvaluationPricingDraftConflictError):
            stale_service.save(
                _reviewed_command(saved, stale_candidate.saved_snapshot.edited_values)
            )
        stale_session.rollback()

    with Session(engine) as verify_session:
        persisted = FeeEvaluationPricingDraftEditRepository(verify_session).get_by_context(
            project_id="P1",
            confirmed_matrix_id="matrix-1",
            confirmed_revision=2,
            fee_rule_version_id="fee_rules_v2026_08_22_r7",
        )
    assert persisted is not None
    assert persisted.generation == 2
    assert persisted.payload_fingerprint == winner.payload_fingerprint


class _CountingProvider:
    def __init__(self, service: ConfirmedMatrixFeeDraftService) -> None:
        self.service = service
        self.calls = 0

    def build_authority_result(self, command):
        self.calls += 1
        return self.service.build_authority_result(command)


class _MutableProvider:
    def __init__(self, result) -> None:
        self.result = result
        self.calls = 0

    def build_authority_result(self, command):
        self.calls += 1
        return self.result


class _MutableProfileAdapter:
    def __init__(self, profile: EffectiveConfirmedPointProfile) -> None:
        self.profile = profile

    def get_effective(self, project_id: str) -> EffectiveConfirmedPointProfile:
        assert project_id == "p1"
        return self.profile


class _ForbiddenBasicFill:
    def build(self, command):
        raise AssertionError("basic-fill service must not reread Confirmed Matrix")


class _ForbiddenProvider:
    def get_effective(self, project_id: str):
        raise AssertionError("compatibility provider must not be reread")


def _provider_and_values():
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(_snapshot())
    )
    values = edited_values_from_fee_draft(
        service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))
    )
    return _CountingProvider(service), values


def _repository_service(session: Session, provider: _MutableProvider):
    return FeeEvaluationPricingDraftPersistenceService(
        basic_fill_service=_ForbiddenBasicFill(),
        draft_store=FeeEvaluationPricingDraftEditRepository(session),
        automatic_defaults_provider=provider,
    )


def _reviewed_command(saved, values):
    return SaveFeeEvaluationPricingDraftCommand(
        project_id="P1",
        edited_values=values,
        expected_pricing_draft_edit_id=saved.draft_edit_id,
        expected_generation=saved.generation,
        expected_payload_fingerprint=saved.payload_fingerprint,
        expected_updated_at=saved.updated_at,
    )


def _confirmed_profile(
    *,
    cr_readings: str,
    fingerprint: str,
) -> EffectiveConfirmedPointProfile:
    return EffectiveConfirmedPointProfile(
        status="confirmed",
        readings_per_sample="9",
        revision_id=f"revision-{fingerprint}",
        revision_sequence=2,
        fingerprint=fingerprint,
        lineage=(
            "Confirmed Project Point Profile: revision 2 "
            f"(revision-{fingerprint}; {fingerprint})"
        ),
        message=None,
        cr_readings_per_sample=cr_readings,
    )


def _cr_build(*, plan_id: str, revision: int, units: str, testing_fee: str):
    snapshot = _cr_snapshot()
    line = replace(
        _cr_line(),
        units=Decimal(units),
        testing_fee=Decimal(testing_fee),
    )
    result = _cr_authority_result(snapshot, line)
    plan = replace(
        result.effective_measurement_plan,
        revision_id=plan_id,
        revision_sequence=revision,
    )
    return replace(
        result,
        rule_library=SimpleNamespace(
            version=SimpleNamespace(version_id="fee_rules_v2026_08_22_r7")
        ),
        effective_measurement_plan=plan,
    )
