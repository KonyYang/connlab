from __future__ import annotations

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from backend.domain.confirmed_fee import ConfirmedFeeSummary, ConfirmedFeeVersion
from backend.infrastructure.storage.database import Base
from backend.infrastructure.storage.models import ConfirmedFeeVersionModel
from backend.infrastructure.storage.repositories.confirmed_fee_authority import (
    ConfirmedFeeAuthorityRepository,
)


def test_confirmed_fee_repository_creates_and_lists_versions_by_revision() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        repo = ConfirmedFeeAuthorityRepository(session)

        first = repo.create(_version("cfv-1", revision=1, testing_fee_total="41"))
        second = repo.create(_version("cfv-2", revision=2, testing_fee_total="52"))
        latest = repo.get_latest_by_project("P1")
        versions = repo.list_by_project("P1")
        row_count = len(session.scalars(select(ConfirmedFeeVersionModel)).all())

    assert row_count == 2
    assert versions == (first, second)
    assert latest == second
    assert latest is not None
    assert latest.summary.testing_fee_total == "52"
    assert latest.pricing_snapshot_json == '{"rows":[]}'


def _version(
    confirmed_fee_id: str,
    *,
    revision: int,
    testing_fee_total: str,
) -> ConfirmedFeeVersion:
    return ConfirmedFeeVersion(
        confirmed_fee_id=confirmed_fee_id,
        project_id="P1",
        confirmed_fee_revision=revision,
        confirmed_matrix_id="cmv-1",
        confirmed_revision=1,
        fee_rule_version_id="fee_rules_v2026_06_03",
        pricing_draft_edit_id="fed-1",
        pricing_effective_from=None,
        summary=ConfirmedFeeSummary(
            testing_fee_total=testing_fee_total,
            working_hours="1.5",
            lab_manpower_cost="300",
            external_cost="150",
            grand_cost="191",
        ),
        pricing_snapshot_json='{"rows":[]}',
        confirmed_by="Lab User",
        confirmed_at="2026-06-10T09:00:00+00:00",
        confirmation_note="ready",
    )
