"""V2 attestation, reviewed merge, and CAS guards for duration defaults."""

from __future__ import annotations

from dataclasses import replace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.application.confirmed_matrix_fee_draft_models import (
    BuildConfirmedMatrixFeeDraftCommand,
)
from backend.application.confirmed_matrix_fee_draft_service import (
    ConfirmedMatrixFeeDraftService,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftConflictError,
    FeeEvaluationPricingDraftPersistenceService,
    SaveFeeEvaluationPricingDraftCommand,
)
from backend.application.fee_evaluation_pricing_draft_v2_contract import (
    decode_pricing_draft_payload,
)
from backend.application.fee_evaluation_pricing_draft_v2_rebase import (
    rebase_reviewed_values,
)
from backend.application.matrix_fee_rebase_promotion_values import (
    edited_values_from_fee_draft,
)
from backend.infrastructure.storage.database import Base
from backend.infrastructure.storage.repositories.fee_evaluation_pricing_draft_edit import (
    FeeEvaluationPricingDraftEditRepository,
)
from tests.integration.test_confirmed_matrix_fee_draft_dependent_fields_api import (
    _Store,
    _snapshot,
)


def test_duration_defaults_are_attested_and_reviewed_merge_preserves_manual_fields(
    tmp_path,
) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'duration-v2.sqlite3'}", future=True)
    Base.metadata.create_all(engine)
    store = _Store(_snapshot(include_second_authority=True))
    provider = _AuthorityProvider(ConfirmedMatrixFeeDraftService(confirmed_store=store))

    with Session(engine) as session:
        service = _service(session, provider)
        defaults = edited_values_from_fee_draft(
            provider.service.build_draft(
                BuildConfirmedMatrixFeeDraftCommand(project_id="P1")
            )
        )
        first_row = defaults.rows[0]
        edited = replace(
            defaults,
            rows=(
                replace(
                    first_row,
                    unit_price="99",
                    unit_type="operator unit",
                    discount="15%",
                    notes="operator note",
                ),
                *defaults.rows[1:],
            ),
        )
        saved = service.save(
            SaveFeeEvaluationPricingDraftCommand(
                project_id="P1",
                edited_values=edited,
            )
        ).saved_snapshot
        assert saved is not None
        session.commit()

    decoded = decode_pricing_draft_payload(saved.payload_json or "")
    assert decoded.automatic_defaults_attestation is not None
    assert all(
        row.safe_for_rebase
        for row in decoded.automatic_defaults_attestation.row_safety
    )

    current_snapshot = store.snapshot
    changed_authority = replace(
        current_snapshot.duration_authorities[0],
        duration_value=current_snapshot.duration_authorities[0].duration_value * 2,
        normalized_hours=current_snapshot.duration_authorities[0].normalized_hours * 2,
        source_fingerprint="source-g1-current",
        lineage_fingerprint="lineage-g1-current",
        authority_revision="2",
    )
    store.snapshot = replace(
        current_snapshot,
        duration_authorities=(
            changed_authority,
            *current_snapshot.duration_authorities[1:],
        ),
    )
    current_defaults = edited_values_from_fee_draft(
        provider.service.build_draft(
            BuildConfirmedMatrixFeeDraftCommand(project_id="P1")
        )
    )
    rebased = rebase_reviewed_values(
        saved=saved.edited_values,
        current_defaults=current_defaults,
        row_provenance={
            first_row.source_line_id: (
                "unit_price",
                "unit_type",
                "discount",
                "notes",
            )
        },
    )
    row = rebased.rows[0]
    assert (row.units, row.testing_fee) == (
        current_defaults.rows[0].units,
        current_defaults.rows[0].testing_fee,
    )
    assert (row.unit_price, row.unit_type, row.discount, row.notes) == (
        "99",
        "operator unit",
        "15%",
        "operator note",
    )


def test_stale_v2_cas_rejects_without_overwriting_duration_draft(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'duration-cas.sqlite3'}", future=True)
    Base.metadata.create_all(engine)
    provider = _AuthorityProvider(
        ConfirmedMatrixFeeDraftService(
            confirmed_store=_Store(_snapshot(include_second_authority=True))
        )
    )
    with Session(engine) as session:
        service = _service(session, provider)
        defaults = edited_values_from_fee_draft(
            provider.service.build_draft(
                BuildConfirmedMatrixFeeDraftCommand(project_id="P1")
            )
        )
        first = service.save(
            SaveFeeEvaluationPricingDraftCommand(
                project_id="P1",
                edited_values=defaults,
            )
        ).saved_snapshot
        assert first is not None
        second = service.save(
            SaveFeeEvaluationPricingDraftCommand(
                project_id="P1",
                edited_values=replace(
                    defaults,
                    rows=(replace(defaults.rows[0], notes="new"), *defaults.rows[1:]),
                ),
                expected_pricing_draft_edit_id=first.draft_edit_id,
                expected_generation=first.generation,
                expected_payload_fingerprint=first.payload_fingerprint,
                expected_updated_at=first.updated_at,
            )
        ).saved_snapshot
        assert second is not None
        session.commit()

    with Session(engine) as session:
        service = _service(session, provider)
        with pytest.raises(FeeEvaluationPricingDraftConflictError):
            service.save(
                SaveFeeEvaluationPricingDraftCommand(
                    project_id="P1",
                    edited_values=defaults,
                    expected_pricing_draft_edit_id=first.draft_edit_id,
                    expected_generation=first.generation,
                    expected_payload_fingerprint=first.payload_fingerprint,
                    expected_updated_at=first.updated_at,
                )
            )
        reloaded = service.load("P1")

    assert reloaded.status == "current_v2"
    assert reloaded.saved_snapshot is not None
    assert reloaded.saved_snapshot.generation == second.generation
    assert reloaded.saved_snapshot.edited_values.rows[0].notes == "new"


class _AuthorityProvider:
    def __init__(self, service: ConfirmedMatrixFeeDraftService) -> None:
        self.service = service

    def build_authority_result(self, command):
        return self.service.build_authority_result(command)


class _ForbiddenBasicFill:
    def build(self, command):
        raise AssertionError("single authority build must provide Matrix basic-fill")


def _service(
    session: Session,
    provider: _AuthorityProvider,
) -> FeeEvaluationPricingDraftPersistenceService:
    return FeeEvaluationPricingDraftPersistenceService(
        basic_fill_service=_ForbiddenBasicFill(),
        draft_store=FeeEvaluationPricingDraftEditRepository(session),
        automatic_defaults_provider=provider,
    )
