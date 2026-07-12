"""Integration coverage for TASK_361B authority bootstrap and lifecycle."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.application.contact_measurement_plan_bootstrap_service import (
    ContactMeasurementPlanBootstrapError,
    ContactMeasurementPlanBootstrapService,
)
from backend.application.contact_measurement_plan_lifecycle_service import (
    ContactMeasurementPlanLifecycleError,
    ContactMeasurementPlanLifecycleService,
)
from backend.application.contact_measurement_plan_projection_service import (
    ContactMeasurementPlanProjectionService,
)
from backend.api.dependencies import get_session, get_settings
from backend.api.main import app
from backend.domain import (
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixStepQuantity,
    ConfirmedMatrixVersion,
    MatrixStepContactFamily,
    MatrixStepContactPlan,
    Project,
    ProjectStatus,
)
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.models_contact_measurement_plan_authority import (
    MeasurementPlanFamilySnapshotModel,
    MeasurementPlanRootModel,
    MeasurementPlanTargetSnapshotModel,
)
from backend.infrastructure.storage.repositories import (
    ConfirmedMatrixAuthorityRepository,
    ContactMeasurementPlanAuthorityRepository,
    ProjectRepository,
)
from backend.shared.config import Settings


def test_bootstrap_persists_confirmed_legacy_contact_plan_idempotently(
    tmp_path: Path,
) -> None:
    session_factory = _session_factory(tmp_path)
    snapshot = _seed_snapshot(session_factory, project_id="P1")

    with session_factory() as session:
        repository = ContactMeasurementPlanAuthorityRepository(session)
        bootstrap = _bootstrap(repository)

        root_id = bootstrap.bootstrap(snapshot, actor="operator")
        same_root_id = bootstrap.bootstrap(snapshot, actor="operator")

        assert root_id == same_root_id
        root = repository.get_root("P1")
        assert root is not None
        assert root.active_confirmed_revision_id is not None
        targets = repository.targets(root.active_confirmed_revision_id)
        assert len(targets) == 1
        assert targets[0].stable_target_key.startswith("cmp-target:v1|")
        assert targets[0].readings_per_sample == 4
        families = repository.families(targets[0].measurement_plan_target_snapshot_id)
        assert [(family.family_id, family.count_per_sample) for family in families] == [
            ("hp", 2),
            ("signal", 2),
        ]
        session.commit()


def test_bootstrap_recovers_matching_partial_rows_and_blocks_divergent_payload(
    tmp_path: Path,
) -> None:
    session_factory = _session_factory(tmp_path)
    snapshot = _seed_snapshot(session_factory, project_id="P1")

    with session_factory() as session:
        repository = ContactMeasurementPlanAuthorityRepository(session)
        bootstrap = _bootstrap(repository)
        root_id = bootstrap.bootstrap(snapshot)
        root = repository.get_root("P1")
        assert root is not None
        target = repository.targets(root.active_confirmed_revision_id or "")[0]
        for family in repository.families(target.measurement_plan_target_snapshot_id):
            session.delete(family)
        session.delete(target)
        session.commit()

        assert bootstrap.bootstrap(snapshot) == root_id
        recovered_root = repository.get_root("P1")
        assert recovered_root is not None
        recovered_targets = repository.targets(
            recovered_root.active_confirmed_revision_id or ""
        )
        assert len(recovered_targets) == 1
        assert len(
            repository.families(
                recovered_targets[0].measurement_plan_target_snapshot_id
            )
        ) == 2

        with pytest.raises(ContactMeasurementPlanBootstrapError, match="authority_corrupt"):
            bootstrap.bootstrap(_snapshot(project_id="P1", high_power_count="3"))


def test_bootstrap_does_not_fallback_to_legacy_when_root_already_exists(
    tmp_path: Path,
) -> None:
    session_factory = _session_factory(tmp_path)
    snapshot = _seed_snapshot(session_factory, project_id="P1")

    with session_factory() as session:
        repository = ContactMeasurementPlanAuthorityRepository(session)
        session.add(
            MeasurementPlanRootModel(
                measurement_plan_root_id="root-existing",
                project_id="P1",
                active_confirmed_revision_id=None,
                editable_revision_id=None,
                created_at="2026-07-12T10:00:00Z",
                updated_at="2026-07-12T10:00:00Z",
            )
        )
        session.commit()

        with pytest.raises(ContactMeasurementPlanBootstrapError, match="authority_corrupt"):
            _bootstrap(repository).bootstrap(snapshot)

        assert repository.get_root("P1").measurement_plan_root_id == "root-existing"
        assert repository.get_active_revision("P1") is None


def test_lifecycle_stale_confirm_keeps_active_revision_then_supersedes_on_success(
    tmp_path: Path,
) -> None:
    session_factory = _session_factory(tmp_path)
    snapshot = _seed_snapshot(session_factory, project_id="P1")

    with session_factory() as session:
        repository = ContactMeasurementPlanAuthorityRepository(session)
        ids = _ids()
        bootstrap = _bootstrap(repository, id_factory=ids)
        confirmed_store = ConfirmedMatrixAuthorityRepository(session)
        lifecycle = ContactMeasurementPlanLifecycleService(
            repository=repository,
            confirmed_store=confirmed_store,
            bootstrap_service=bootstrap,
            clock=_clock(),
            id_factory=ids,
        )
        draft_id = lifecycle.open_draft("P1", actor="operator")
        active_before = repository.get_active_revision("P1")
        assert active_before is not None

        with pytest.raises(ContactMeasurementPlanLifecycleError, match="stale"):
            lifecycle.confirm("P1", draft_id, "wrong-fingerprint", "operator")

        assert repository.get_active_revision("P1").measurement_plan_revision_id == (
            active_before.measurement_plan_revision_id
        )
        assert repository.get_revision(draft_id).state == "draft"

        lifecycle.confirm(
            "P1",
            draft_id,
            repository.get_revision(draft_id).revision_fingerprint,
            "operator",
        )

        assert repository.get_revision(active_before.measurement_plan_revision_id).state == (
            "superseded"
        )
        assert repository.get_active_revision("P1").measurement_plan_revision_id == draft_id
        session.commit()


def test_superseded_matrix_persists_review_impact_and_blocks_confirmation(
    tmp_path: Path,
) -> None:
    session_factory = _session_factory(tmp_path)
    _seed_snapshot(session_factory, project_id="P1")

    with session_factory() as session:
        repository = ContactMeasurementPlanAuthorityRepository(session)
        confirmed_store = ConfirmedMatrixAuthorityRepository(session)
        lifecycle = ContactMeasurementPlanLifecycleService(
            repository=repository,
            confirmed_store=confirmed_store,
            bootstrap_service=_bootstrap(repository),
            clock=_clock(),
        )
        draft_id = lifecycle.open_draft("P1", actor="operator")
        confirmed_store.supersede_active_and_create_snapshot(
            previous_active_confirmed_matrix_id="cmv-1",
            snapshot=_superseding_snapshot(),
        )
        lifecycle.refresh_impacts("P1", draft_id, "cmv-2:2", "operator")

        impacts = repository.unresolved_review_impacts(draft_id)
        assert len(impacts) == 1
        assert impacts[0].category == "structural_review_required"
        assert impacts[0].stable_target_key is None
        assert impacts[0].impact_subject_key == (
            "cmp-candidate:v1|matrix:cmv-2|group:cmg-3|row:cmr-2|step:1|suffix:"
        )
        candidate_subject = impacts[0].impact_subject_key
        old_target_key = repository.targets(draft_id)[0].stable_target_key
        fingerprint_before_rebind = repository.get_revision(draft_id).revision_fingerprint
        lifecycle.rebind_target(
            "P1",
            draft_id,
            old_target_key,
            candidate_subject,
            repository.get_revision(draft_id).revision_fingerprint,
            "operator",
        )
        fingerprint_after_rebind = repository.get_revision(draft_id).revision_fingerprint
        assert fingerprint_after_rebind != fingerprint_before_rebind
        with pytest.raises(ContactMeasurementPlanLifecycleError, match="stale"):
            lifecycle.confirm("P1", draft_id, fingerprint_before_rebind, "operator")
        lifecycle.rebind_target(
            "P1",
            draft_id,
            old_target_key,
            candidate_subject,
            fingerprint_after_rebind,
            "operator",
        )
        assert repository.unresolved_review_impacts(draft_id) == []
        lifecycle.confirm(
            "P1",
            draft_id,
            repository.get_revision(draft_id).revision_fingerprint,
            "operator",
        )

        projection = ContactMeasurementPlanProjectionService(
            repository,
            enabled=True,
            confirmed_store=confirmed_store,
        ).get_effective("P1")
        assert projection.status == "needs_review"
        assert len(projection.targets) == 1
        session.commit()


def test_typed_api_exposes_workspace_and_blocks_writes_when_feature_disabled(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _api_client(tmp_path, enabled=True)
    _seed_snapshot(session_factory, project_id="P1")
    try:
        summary = client.get("/api/projects/P1/contact-measurement-plan/summary")
        assert summary.status_code == 200
        assert summary.json()["status"] == "not_started"

        opened = client.post(
            "/api/projects/P1/contact-measurement-plan/revisions",
            json={"actor": "operator"},
        )
        assert opened.status_code == 200
        revision_id = opened.json()["revision_id"]

        workspace = client.get(
            "/api/projects/P1/contact-measurement-plan/workspace"
        )
        assert workspace.status_code == 200
        payload = workspace.json()
        assert payload["active_confirmed_revision_id"] is not None
        assert payload["editable_revision_id"] == revision_id
        assert payload["editable_revision_state"] == "draft"
        assert payload["targets"][0]["families"][0]["family_id"] == "hp"

        saved = client.put(
            f"/api/projects/P1/contact-measurement-plan/revisions/{revision_id}",
            json={
                "actor": "operator",
                "expected_revision_fingerprint": payload[
                    "editable_revision_fingerprint"
                ],
            },
        )
        assert saved.status_code == 200

        refreshed = client.post(
            (
                f"/api/projects/P1/contact-measurement-plan/revisions/{revision_id}"
                "/impacts/refresh"
            ),
            json={
                "actor": "operator",
                "expected_matrix_binding_fingerprint": "cmv-1:1",
            },
        )
        assert refreshed.status_code == 200
        assert refreshed.json()["status"] == "unchanged"

        accepted = client.post(
            (
                f"/api/projects/P1/contact-measurement-plan/revisions/{revision_id}"
                "/suggestions/accept-compatible"
            ),
            json={
                "actor": "operator",
                "expected_revision_fingerprint": payload[
                    "editable_revision_fingerprint"
                ],
            },
        )
        assert accepted.status_code == 200

        updated = client.patch(
            f"/api/projects/P1/contact-measurement-plan/revisions/{revision_id}/targets",
            json={
                "actor": "operator",
                "expected_revision_fingerprint": payload[
                    "editable_revision_fingerprint"
                ],
                "stable_target_key": payload["targets"][0]["stable_target_key"],
                "included": False,
                "exclusion_reason": "Not applicable to this project.",
                "families": [
                    {
                        "family_id": "hp",
                        "label": "High power",
                        "count_per_sample": 3,
                        "record_label": "High power pin",
                        "record_prefix": "HP",
                        "included": True,
                        "is_custom": False,
                    },
                    {
                        "family_id": "custom-sense",
                        "label": "Sense",
                        "count_per_sample": 1,
                        "record_label": "Sense pin",
                        "record_prefix": "SENSE",
                        "included": True,
                        "is_custom": True,
                    },
                ],
            },
        )
        assert updated.status_code == 200

        workspace_after_patch = client.get(
            "/api/projects/P1/contact-measurement-plan/workspace"
        ).json()
        assert workspace_after_patch["targets"][0]["readings_per_sample"] == 4
        assert [
            family["family_id"]
            for family in workspace_after_patch["targets"][0]["families"]
        ] == ["hp", "custom-sense"]

        confirmed = client.post(
            f"/api/projects/P1/contact-measurement-plan/revisions/{revision_id}/confirm",
            json={
                "actor": "operator",
                "expected_revision_fingerprint": workspace_after_patch[
                    "editable_revision_fingerprint"
                ],
            },
        )
        assert confirmed.status_code == 200
        assert confirmed.json()["status"] == "confirmed"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()

    disabled_client, disabled_engine, disabled_factory = _api_client(
        tmp_path / "disabled",
        enabled=False,
    )
    _seed_snapshot(disabled_factory, project_id="P2")
    try:
        response = disabled_client.post(
            "/api/projects/P2/contact-measurement-plan/revisions",
            json={"actor": "operator"},
        )
        assert response.status_code == 503
        assert response.json()["detail"]["code"] == (
            "contact_measurement_plan_authority_disabled"
        )
    finally:
        app.dependency_overrides.clear()
        disabled_engine.dispose()


def test_typed_api_registers_the_authority_revision_command_surface() -> None:
    paths = app.openapi()["paths"]
    base = "/api/projects/{project_id}/contact-measurement-plan"

    assert {
        f"{base}/summary",
        f"{base}/workspace",
        f"{base}/effective-projection",
        f"{base}/revisions",
        f"{base}/revisions/{{revision_id}}",
        f"{base}/revisions/{{revision_id}}/impacts/refresh",
        f"{base}/revisions/{{revision_id}}/suggestions/accept-compatible",
        f"{base}/revisions/{{revision_id}}/targets/rebind",
        f"{base}/revisions/{{revision_id}}/targets",
        f"{base}/revisions/{{revision_id}}/confirm",
    }.issubset(paths)


def _session_factory(tmp_path: Path):
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "authority.sqlite3",
    )
    engine = create_database_engine(settings)
    init_db(engine)
    return create_session_factory(engine)


def _api_client(tmp_path: Path, *, enabled: bool):
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "authority-api.sqlite3",
        contact_measurement_plan_authority_enabled=enabled,
    )
    engine = create_database_engine(settings)
    init_db(engine)
    session_factory = create_session_factory(engine)

    def override_session() -> Iterator[Session]:
        with session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app), engine, session_factory


def _seed_snapshot(session_factory, *, project_id: str) -> ConfirmedMatrixSnapshot:
    snapshot = _snapshot(project_id=project_id)
    with session_factory() as session:
        ProjectRepository(session).create(
            Project(
                project_id=project_id,
                project_no=f"DL-2026-07-{project_id}",
                product_name="Connector",
                requestor="Operator",
                status=ProjectStatus.LTR_REGISTERED,
                created_on=date(2026, 7, 12),
            )
        )
        ConfirmedMatrixAuthorityRepository(session).create_snapshot(snapshot)
        session.commit()
    return snapshot


def _snapshot(*, project_id: str, high_power_count: str = "2") -> ConfirmedMatrixSnapshot:
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="cmv-1",
            project_id=project_id,
            project_matrix_draft_id="pmd-1",
            source_import_id="smi-1",
            source_snapshot_id="sms-1",
            confirmed_revision=1,
            is_active_authority=True,
            status=ConfirmedMatrixStatus.CONFIRMED,
            confirmed_by="operator",
            confirmed_at="2026-07-12T10:00:00Z",
        ),
        groups=(
            ConfirmedMatrixGroup(
                confirmed_group_id="cmg-1",
                confirmed_matrix_id="cmv-1",
                draft_group_id="pmdg-1",
                source_group_snapshot_id="smg-1",
                group_order=1,
                group_key="group-1",
                group_label="Group 1",
                sample_quantity_expression="2",
            ),
        ),
        rows=(
            ConfirmedMatrixRow(
                confirmed_row_id="cmr-1",
                confirmed_matrix_id="cmv-1",
                draft_row_id="pmdr-1",
                source_row_snapshot_id="smr-1",
                row_order=1,
                test_item="Low level contact resistance",
            ),
        ),
        step_quantities=(
            ConfirmedMatrixStepQuantity(
                confirmed_step_quantity_id="cmsq-1",
                confirmed_matrix_id="cmv-1",
                confirmed_group_id="cmg-1",
                confirmed_row_id="cmr-1",
                draft_group_id="pmdg-1",
                draft_row_id="pmdr-1",
                step_sequence=1,
                step_suffix_note=None,
                raw_token="1",
                test_points_per_sample=None,
                readings_per_point=None,
                contact_points_per_sample=None,
                source="matrix_contact_plan",
                review_required=False,
                review_reason=None,
                confirmed_at="2026-07-12T10:00:00Z",
                contact_plan=MatrixStepContactPlan(
                    contact_kind="llcr",
                    coverage_status="included",
                    included=True,
                    exclusion_reason=None,
                    is_override=False,
                    readings_per_sample="4",
                    families=(
                        MatrixStepContactFamily(
                            family_id="hp",
                            family_label="High power",
                            count_per_sample=high_power_count,
                            record_label="High power pin",
                            record_prefix="HP",
                            included=True,
                            is_custom=False,
                        ),
                        MatrixStepContactFamily(
                            family_id="signal",
                            family_label="Signal",
                            count_per_sample="2",
                            record_label="Signal pin",
                            record_prefix="SIG",
                            included=True,
                            is_custom=False,
                        ),
                    ),
                ),
            ),
        ),
    )


def _superseding_snapshot() -> ConfirmedMatrixSnapshot:
    base = _snapshot(project_id="P1")
    version = replace(
        base.version,
        confirmed_matrix_id="cmv-2",
        project_matrix_draft_id="pmd-2",
        source_import_id="smi-2",
        source_snapshot_id="sms-2",
        confirmed_revision=2,
        confirmed_at="2026-07-12T11:00:00Z",
    )
    first_group = replace(
        base.groups[0],
        confirmed_group_id="cmg-2",
        confirmed_matrix_id="cmv-2",
        draft_group_id="pmdg-2",
        sample_quantity_expression="3",
    )
    added_group = replace(
        first_group,
        confirmed_group_id="cmg-3",
        draft_group_id="pmdg-3",
        source_group_snapshot_id="smg-2",
        group_order=2,
        group_key="group-2",
    )
    row = replace(
        base.rows[0],
        confirmed_row_id="cmr-2",
        confirmed_matrix_id="cmv-2",
        draft_row_id="pmdr-2",
    )
    quantities = tuple(
        replace(
            base.step_quantities[0],
            confirmed_step_quantity_id=f"cmsq-{group.confirmed_group_id}",
            confirmed_matrix_id="cmv-2",
            confirmed_group_id=group.confirmed_group_id,
            confirmed_row_id=row.confirmed_row_id,
            draft_group_id=group.draft_group_id,
            draft_row_id=row.draft_row_id,
            confirmed_at="2026-07-12T11:00:00Z",
        )
        for group in (first_group, added_group)
    )
    return ConfirmedMatrixSnapshot(
        version=version,
        groups=(first_group, added_group),
        rows=(row,),
        step_quantities=quantities,
    )


def _bootstrap(
    repository: ContactMeasurementPlanAuthorityRepository,
    *,
    id_factory=None,
):
    return ContactMeasurementPlanBootstrapService(
        repository=repository,
        clock=_clock(),
        id_factory=id_factory or _ids(),
    )


def _clock() -> Iterator[str]:
    return iter(
        [
            "2026-07-12T10:00:01Z",
            "2026-07-12T10:00:02Z",
            "2026-07-12T10:00:03Z",
            "2026-07-12T10:00:04Z",
            "2026-07-12T10:00:05Z",
            "2026-07-12T10:00:06Z",
        ]
    ).__next__


def _ids() -> Iterator[str]:
    return iter(
        [
            "root",
            "revision",
            "target",
            "family-one",
            "family-two",
            "draft",
            "next-target",
            "next-family-one",
            "next-family-two",
        ]
    ).__next__
